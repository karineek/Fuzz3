#include "driver.hpp"

#include <cstddef>
#include <stdexcept>
#include <string>
#include <vector>

#ifdef FUZZ3_GPU
#include <cuda_runtime.h>
#include "cutlass/cutlass.h"
#include "cutlass/gemm/device/gemm.h"
#include "cutlass/layout/matrix.h"
#endif

namespace fuzz3::worker {
namespace {

struct Matrix {
    std::size_t rows;
    std::size_t columns;
    std::vector<float> values;
};

Matrix matrix_input(const Request& request, const std::string& name) {
    const DenseInput input = request.dense(name, "matrix", 2);
    if (input.shape[0] == 0 || input.shape[1] == 0) {
        throw InputError(name + " dimensions must be non-zero");
    }
    return {input.shape[0], input.shape[1],
            request.values<float>(input, "f32", name)};
}

void validate_gemm(const Matrix& a, const Matrix& b, const Matrix& c) {
    if (a.columns != b.rows) {
        throw InputError("a columns must match b rows");
    }
    if (c.rows != a.rows || c.columns != b.columns) {
        throw InputError("c shape must be [a rows, b columns]");
    }
}

#ifdef FUZZ3_GPU

void check_cuda(cudaError_t status, const std::string& operation) {
    if (status != cudaSuccess) {
        throw std::runtime_error(operation + ": " + cudaGetErrorString(status));
    }
}

class DeviceBuffer {
public:
    explicit DeviceBuffer(std::size_t count) {
        check_cuda(cudaMalloc(reinterpret_cast<void**>(&pointer_), count * sizeof(float)),
                   "cudaMalloc");
    }

    ~DeviceBuffer() {
        if (pointer_ != nullptr) cudaFree(pointer_);
    }

    DeviceBuffer(const DeviceBuffer&) = delete;
    DeviceBuffer& operator=(const DeviceBuffer&) = delete;

    float* get() const { return pointer_; }

private:
    float* pointer_ = nullptr;
};

std::vector<float> gemm(const Matrix& a, const Matrix& b, const Matrix& c,
                        float alpha, float beta) {
    validate_gemm(a, b, c);
    DeviceBuffer device_a(a.values.size());
    DeviceBuffer device_b(b.values.size());
    DeviceBuffer device_c(c.values.size());
    DeviceBuffer device_d(c.values.size());
    check_cuda(cudaMemcpy(device_a.get(), a.values.data(), a.values.size() * sizeof(float),
                          cudaMemcpyHostToDevice), "copy a");
    check_cuda(cudaMemcpy(device_b.get(), b.values.data(), b.values.size() * sizeof(float),
                          cudaMemcpyHostToDevice), "copy b");
    check_cuda(cudaMemcpy(device_c.get(), c.values.data(), c.values.size() * sizeof(float),
                          cudaMemcpyHostToDevice), "copy c");

    using RowMajor = cutlass::layout::RowMajor;
    using Gemm = cutlass::gemm::device::Gemm<float, RowMajor, float, RowMajor,
                                               float, RowMajor>;
    typename Gemm::Arguments arguments(
        {static_cast<int>(a.rows), static_cast<int>(b.columns),
         static_cast<int>(a.columns)},
        {device_a.get(), static_cast<int>(a.columns)},
        {device_b.get(), static_cast<int>(b.columns)},
        {device_c.get(), static_cast<int>(c.columns)},
        {device_d.get(), static_cast<int>(c.columns)}, {alpha, beta});
    Gemm operation;
    cutlass::Status status = operation.can_implement(arguments);
    if (status != cutlass::Status::kSuccess) {
        throw InputError(std::string("CUTLASS cannot implement input: ") +
                         cutlassGetStatusString(status));
    }
    status = operation(arguments);
    if (status != cutlass::Status::kSuccess) {
        throw std::runtime_error(std::string("CUTLASS GEMM failed: ") +
                                 cutlassGetStatusString(status));
    }
    check_cuda(cudaDeviceSynchronize(), "CUTLASS synchronize");

    std::vector<float> output(c.values.size());
    check_cuda(cudaMemcpy(output.data(), device_d.get(), output.size() * sizeof(float),
                          cudaMemcpyDeviceToHost), "copy output");
    return output;
}

#else

std::vector<float> gemm(const Matrix& a, const Matrix& b, const Matrix& c,
                        float alpha, float beta) {
    validate_gemm(a, b, c);
    std::vector<float> output(c.values.size());
    for (std::size_t row = 0; row < a.rows; ++row) {
        for (std::size_t column = 0; column < b.columns; ++column) {
            float sum = 0.0f;
            for (std::size_t inner = 0; inner < a.columns; ++inner) {
                sum += a.values[row * a.columns + inner] *
                       b.values[inner * b.columns + column];
            }
            const std::size_t index = row * b.columns + column;
            output[index] = alpha * sum + beta * c.values[index];
        }
    }
    return output;
}

#endif

Matrix zero_output(const Matrix& a, const Matrix& b) {
    if (a.columns != b.rows) {
        throw InputError("a columns must match b rows");
    }
    return {a.rows, b.columns, std::vector<float>(a.rows * b.columns, 0.0f)};
}

json matrix_result(const Matrix& matrix) {
    return dense_result("matrix", "f32", {matrix.rows, matrix.columns}, matrix.values);
}

}  // namespace

std::string driver_name() {
    return "cutlass";
}

json driver_manifest() {
    return {
        {"schema_version", 1},
        {"library", "cutlass"},
#ifdef FUZZ3_GPU
        {"backend", "gpu"},
#else
        {"backend", "cpu-reference"},
#endif
        {"functions",
         {
             {"gemm", {{"a", "matrix<f32>"}, {"b", "matrix<f32>"}}},
             {"gemm_accumulate", {{"a", "matrix<f32>"}, {"b", "matrix<f32>"},
                                  {"c", "matrix<f32>"}, {"alpha", "scalar<f32>"},
                                  {"beta", "scalar<f32>"}}},
             {"batched_gemm", {{"a", "tensor<f32>[batch,m,k]"},
                               {"b", "tensor<f32>[batch,k,n]"}}},
             {"gemm_chain", {{"a", "matrix<f32>"}, {"b", "matrix<f32>"},
                             {"c", "matrix<f32>"}}},
         }},
    };
}

json run(const Request& request) {
    const std::string function = request.function();

    if (function == "gemm" || function == "gemm_accumulate") {
        const Matrix a = matrix_input(request, "a");
        const Matrix b = matrix_input(request, "b");
        Matrix c = zero_output(a, b);
        float alpha = 1.0f;
        float beta = 0.0f;
        if (function == "gemm_accumulate") {
            c = matrix_input(request, "c");
            alpha = request.scalar<float>("alpha", "f32");
            beta = request.scalar<float>("beta", "f32");
        }
        c.values = gemm(a, b, c, alpha, beta);
        return matrix_result(c);
    }

    if (function == "batched_gemm") {
        const DenseInput a_input = request.dense("a", "tensor", 3);
        const DenseInput b_input = request.dense("b", "tensor", 3);
        if (a_input.shape[0] == 0 || a_input.shape[1] == 0 || a_input.shape[2] == 0 ||
            b_input.shape[0] == 0 || b_input.shape[1] == 0 || b_input.shape[2] == 0) {
            throw InputError("batched_gemm dimensions must be non-zero");
        }
        if (a_input.shape[0] != b_input.shape[0] ||
            a_input.shape[2] != b_input.shape[1]) {
            throw InputError("batched_gemm tensor shapes are incompatible");
        }
        const std::vector<float> a_values = request.values<float>(a_input, "f32", "a");
        const std::vector<float> b_values = request.values<float>(b_input, "f32", "b");
        const std::size_t batches = a_input.shape[0];
        const std::size_t m = a_input.shape[1];
        const std::size_t k = a_input.shape[2];
        const std::size_t n = b_input.shape[2];
        std::vector<float> output;
        output.reserve(batches * m * n);
        for (std::size_t batch = 0; batch < batches; ++batch) {
            Matrix a{m, k, {a_values.begin() + batch * m * k,
                            a_values.begin() + (batch + 1) * m * k}};
            Matrix b{k, n, {b_values.begin() + batch * k * n,
                            b_values.begin() + (batch + 1) * k * n}};
            Matrix c = zero_output(a, b);
            std::vector<float> values = gemm(a, b, c, 1.0f, 0.0f);
            output.insert(output.end(), values.begin(), values.end());
        }
        return dense_result("tensor", "f32", {batches, m, n}, output);
    }

    if (function == "gemm_chain") {
        const Matrix a = matrix_input(request, "a");
        const Matrix b = matrix_input(request, "b");
        const Matrix c = matrix_input(request, "c");
        Matrix intermediate = zero_output(a, b);
        intermediate.values = gemm(a, b, intermediate, 1.0f, 0.0f);
        Matrix output = zero_output(intermediate, c);
        output.values = gemm(intermediate, c, output, 1.0f, 0.0f);
        return matrix_result(output);
    }

    throw InputError("unknown cutlass function: " + function);
}

}  // namespace fuzz3::worker
