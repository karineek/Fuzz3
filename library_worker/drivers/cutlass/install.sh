#!/bin/sh
set -eu

if [ "$1" = "gpu" ]; then
    mkdir -p /fuzz_workspace
    git clone --branch "${CUTLASS_REF:-v3.5.1}" --depth 1 \
        https://github.com/NVIDIA/cutlass.git /fuzz_workspace/cutlass
fi
