ARG BASE_IMAGE=ubuntu:22.04
FROM ${BASE_IMAGE} AS dependencies

ARG BACKEND=cpu

ENV DEBIAN_FRONTEND=noninteractive \
    BACKEND=${BACKEND} \
    LD_LIBRARY_PATH=/opt/arrayfire/lib:/opt/arrayfire/lib64

RUN apt-get -o Acquire::Retries=3 -o Acquire::http::No-Cache=True update \
    && apt-get install -y --no-install-recommends \
        build-essential ca-certificates cmake git nlohmann-json3-dev python3 \
    && rm -rf /var/lib/apt/lists/*

ARG TARGET_LIBRARY=thrust
ARG CUTLASS_REF=v3.5.1
ARG ARRAYFIRE_REF=v3.9.0
ARG BUILD_JOBS=2

ENV CUTLASS_REF=${CUTLASS_REF} \
    ARRAYFIRE_REF=${ARRAYFIRE_REF} \
    BUILD_JOBS=${BUILD_JOBS}

COPY drivers/${TARGET_LIBRARY}/install.sh /tmp/driver-install.sh

RUN case "$BACKEND" in cpu|gpu) ;; *) exit 2 ;; esac \
    && sh /tmp/driver-install.sh "$BACKEND" \
    && rm /tmp/driver-install.sh

FROM dependencies AS driver-build

WORKDIR /fuzz_workspace

COPY common /fuzz_workspace/common
COPY drivers/${TARGET_LIBRARY}/build.sh /fuzz_workspace/driver/build.sh
COPY drivers/${TARGET_LIBRARY}/driver.* /fuzz_workspace/driver/

RUN sh /fuzz_workspace/driver/build.sh "$BACKEND"

FROM dependencies AS worker

WORKDIR /fuzz_workspace

COPY --from=driver-build /fuzz_workspace/native_harness /fuzz_workspace/native_harness
COPY forkserver.py /fuzz_workspace/forkserver.py

CMD ["python3", "-u", "/fuzz_workspace/forkserver.py"]
