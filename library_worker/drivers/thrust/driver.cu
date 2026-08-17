#include "driver.hpp"

#include <cstdint>
#include <string>
#include <vector>

#include <thrust/device_vector.h>
#include <thrust/functional.h>
#include <thrust/host_vector.h>
#include <thrust/reduce.h>
#include <thrust/scan.h>
#include <thrust/sort.h>
#include <thrust/transform.h>

namespace fuzz3::worker {
namespace {

#ifdef FUZZ3_GPU
template <typename T>
using BackendVector = thrust::device_vector<T>;
#else
template <typename T>
using BackendVector = thrust::host_vector<T>;
#endif

template <typename T>
std::vector<T> to_host(const BackendVector<T>& values) {
    thrust::host_vector<T> host(values);
    return {host.begin(), host.end()};
}

template <typename T>
json sort_values(const Request& request, const DenseInput& input,
                 const std::string& dtype) {
    BackendVector<T> values(request.values<T>(input, dtype, "values"));
    const bool descending = request.has("descending") &&
                            request.scalar<bool>("descending", "bool");
    if (descending) {
        thrust::sort(values.begin(), values.end(), thrust::greater<T>());
    } else {
        thrust::sort(values.begin(), values.end());
    }
    return dense_result("vector", dtype, input.shape, to_host(values));
}

#ifdef __CUDACC__
#define FUZZ3_HD __host__ __device__
#else
#define FUZZ3_HD
#endif

struct Axpby {
    float alpha;
    float beta;

    FUZZ3_HD float operator()(float x, float y) const {
        return alpha * x + beta * y;
    }
};

#undef FUZZ3_HD

}  // namespace

std::string driver_name() {
    return "thrust";
}

json driver_manifest() {
    return {
        {"schema_version", 1},
        {"library", "thrust"},
#ifdef FUZZ3_GPU
        {"backend", "gpu"},
#else
        {"backend", "cpu"},
#endif
        {"functions",
         {
             {"sort", {{"values", "vector<f32|f64|i32|i64>"},
                       {"descending", "scalar<bool>, optional"}}},
             {"reduce_sum", {{"values", "vector<f32>"}}},
             {"exclusive_scan", {{"values", "vector<i32>"}}},
             {"stable_sort_by_key", {{"keys", "vector<i32>"},
                                    {"values", "vector<f32>"}}},
             {"reduce_by_key", {{"keys", "vector<i32>"},
                               {"values", "vector<f32>"}}},
             {"transform_axpby", {{"x", "vector<f32>"}, {"y", "vector<f32>"},
                                 {"alpha", "scalar<f32>"},
                                 {"beta", "scalar<f32>"}}},
         }},
    };
}

json run(const Request& request) {
    const std::string function = request.function();
    if (function == "sort") {
        const DenseInput input = request.dense("values", "vector", 1);
        if (input.dtype == "f32") return sort_values<float>(request, input, "f32");
        if (input.dtype == "f64") return sort_values<double>(request, input, "f64");
        if (input.dtype == "i32") return sort_values<std::int32_t>(request, input, "i32");
        if (input.dtype == "i64") return sort_values<std::int64_t>(request, input, "i64");
        throw InputError("values.dtype is not supported by sort");
    }

    if (function == "reduce_sum") {
        const DenseInput input = request.dense("values", "vector", 1);
        BackendVector<float> values(request.values<float>(input, "f32", "values"));
        return scalar_result("f32", thrust::reduce(values.begin(), values.end(), 0.0f));
    }

    if (function == "exclusive_scan") {
        const DenseInput input = request.dense("values", "vector", 1);
        BackendVector<std::int32_t> values(
            request.values<std::int32_t>(input, "i32", "values"));
        BackendVector<std::int32_t> output(values.size());
        thrust::exclusive_scan(values.begin(), values.end(), output.begin());
        return dense_result("vector", "i32", input.shape, to_host(output));
    }

    if (function == "stable_sort_by_key" || function == "reduce_by_key") {
        const DenseInput key_input = request.dense("keys", "vector", 1);
        const DenseInput value_input = request.dense("values", "vector", 1);
        if (key_input.shape != value_input.shape) {
            throw InputError("keys and values must have the same shape");
        }
        BackendVector<std::int32_t> keys(
            request.values<std::int32_t>(key_input, "i32", "keys"));
        BackendVector<float> values(request.values<float>(value_input, "f32", "values"));

        if (function == "stable_sort_by_key") {
            thrust::stable_sort_by_key(keys.begin(), keys.end(), values.begin());
            return {{"keys", dense_result("vector", "i32", key_input.shape, to_host(keys))},
                    {"values", dense_result("vector", "f32", value_input.shape,
                                            to_host(values))}};
        }

        BackendVector<std::int32_t> output_keys(keys.size());
        BackendVector<float> output_values(values.size());
        const auto end = thrust::reduce_by_key(keys.begin(), keys.end(), values.begin(),
                                               output_keys.begin(), output_values.begin());
        const std::size_t size = static_cast<std::size_t>(end.first - output_keys.begin());
        output_keys.resize(size);
        output_values.resize(size);
        const std::vector<std::size_t> shape{size};
        return {{"keys", dense_result("vector", "i32", shape, to_host(output_keys))},
                {"values", dense_result("vector", "f32", shape, to_host(output_values))}};
    }

    if (function == "transform_axpby") {
        const DenseInput x_input = request.dense("x", "vector", 1);
        const DenseInput y_input = request.dense("y", "vector", 1);
        if (x_input.shape != y_input.shape) {
            throw InputError("x and y must have the same shape");
        }
        BackendVector<float> x(request.values<float>(x_input, "f32", "x"));
        BackendVector<float> y(request.values<float>(y_input, "f32", "y"));
        BackendVector<float> output(x.size());
        const Axpby operation{request.scalar<float>("alpha", "f32"),
                              request.scalar<float>("beta", "f32")};
        thrust::transform(x.begin(), x.end(), y.begin(), output.begin(), operation);
        return dense_result("vector", "f32", x_input.shape, to_host(output));
    }

    throw InputError("unknown thrust function: " + function);
}

}  // namespace fuzz3::worker
