#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    echo "Usage: $0 <cpu|gpu> <library> [image]" >&2
    exit 2
fi

backend=$1
library=$2
image=${3:-fuzz3-worker:${library}-${backend}}

case "$backend" in
    cpu) base_image=${CPU_BASE_IMAGE:-ubuntu:22.04} ;;
    gpu) base_image=${GPU_BASE_IMAGE:-nvidia/cuda:12.4.1-devel-ubuntu22.04} ;;
    *)
        echo "Backend must be cpu or gpu" >&2
        exit 2
        ;;
esac

if [ ! -f "$script_dir/drivers/$library/install.sh" ] ||
   [ ! -f "$script_dir/drivers/$library/build.sh" ]; then
    echo "Unknown or incomplete driver: $library" >&2
    exit 2
fi

docker build \
    --build-arg BASE_IMAGE="$base_image" \
    --build-arg TARGET_LIBRARY="$library" \
    --build-arg BACKEND="$backend" \
    --build-arg ARRAYFIRE_REF="${ARRAYFIRE_REF:-v3.9.0}" \
    --build-arg CUTLASS_REF="${CUTLASS_REF:-v3.5.1}" \
    --build-arg BUILD_JOBS="${BUILD_JOBS:-2}" \
    -t "$image" "$script_dir"

printf 'Built %s with the %s driver on the %s backend\n' \
    "$image" "$library" "$backend"
