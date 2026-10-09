#!/bin/sh
set -eu

if [ "$1" = "gpu" ]; then
    backend_library=afcuda
    backend_macro=FUZZ3_GPU
    cuda_driver_flags="-L/usr/local/cuda/lib64/stubs -Wl,-rpath-link,/usr/local/cuda/lib64/stubs -lcuda"
else
    backend_library=afcpu
    backend_macro=FUZZ3_CPU
    cuda_driver_flags=
fi

g++ -std=c++17 -O2 -D"$backend_macro" \
    -I/fuzz_workspace/common -I/opt/arrayfire/include \
    /fuzz_workspace/common/main.cpp \
    /fuzz_workspace/driver/driver.cpp \
    -L/opt/arrayfire/lib -L/opt/arrayfire/lib64 \
    -Wl,-rpath,/opt/arrayfire/lib -Wl,-rpath,/opt/arrayfire/lib64 \
    -l"$backend_library" $cuda_driver_flags -o /fuzz_workspace/native_harness
