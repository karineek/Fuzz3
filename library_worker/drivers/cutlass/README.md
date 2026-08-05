# CUTLASS driver

The GPU backend uses CUTLASS v3.5.1 CUDA GEMM kernels. CUTLASS has no CPU backend,
so the CPU image provides a row-major reference implementation with the same
request and result protocol.

## Functions

| Function | Inputs | Result |
| --- | --- | --- |
| `gemm` | `a`: matrix `f32` `[m,k]`; `b`: matrix `f32` `[k,n]` | Matrix `f32` `[m,n]` |
| `gemm_accumulate` | `a`, `b`, `c`: matrix `f32`; `alpha`, `beta`: scalar `f32` | `alpha*(a*b) + beta*c` |
| `batched_gemm` | `a`: tensor `f32` `[batch,m,k]`; `b`: tensor `f32` `[batch,k,n]` | Tensor `f32` `[batch,m,n]` |
| `gemm_chain` | `a`, `b`, `c`: compatible matrix `f32` inputs | Matrix `f32` containing `(a*b)*c` |

All dimensions must be non-zero. Matrices and tensors contain flat row-major
data. `gemm_accumulate` requires `c.shape == [a.rows, b.columns]`.

## Input format

```json
{"schema_version":1,"library":"cutlass","function":"gemm_accumulate","inputs":{"a":{"type":"matrix","dtype":"f32","shape":[2,2],"data":[1,2,3,4]},"b":{"type":"matrix","dtype":"f32","shape":[2,2],"data":[5,6,7,8]},"c":{"type":"matrix","dtype":"f32","shape":[2,2],"data":[1,1,1,1]},"alpha":{"type":"scalar","dtype":"f32","value":0.5},"beta":{"type":"scalar","dtype":"f32","value":2}}}
```

See [`seeds/cutlass`](../../seeds/cutlass) for every operation.

## Build

```sh
./library_worker/build-docker.sh cpu cutlass
./library_worker/build-docker.sh gpu cutlass
```

Override the pinned repository ref with `CUTLASS_REF`.
