FROM ubuntu:22.04

ARG TARGET_LIBRARY=thrust
ARG BACKEND=cpu

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
