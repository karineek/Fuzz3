#include "driver.hpp"

#include <iostream>
#include <iterator>
#include <string>

namespace {

using fuzz3::worker::InputError;
using fuzz3::worker::Request;
using fuzz3::worker::json;

int fail(const std::string& category, const std::string& message, int code) {
    std::cerr << json{{"error", category}, {"message", message}}.dump() << '\n';
    return code;
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
        if (value.contains("schema_version") && value["schema_version"] != 1) {
            throw InputError("schema_version must be 1");
        }
        if (value.contains("library") &&
            (!value["library"].is_string() ||
             value["library"].get<std::string>() != fuzz3::worker::driver_name())) {
            throw InputError("request library does not match the built driver");
        }

        Request request(std::move(value));
        json response = {{"schema_version", 1},
                         {"library", fuzz3::worker::driver_name()},
                         {"function", request.function()},
                         {"result", fuzz3::worker::run(request)}};
        std::cout << response.dump() << '\n';
        return 0;
    } catch (const InputError& error) {
        return fail("invalid_input", error.what(), 2);
    } catch (const std::exception& error) {
        return fail("runtime_error", error.what(), 1);
    } catch (...) {
        return fail("runtime_error", "unknown native failure", 1);
    }
}
