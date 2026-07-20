FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

ARG TARGET_LIBRARY=thrust
ARG BACKEND=gpu
ENV TARGET_LIBRARY=${TARGET_LIBRARY}
ENV BACKEND=${BACKEND}

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --fix-missing \
    python3 \
    python3-pip \
    build-essential \
    cmake \
    git \
    wget \
    libfreeimage-dev \
    libfftw3-dev \
    liblapacke-dev \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /fuzz_workspace

RUN if [ "$TARGET_LIBRARY" = "cutlass" ] ; then \
        echo "Fetching CUTLASS repository..." && \
        git clone --recursive https://github.com/NVIDIA/cutlass.git /fuzz_workspace/cutlass ; \
    elif [ "$TARGET_LIBRARY" = "arrayfire" ] ; then \
        echo "Installing ArrayFire..." && \
        apt-get update && \
        apt-get install -y libarrayfire-cpu-dev libarrayfire-cuda-dev && \
        rm -rf /var/lib/apt/lists/* ; \
    fi

COPY harness.cu /fuzz_workspace/harness.cu
COPY forkserver.py /fuzz_workspace/forkserver.py

RUN macro_backend=$(if [ "$BACKEND" = "cpu" ]; then echo "-DMODE_CPU"; else echo "-DMODE_GPU"; fi) && \
    compiler=$(if [ "$BACKEND" = "cpu" ] && [ "$TARGET_LIBRARY" = "thrust" ]; then echo "g++ -x c++"; else echo "nvcc"; fi) && \
    \
    if [ "$TARGET_LIBRARY" = "thrust" ] ; then \
        $compiler -O3 harness.cu -o native_harness -DTRACK_THRUST $macro_backend ; \
    elif [ "$TARGET_LIBRARY" = "cutlass" ] ; then \
        nvcc -O3 harness.cu -I/fuzz_workspace/cutlass/include -I/fuzz_workspace/cutlass/tools/util/include -o native_harness -DTRACK_CUTLASS $macro_backend ; \
    elif [ "$TARGET_LIBRARY" = "arrayfire" ] ; then \
        nvcc -O3 harness.cu -lafire -o native_harness -DTRACK_ARRAYFIRE $macro_backend ; \
    fi

ENTRYPOINT ["python3", "-u", "/fuzz_workspace/forkserver.py"]
