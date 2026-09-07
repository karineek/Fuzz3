#!/bin/sh
set -eu

if [ "$1" = "gpu" ]; then
    nvcc -std=c++17 -O2 -DFUZZ3_GPU -x cu \
        -I/fuzz_workspace/common \
        -I/fuzz_workspace/cutlass/include \
        /fuzz_workspace/common/main.cpp \
        /fuzz_workspace/driver/driver.cu \
        -o /fuzz_workspace/native_harness
else
    g++ -std=c++17 -O2 -DFUZZ3_CPU -x c++ \
        -I/fuzz_workspace/common \
        /fuzz_workspace/common/main.cpp \
        /fuzz_workspace/driver/driver.cu \
        -o /fuzz_workspace/native_harness
fi
