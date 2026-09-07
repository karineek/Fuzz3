#!/bin/sh
set -eu

apt-get -o Acquire::Retries=3 -o Acquire::http::No-Cache=True update
apt-get install -y --no-install-recommends \
    libboost-dev libfftw3-dev liblapacke-dev libopenblas-dev libspdlog-dev ocl-icd-opencl-dev
rm -rf /var/lib/apt/lists/*

git clone --branch "${ARRAYFIRE_REF:-v3.9.0}" --depth 1 \
    https://github.com/arrayfire/arrayfire.git /tmp/arrayfire

if [ "$1" = "gpu" ]; then
    cmake -S /tmp/arrayfire -B /tmp/arrayfire/build \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/opt/arrayfire \
        -DAF_BUILD_CPU=OFF -DAF_BUILD_CUDA=ON \
        -DAF_BUILD_OPENCL=OFF -DAF_BUILD_ONEAPI=OFF \
        -DAF_BUILD_EXAMPLES=OFF -DAF_BUILD_FORGE=OFF -DBUILD_TESTING=OFF
else
    cmake -S /tmp/arrayfire -B /tmp/arrayfire/build \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/opt/arrayfire \
        -DAF_BUILD_CPU=ON -DAF_BUILD_CUDA=OFF \
        -DAF_BUILD_OPENCL=OFF -DAF_BUILD_ONEAPI=OFF \
        -DAF_BUILD_EXAMPLES=OFF -DAF_BUILD_FORGE=OFF -DBUILD_TESTING=OFF
fi

cmake --build /tmp/arrayfire/build --parallel "${BUILD_JOBS:-2}"
cmake --install /tmp/arrayfire/build
rm -rf /tmp/arrayfire
