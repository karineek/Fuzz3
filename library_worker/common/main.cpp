#include "driver.hpp"

#include <csignal>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <iterator>
#include <map>
#include <sstream>
#include <string>

#include <sys/socket.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <unistd.h>

// Execution mode:
//   (default)          exec:       one native process per execution (legacy,
//                                  forkserver.py spawns this binary each time)
//   -DFUZZ3_FORKSERVER forkserver: `--serve` keeps one parent alive and forks a
//                                  fresh child per request
//   -DFUZZ3_PERSISTENT persistent: `--serve` runs every request in one process
//                                  for the whole campaign (state/noise carries
//                                  over); forkserver.py restarts it on crash
enum class ExecMode { exec, forkserver, persistent };
#if defined(FUZZ3_PERSISTENT) && defined(FUZZ3_FORKSERVER)
#error "Define at most one of FUZZ3_PERSISTENT and FUZZ3_FORKSERVER"
#elif defined(FUZZ3_PERSISTENT)
constexpr ExecMode kExecMode = ExecMode::persistent;
#elif defined(FUZZ3_FORKSERVER)
constexpr ExecMode kExecMode = ExecMode::forkserver;
#else
constexpr ExecMode kExecMode = ExecMode::exec;
#endif

namespace {

using fuzz3::worker::InputError;
using fuzz3::worker::Request;
using fuzz3::worker::json;

int fail(std::ostream& err, const std::string& category, const std::string& message,
         int code) {
    err << json{{"error", category}, {"message", message}}.dump() << '\n';
    return code;
}

std::size_t max_chain_depth() {
    const char* raw = std::getenv("FUZZ3_MAX_CHAIN_DEPTH");
    if (raw == nullptr || *raw == '\0') return 4;
    char* end = nullptr;
    const unsigned long value = std::strtoul(raw, &end, 10);
    if (*end != '\0' || value < 1 || value > 64) {
        throw InputError("FUZZ3_MAX_CHAIN_DEPTH must be between 1 and 64");
    }
    return static_cast<std::size_t>(value);
}

json resolve_reference(const json& reference,
                       const std::map<std::string, json>& results) {
    if (!reference["ref"].is_string() ||
        (reference.size() != 1 && reference.size() != 2) ||
        (reference.size() == 2 && !reference.contains("path"))) {
        throw InputError("result reference must contain ref and optional path only");
    }

    const std::string id = reference["ref"].get<std::string>();
    const auto found = results.find(id);
    if (found == results.end()) {
        throw InputError("unknown or forward result reference: " + id);
    }

    json result = found->second;
    if (!reference.contains("path")) return result;
    if (!reference["path"].is_array()) {
        throw InputError("reference path must be an array");
    }

    for (const json& part : reference["path"]) {
        if (part.is_string() && result.is_object() && result.contains(part)) {
            result = result[part.get<std::string>()];
        } else if (part.is_number_unsigned() && result.is_array() &&
                   part.get<std::size_t>() < result.size()) {
            result = result[part.get<std::size_t>()];
        } else {
            throw InputError("reference path does not exist");
        }
    }
    return result;
}

json resolve_value(const json& value, const std::map<std::string, json>& results) {
    if (value.is_object() && value.contains("ref")) {
        return resolve_reference(value, results);
    }
    if (value.is_object()) {
        json result = json::object();
        for (auto item = value.begin(); item != value.end(); ++item) {
            result[item.key()] = resolve_value(item.value(), results);
        }
        return result;
    }
    if (value.is_array()) {
        json result = json::array();
        for (const json& item : value) result.push_back(resolve_value(item, results));
        return result;
    }
    return value;
}

json execute_single(json value) {
    Request request(std::move(value));
    return {{"schema_version", 1},
            {"library", fuzz3::worker::driver_name()},
            {"function", request.function()},
            {"result", fuzz3::worker::run(request)}};
}

json execute_pipeline(const json& operations) {
    if (!operations.is_array() || operations.empty()) {
        throw InputError("operations must be a non-empty array");
    }
    if (operations.size() > max_chain_depth()) {
        throw InputError("operation chain exceeds FUZZ3_MAX_CHAIN_DEPTH");
    }

    std::map<std::string, json> results;
    json executed = json::array();
    for (std::size_t index = 0; index < operations.size(); ++index) {
        const json& source = operations[index];
        if (!source.is_object()) throw InputError("each operation must be an object");
        if (source.contains("id") && !source["id"].is_string()) {
            throw InputError("operation id must be a string");
        }

        const std::string id = source.value("id", "op" + std::to_string(index));
        if (id.empty() || results.count(id)) {
            throw InputError("operation ids must be unique and non-empty");
        }

        json operation = resolve_value(source, results);
        operation.erase("id");
        Request request(std::move(operation));
        json result = fuzz3::worker::run(request);
        results.emplace(id, result);
        executed.push_back(
            {{"id", id}, {"function", request.function()}, {"result", result}});
    }

    return {{"schema_version", 2},
            {"library", fuzz3::worker::driver_name()},
            {"operations", executed},
            {"result", executed.back()["result"]}};
}

json execute(json value) {
    if (value.contains("schema_version") && value["schema_version"] != 1 &&
        value["schema_version"] != 2) {
        throw InputError("schema_version must be 1 or 2");
    }
    if (value.contains("library") &&
        (!value["library"].is_string() ||
         value["library"].get<std::string>() != fuzz3::worker::driver_name())) {
        throw InputError("request library does not match the built driver");
    }
    if (value.contains("operations")) return execute_pipeline(value["operations"]);
    return execute_single(std::move(value));
}

// Runs one request. Returns the process exit code.
int handle_request(const std::string& input, std::ostream& out, std::ostream& err) {
    try {
        if (input.empty()) {
            throw InputError("request is empty");
        }
        json value;
        try {
            value = json::parse(input);
        } catch (const json::parse_error& error) {
            throw InputError(std::string("invalid JSON: ") + error.what());
        }
        out << execute(std::move(value)).dump() << '\n';
        return 0;
    } catch (const InputError& error) {
        return fail(err, "invalid_input", error.what(), 2);
    } catch (const std::exception& error) {
        return fail(err, "runtime_error", error.what(), 1);
    } catch (...) {
        return fail(err, "runtime_error", "unknown native failure", 1);
    }
}

void write_all(int fd, const std::string& data) {
    std::size_t written = 0;
    while (written < data.size()) {
        const ssize_t n = ::write(fd, data.data() + written, data.size() - written);
        if (n <= 0) return;
        written += static_cast<std::size_t>(n);
    }
}

void reply(int fd, int code, const std::string& out, const std::string& err) {
    write_all(fd, json{{"return_code", code}, {"stdout", out}, {"stderr", err}}.dump() +
                      "\n");
}

void serve_one(int fd, const std::string& line) {
    std::ostringstream out, err;
    const int code = handle_request(line, out, err);
    reply(fd, code, out.str(), err.str());
}

// One request per connection: read a line, write one JSON envelope line, close.
int serve() {
    std::signal(SIGPIPE, SIG_IGN);
    const char* env_path = std::getenv("FUZZ3_SOCKET");
    const std::string path = env_path && *env_path ? env_path : "/tmp/fuzz3-native.sock";

    sockaddr_un address{};
    if (path.size() >= sizeof(address.sun_path)) {
        std::cerr << "fuzz3 serve: FUZZ3_SOCKET path is too long: " << path << '\n';
        return 1;
    }
    const int server = ::socket(AF_UNIX, SOCK_STREAM, 0);
    address.sun_family = AF_UNIX;
    std::strncpy(address.sun_path, path.c_str(), sizeof(address.sun_path) - 1);
    ::unlink(path.c_str());
    if (server < 0 ||
        ::bind(server, reinterpret_cast<sockaddr*>(&address), sizeof(address)) != 0 ||
        ::listen(server, 16) != 0) {
        std::perror("fuzz3 serve");
        return 1;
    }

    for (;;) {
        const int connection = ::accept(server, nullptr, nullptr);
        if (connection < 0) continue;
        std::string line;
        char c;
        while (::read(connection, &c, 1) == 1 && c != '\n') line.push_back(c);
        if (line.empty()) {  // readiness probe from forkserver.py
            ::close(connection);
            continue;
        }

        if constexpr (kExecMode == ExecMode::persistent) {
            serve_one(connection, line);
        } else {
            // Never touch CUDA in this parent: a CUDA context does not survive fork.
            const pid_t child = ::fork();
            if (child == 0) {
                ::close(server);
                serve_one(connection, line);
                ::_exit(0);
            }
            int status = 0;
            if (child < 0 || ::waitpid(child, &status, 0) < 0) {
                reply(connection, 1, "", "fork server: fork/wait failed");
            } else if (WIFSIGNALED(status)) {
                write_all(connection, "\n");
                reply(connection, -WTERMSIG(status), "",
                      "child killed by signal " + std::to_string(WTERMSIG(status)));
            } else if (WEXITSTATUS(status) != 0) {
                write_all(connection, "\n");
                reply(connection, WEXITSTATUS(status), "", "child exited abnormally");
            }
        }
        ::close(connection);
    }
}

}  // namespace

int main(int argc, char** argv) {
    if (argc == 2 && std::string(argv[1]) == "--describe") {
        try {
            std::cout << fuzz3::worker::driver_manifest().dump() << '\n';
            return 0;
        } catch (const std::exception& error) {
            return fail(std::cerr, "runtime_error", error.what(), 1);
        }
    }
    if (argc == 2 && std::string(argv[1]) == "--serve") {
        if constexpr (kExecMode == ExecMode::exec) {
            return fail(std::cerr, "usage",
                        "--serve needs -DFUZZ3_FORKSERVER or -DFUZZ3_PERSISTENT", 64);
        } else {
            return serve();
        }
    }
    const std::string input(std::istreambuf_iterator<char>(std::cin), {});
    return handle_request(input, std::cout, std::cerr);
}
