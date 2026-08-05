# Library worker

This directory contains the CPU and GPU workers used to execute the
libraries through one request protocol. Each Docker image contains one
selected library driver and one backend. The persistent Python manager isolates
executions, applies validation limits, and reports output and
entropy observations.

## Layout

```text
library_worker/
├── Dockerfile
├── build-docker.sh
├── common/                 shared C++ request validation and entry point
├── drivers/
│   ├── arrayfire/
│   ├── cutlass/
│   └── thrust/
├── seeds/                  one-line JSON examples for every operation
├── forkserver.py           persistent request manager
├── verify_worker.py        image smoke test
└── tests/                  unit tests
```

The Dockerfile has separate `dependencies`, `driver-build`, and `worker` stages.
Only the selected driver's `install.sh` is copied before the dependency stage is
built. Changes to `driver.cpp`, `driver.cu`, the broker, seeds, or documentation do
not rebuild ArrayFire or another heavy dependency.

## Drivers

| Driver | Operations | CPU implementation | GPU implementation |
| --- | --- | --- | --- |
| [Thrust](drivers/thrust/README.md) | `sort`, `reduce_sum`, `exclusive_scan`, `stable_sort_by_key`, `reduce_by_key`, `transform_axpby` | Thrust CPP system | Thrust CUDA system |
| [ArrayFire](drivers/arrayfire/README.md) | `sort`, `reduce_sum`, `matmul`, `transpose`, `fft`, `convolve1` | ArrayFire CPU backend | ArrayFire CUDA backend |
| [CUTLASS](drivers/cutlass/README.md) | `gemm`, `gemm_accumulate`, `batched_gemm`, `gemm_chain` | Row-major reference implementation | CUTLASS CUDA kernels |

Each driver directory owns three operational files:

- `install.sh <cpu|gpu>` installs or compiles its pinned dependency.
- `build.sh <cpu|gpu>` builds `/fuzz_workspace/native_harness`.
- `driver.cpp` or `driver.cu` implements the manifest and operations.

## Build images

Run the build script from the repository root:

```sh
./library_worker/build-docker.sh cpu thrust
./library_worker/build-docker.sh gpu thrust

./library_worker/build-docker.sh cpu arrayfire
./library_worker/build-docker.sh gpu arrayfire

./library_worker/build-docker.sh cpu cutlass
./library_worker/build-docker.sh gpu cutlass
```

Default image names use `fuzz3-worker:<library>-<backend>`. Pass a third argument
to choose another name:

```sh
./library_worker/build-docker.sh cpu arrayfire local/arrayfire:test
```

The following environment variables override pinned build settings:

```sh
ARRAYFIRE_REF=v3.9.0 CUTLASS_REF=v3.5.1 BUILD_JOBS=4 \
  ./library_worker/build-docker.sh cpu arrayfire
```

`CPU_BASE_IMAGE` and `GPU_BASE_IMAGE` can override the default Ubuntu 22.04 and
CUDA 12.4.1 development images.

## Request protocol

The worker reads one JSON object per line. A request selects a function and
provides named structured inputs:

```json
{"schema_version":1,"library":"arrayfire","function":"matmul","inputs":{"a":{"type":"matrix","dtype":"f32","shape":[2,3],"data":[1,2,3,4,5,6]},"b":{"type":"matrix","dtype":"f32","shape":[3,2],"data":[7,8,9,10,11,12]}}}
```

Dense vectors, matrices, and tensors use flat row-major `data`. Its length must
equal the product of `shape`. Scalars use `value` instead of `shape` and `data`:

```json
{"type":"scalar","dtype":"f32","value":0.5}
```

Optional controls request repeated executions for nondeterminism measurement:

```json
"controls":{"repetitions":8,"timeout_sec":5}
```

The maximum defaults are 64 repetitions, 30 seconds per native execution, one
MiB per request, and 1,048,576 dense elements. Invalid JSON, dtypes, ranks,
shapes, or operation constraints produce `status: "invalid"` and
`return_code: 300`. Native crashes and timeouts remain separate outcomes.

Send `{"command":"describe"}` to inspect the selected driver's runtime manifest.

## Run and verify

Run one CPU seed:

```sh
docker run --rm -i fuzz3-worker:arrayfire-cpu \
  < library_worker/seeds/arrayfire/matmul.json
```

Use the NVIDIA container runtime for a GPU image:

```sh
docker run --rm --gpus all -i fuzz3-worker:arrayfire-gpu \
  < library_worker/seeds/arrayfire/matmul.json
```

Smoke-test a built image and its manifest:

```sh
python3 library_worker/verify_worker.py \
  fuzz3-worker:thrust-cpu --library thrust

python3 library_worker/verify_worker.py \
  fuzz3-worker:thrust-gpu --library thrust --gpu
```

Run manager tests without building an image:

```sh
python3 -m unittest discover -s library_worker/tests -v
```

## Run with Fuzz3

Create a persistent CPU container. `-i` keeps the worker available for repeated
`docker exec` requests:

```sh
docker create -i --name thrust-cpu fuzz3-worker:thrust-cpu
```

For a GPU worker, add the NVIDIA runtime option:

```sh
docker create -i --gpus all --name thrust-gpu fuzz3-worker:thrust-gpu
```

The same launcher supports both backends:

```sh
./SUT/fuzz-library-worker.sh /tmp/thrust-seeds /tmp/thrust-out /tmp/thrust-crashes 1000 thrust-cpu thrust sort
```

The final function argument may be `all` to generate requests for every function
implemented by the selected driver. The launcher uses `library_worker_generator`
to create structured seeds and `library_worker_mutator` to preserve JSON, dtypes,
shapes, and paired-vector constraints. Set `FUZZ3_SEEDS` to change the default 200
generated seeds.

`docker_executor` sends each request through `docker exec -i`; it does not allocate
a TTY or construct a shell pipeline. Application return code 300 remains an
invalid-input outcome, while process failures and timeouts remain crash and hang
outcomes.

## Add a driver

Create `drivers/<library>/` containing `install.sh`, `build.sh`, a `driver.cpp` or
`driver.cu`, and a README describing its request schema. The native source must
implement `driver_name`, `driver_manifest`, and `run`, and `build.sh` must produce
`/fuzz_workspace/native_harness`. No Dockerfile changes are required.
