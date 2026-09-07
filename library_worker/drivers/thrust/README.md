# Thrust driver

The Thrust driver uses host vectors with the CPP device system in CPU images and
device vectors with the CUDA device system in GPU images.

## Functions

| Function | Inputs | Result |
| --- | --- | --- |
| `sort` | `values`: vector of `f32`, `f64`, `i32`, or `i64`; optional `descending`: scalar `bool` | Vector with the input dtype and shape |
| `reduce_sum` | `values`: vector `f32` | Scalar `f32` |
| `exclusive_scan` | `values`: vector `i32` | Vector `i32` with the input shape |
| `stable_sort_by_key` | `keys`: vector `i32`; `values`: vector `f32` | Object containing reordered `keys` and `values` |
| `reduce_by_key` | `keys`: vector `i32`; `values`: vector `f32` | Object containing reduced `keys` and `values` |
| `transform_axpby` | `x`, `y`: vector `f32`; `alpha`, `beta`: scalar `f32` | Vector `f32` containing `alpha*x + beta*y` |

`keys` and `values`, or `x` and `y`, must have identical shapes.
`reduce_by_key` reduces consecutive equal keys, matching Thrust semantics.

## Input format

```json
{"schema_version":1,"library":"thrust","function":"transform_axpby","inputs":{"x":{"type":"vector","dtype":"f32","shape":[4],"data":[1,-2,3,-4]},"y":{"type":"vector","dtype":"f32","shape":[4],"data":[4,3,2,1]},"alpha":{"type":"scalar","dtype":"f32","value":0.5},"beta":{"type":"scalar","dtype":"f32","value":-2}}}
```

All dense inputs use flat row-major data, although current Thrust operations are
one-dimensional. See [`seeds/thrust`](../../seeds/thrust) for every operation.

## Build

```sh
./library_worker/build-docker.sh cpu thrust
./library_worker/build-docker.sh gpu thrust
```
