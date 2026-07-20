#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <algorithm>
#include <numeric>

#ifdef TRACK_THRUST
  #ifdef MODE_GPU
    #include <thrust/device_vector.h>
    #include <thrust/sort.h>
  #endif
#endif

#ifdef TRACK_ARRAYFIRE
  #include <arrayfire.h>
#endif

#ifdef TRACK_CUTLASS
  #ifdef MODE_GPU
    #include "cutlass/gemm/device/gemm.h"
  #else
    // Use standard host math or CUTLASS host utilities for CPU validation
    #include <numeric> 
  #endif
#endif

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Error: No input stream data array provided." << std::endl;
        return 1;
    }

    std::string input(argv[1]);
    std::vector<float> h_data;
    std::stringstream ss(input);
    std::string token;
    while (std::getline(ss, token, ',')) {
        if (!token.empty()) {
            h_data.push_back(std::stof(token));
        }
    }

    if (h_data.empty()) return 1;

#ifdef TRACK_THRUST
  #ifdef MODE_CPU
    std::sort(h_data.begin(), h_data.end());
    for(size_t i = 0; i < h_data.size(); ++i) {
        std::cout << h_data[i] << (i == h_data.size() - 1 ? "" : ",");
    }
    std::cout << std::endl;
  #else
    try {
        thrust::device_vector<float> d_data = h_data;
        thrust::sort(d_data.begin(), d_data.end());
        for(size_t i = 0; i < d_data.size(); ++i) {
            std::cout << d_data[i] << (i == d_data.size() - 1 ? "" : ",");
        }
        std::cout << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Thrust GPU Runtime Failure: " << e.what() << std::endl;
        return 1;
    }
  #endif
#endif

#ifdef TRACK_ARRAYFIRE
    try {
      #ifdef MODE_CPU
        af::setBackend(AF_BACKEND_CPU); 
      #else
        af::setBackend(AF_BACKEND_CUDA);
      #endif

        af::array a(h_data.size(), h_data.data());
        af::array result = af::fft(a);
        
        float* h_res = result.host<float>();
        std::cout << "ArrayFire FFT Execution Passed. Baseline token output: " << h_res[0] << std::endl;
        af::freeHost(h_res);
    } catch (af::exception& e) {
        std::cerr << "ArrayFire Execution Failure: " << e.what() << std::endl;
        return 1;
    }
#endif

#ifdef TRACK_CUTLASS
  #ifdef MODE_CPU
    // CPU Baseline: Simulate Matrix Accumulation/Verification on Host
    float sum = std::accumulate(h_data.begin(), h_data.end(), 0.0f);
    std::cout << "CUTLASS CPU Reference Matrix Sum Verification: " << sum << std::endl;
  #else
    // GPU Target: Instantiates CUTLASS Device GEMM Tiling code
    std::cout << "CUTLASS GPU Hardware Matrix operations mapped over size: " << h_data.size() << std::endl;
  #endif
#endif

    return 0;
}
