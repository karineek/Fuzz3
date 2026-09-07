#include "driver.hpp"

#include <cstdlib>
#include <iostream>
#include <iterator>
#include <map>
#include <string>

namespace {

using fuzz3::worker::InputError;
using fuzz3::worker::Request;
using fuzz3::worker::json;

int fail(const std::string& category, const std::string& message, int code) {
    std::cerr << json{{"error", category}, {"message", message}}.dump() << '\n';
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

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--describe") {
            std::cout << fuzz3::worker::driver_manifest().dump() << '\n';
            return 0;
        }

        const std::string input(std::istreambuf_iterator<char>(std::cin), {});
        if (input.empty()) {
            throw InputError("request is empty");
        }
        json value;
        try {
            value = json::parse(input);
        } catch (const json::parse_error& error) {
            throw InputError(std::string("invalid JSON: ") + error.what());
        }
        std::cout << execute(std::move(value)).dump() << '\n';
        return 0;
    } catch (const InputError& error) {
        return fail("invalid_input", error.what(), 2);
    } catch (const std::exception& error) {
        return fail("runtime_error", error.what(), 1);
    } catch (...) {
        return fail("runtime_error", "unknown native failure", 1);
    }
}
