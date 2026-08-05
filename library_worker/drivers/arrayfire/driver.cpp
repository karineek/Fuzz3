#include "driver.hpp"

#include <algorithm>
#include <cstddef>
#include <limits>
#include <string>
#include <vector>

#include <arrayfire.h>

namespace fuzz3::worker {
namespace {

dim_t checked_dim(std::size_t value, const std::string& name) {
    if (value > static_cast<std::size_t>(std::numeric_limits<dim_t>::max())) {
        throw InputError(name + " exceeds ArrayFire dim_t");
    }
    return static_cast<dim_t>(value);
}

af::array vector_array(const Request& request, const std::string& name,
                       DenseInput& input) {
    input = request.dense(name, "vector", 1);
    const std::vector<float> values = request.values<float>(input, "f32", name);
    if (values.empty()) {
        throw InputError(name + " cannot be empty");
    }
    return af::array(checked_dim(values.size(), name), values.data());
}

std::vector<float> row_to_column(const std::vector<float>& values,
                                 std::size_t rows, std::size_t columns) {
    std::vector<float> output(values.size());
    for (std::size_t row = 0; row < rows; ++row) {
        for (std::size_t column = 0; column < columns; ++column) {
            output[column * rows + row] = values[row * columns + column];
        }
    }
    return output;
}

std::vector<float> column_to_row(const std::vector<float>& values,
                                 std::size_t rows, std::size_t columns) {
    std::vector<float> output(values.size());
    for (std::size_t row = 0; row < rows; ++row) {
        for (std::size_t column = 0; column < columns; ++column) {
            output[row * columns + column] = values[column * rows + row];
        }
    }
    return output;
}

af::array matrix_array(const Request& request, const std::string& name,
                       DenseInput& input) {
    input = request.dense(name, "matrix", 2);
    const std::vector<float> row_major = request.values<float>(input, "f32", name);
    const std::vector<float> column_major =
        row_to_column(row_major, input.shape[0], input.shape[1]);
    if (input.shape[0] == 0 || input.shape[1] == 0) {
        throw InputError(name + " dimensions cannot be zero");
    }
    return af::array(checked_dim(input.shape[0], name + ".rows"),
                     checked_dim(input.shape[1], name + ".columns"),
                     column_major.data());
}

std::vector<float> host_values(const af::array& value) {
    af::array evaluated = value;
    evaluated.eval();
    std::vector<float> result(static_cast<std::size_t>(evaluated.elements()));
    evaluated.host(result.data());
    return result;
}

json matrix_output(const af::array& value) {
    const std::size_t rows = static_cast<std::size_t>(value.dims(0));
    const std::size_t columns = static_cast<std::size_t>(value.dims(1));
    return dense_result("matrix", "f32", {rows, columns},
                        column_to_row(host_values(value), rows, columns));
}

void select_backend() {
#ifdef FUZZ3_GPU
    af::setBackend(AF_BACKEND_CUDA);
#else
    af::setBackend(AF_BACKEND_CPU);
#endif
    af::setDevice(0);
}

}  // namespace

std::string driver_name() {
    return "arrayfire";
}

json driver_manifest() {
    return {
        {"schema_version", 1},
        {"library", "arrayfire"},
#ifdef FUZZ3_GPU
        {"backend", "gpu"},
#else
        {"backend", "cpu"},
#endif
        {"functions",
         {
             {"sort", {{"values", "vector<f32>"}}},
             {"reduce_sum", {{"values", "vector<f32>"}}},
             {"matmul", {{"a", "matrix<f32>"}, {"b", "matrix<f32>"}}},
             {"transpose", {{"matrix", "matrix<f32>"}}},
             {"fft", {{"values", "vector<f32>"}}},
             {"convolve1", {{"signal", "vector<f32>"}, {"kernel", "vector<f32>"}}},
         }},
    };
}

json run(const Request& request) {
    select_backend();
    const std::string function = request.function();

    if (function == "sort" || function == "reduce_sum" || function == "fft") {
        DenseInput input;
        const af::array values = vector_array(request, "values", input);
        if (function == "sort") {
            return dense_result("vector", "f32", input.shape, host_values(af::sort(values)));
        }
        if (function == "reduce_sum") {
            return scalar_result("f64", af::sum<double>(values));
        }
        const af::array transformed = af::fft(values);
        return {{"real", dense_result("vector", "f32", input.shape,
                                      host_values(af::real(transformed)))},
                {"imag", dense_result("vector", "f32", input.shape,
                                      host_values(af::imag(transformed)))}};
    }

    if (function == "matmul") {
        DenseInput a_input;
        DenseInput b_input;
        const af::array a = matrix_array(request, "a", a_input);
        const af::array b = matrix_array(request, "b", b_input);
        if (a_input.shape[1] != b_input.shape[0]) {
            throw InputError("a columns must match b rows");
        }
        return matrix_output(af::matmul(a, b));
    }

    if (function == "transpose") {
        DenseInput input;
        return matrix_output(af::transpose(matrix_array(request, "matrix", input), false));
    }

    if (function == "convolve1") {
        DenseInput signal_input;
        DenseInput kernel_input;
        const af::array signal = vector_array(request, "signal", signal_input);
        const af::array kernel = vector_array(request, "kernel", kernel_input);
        const af::array output = af::convolve1(signal, kernel, AF_CONV_EXPAND);
        const std::vector<float> result = host_values(output);
        return dense_result("vector", "f32", {result.size()}, result);
    }

    throw InputError("unknown arrayfire function: " + function);
}

}  // namespace fuzz3::worker
