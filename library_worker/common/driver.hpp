#pragma once

#include <cstddef>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>

#include <nlohmann/json.hpp>

namespace fuzz3::worker {

using json = nlohmann::json;

class InputError : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

struct DenseInput {
    std::string type;
    std::string dtype;
    std::vector<std::size_t> shape;
    json data;
};

class Request {
public:
    explicit Request(json value) : value_(std::move(value)) {
        if (!value_.is_object()) {
            throw InputError("request must be an object");
        }
        if (!value_.contains("function") || !value_["function"].is_string()) {
            throw InputError("function must be a string");
        }
        if (!value_.contains("inputs") || !value_["inputs"].is_object()) {
            throw InputError("inputs must be an object");
        }
    }

    const std::string function() const {
        return value_["function"].get<std::string>();
    }

    bool has(const std::string& name) const {
        return value_["inputs"].contains(name);
    }

    DenseInput dense(const std::string& name, const std::string& expected_type,
                     std::size_t rank) const {
        const json& input = named(name);
        if (!input.is_object()) {
            throw InputError(name + " must be an object");
        }
        const std::string type = required_string(input, "type", name);
        const std::string dtype = required_string(input, "dtype", name);
        if (type != expected_type) {
            throw InputError(name + ".type must be " + expected_type);
        }
        if (!input.contains("shape") || !input["shape"].is_array() ||
            input["shape"].size() != rank) {
            throw InputError(name + ".shape must have rank " + std::to_string(rank));
        }
        if (!input.contains("data") || !input["data"].is_array()) {
            throw InputError(name + ".data must be an array");
        }

        std::vector<std::size_t> shape;
        std::size_t count = 1;
        for (const json& dimension : input["shape"]) {
            if (!dimension.is_number_unsigned() && !dimension.is_number_integer()) {
                throw InputError(name + ".shape entries must be integers");
            }
            const auto signed_dimension = dimension.get<std::int64_t>();
            if (signed_dimension < 0) {
                throw InputError(name + ".shape entries cannot be negative");
            }
            const auto size = static_cast<std::size_t>(signed_dimension);
            if (size != 0 && count > max_elements / size) {
                throw InputError(name + " is too large");
            }
            count *= size;
            shape.push_back(size);
        }
        if (input["data"].size() != count) {
            throw InputError(name + ".data length does not match shape");
        }
        return {type, dtype, std::move(shape), input["data"]};
    }

    template <typename T>
    std::vector<T> values(const DenseInput& input, const std::string& dtype,
                          const std::string& name) const {
        if (input.dtype != dtype) {
            throw InputError(name + ".dtype must be " + dtype);
        }
        try {
            return input.data.get<std::vector<T>>();
        } catch (const json::exception&) {
            throw InputError(name + ".data contains a value outside " + dtype);
        }
    }

    template <typename T>
    T scalar(const std::string& name, const std::string& dtype) const {
        const json& input = named(name);
        if (!input.is_object() || required_string(input, "type", name) != "scalar") {
            throw InputError(name + ".type must be scalar");
        }
        if (required_string(input, "dtype", name) != dtype) {
            throw InputError(name + ".dtype must be " + dtype);
        }
        if (!input.contains("value")) {
            throw InputError(name + ".value is required");
        }
        try {
            return input["value"].get<T>();
        } catch (const json::exception&) {
            throw InputError(name + ".value is outside " + dtype);
        }
    }

private:
    static constexpr std::size_t max_elements = 1U << 20;
    json value_;

    const json& named(const std::string& name) const {
        if (!value_["inputs"].contains(name)) {
            throw InputError("missing input: " + name);
        }
        return value_["inputs"][name];
    }

    static std::string required_string(const json& value, const std::string& key,
                                       const std::string& name) {
        if (!value.contains(key) || !value[key].is_string()) {
            throw InputError(name + "." + key + " must be a string");
        }
        return value[key].get<std::string>();
    }
};

template <typename T>
json dense_result(const std::string& type, const std::string& dtype,
                  const std::vector<std::size_t>& shape, const std::vector<T>& data) {
    return {{"type", type}, {"dtype", dtype}, {"shape", shape}, {"data", data}};
}

template <typename T>
json scalar_result(const std::string& dtype, T value) {
    return {{"type", "scalar"}, {"dtype", dtype}, {"value", value}};
}

std::string driver_name();
json driver_manifest();
json run(const Request& request);

}  // namespace fuzz3::worker
