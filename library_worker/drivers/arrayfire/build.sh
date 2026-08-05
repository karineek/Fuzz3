#!/bin/sh
set -eu

if [ "$1" = "gpu" ]; then
    backend_library=afcuda
    backend_macro=FUZZ3_GPU
else
    backend_library=afcpu
    backend_macro=FUZZ3_CPU
fi

g++ -std=c++17 -O2 -D"$backend_macro" \
    -I/fuzz_workspace/common -I/opt/arrayfire/include \
    /fuzz_workspace/common/main.cpp \
    /fuzz_workspace/driver/driver.cpp \
    -L/opt/arrayfire/lib -L/opt/arrayfire/lib64 \
    -Wl,-rpath,/opt/arrayfire/lib -Wl,-rpath,/opt/arrayfire/lib64 \
    -l"$backend_library" -o /fuzz_workspace/native_harness
