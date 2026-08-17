# ArrayFire driver

The ArrayFire driver compiles ArrayFire v3.9.0 from source for the selected CPU or
CUDA backend. Protocol matrices are row-major; the driver converts them to and
from ArrayFire's column-major storage. Array dimensions are checked before being
converted to ArrayFire's global `dim_t`.

## Functions

| Function | Inputs | Result |
| --- | --- | --- |
| `sort` | `values`: vector `f32` | Sorted vector `f32` |
| `reduce_sum` | `values`: vector `f32` | Scalar `f64` |
| `matmul` | `a`, `b`: matrix `f32` | Matrix `f32` with shape `[a.rows, b.columns]` |
| `transpose` | `matrix`: matrix `f32` | Matrix `f32` with reversed dimensions |
| `fft` | `values`: vector `f32` | Object containing `real` and `imag` vectors |
| `convolve1` | `signal`, `kernel`: vector `f32` | Expanded one-dimensional convolution vector |

Vectors and matrix dimensions must be non-zero. For `matmul`, `a.shape[1]` must
equal `b.shape[0]`. All current ArrayFire input arrays use `f32`.

## Input format

```json
{"schema_version":1,"library":"arrayfire","function":"matmul","inputs":{"a":{"type":"matrix","dtype":"f32","shape":[2,3],"data":[1,2,3,4,5,6]},"b":{"type":"matrix","dtype":"f32","shape":[3,2],"data":[7,8,9,10,11,12]}}}
```

See [`seeds/arrayfire`](../../seeds/arrayfire) for every operation.

## Build

```sh
./library_worker/build-docker.sh cpu arrayfire
./library_worker/build-docker.sh gpu arrayfire
```

The CPU source configuration includes:

```text
-DAF_BUILD_CPU=ON
-DAF_BUILD_CUDA=OFF
-DBUILD_TESTING=OFF
-DAF_BUILD_FORGE=OFF
```

Override the pinned ref or parallelism with `ARRAYFIRE_REF` and `BUILD_JOBS`.
