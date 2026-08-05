#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys


CASES = {
    "thrust": {
        "schema_version": 1,
        "library": "thrust",
        "function": "sort",
        "inputs": {
            "values": {
                "type": "vector",
                "dtype": "f32",
                "shape": [5],
                "data": [10.5, 2.3, 99.1, 0.05, 43.2],
            }
        },
        "controls": {"repetitions": 3},
    },
    "arrayfire": {
        "schema_version": 1,
        "library": "arrayfire",
        "function": "matmul",
        "inputs": {
            "a": {
                "type": "matrix",
                "dtype": "f32",
                "shape": [2, 3],
                "data": [1, 2, 3, 4, 5, 6],
            },
            "b": {
                "type": "matrix",
                "dtype": "f32",
                "shape": [3, 2],
                "data": [7, 8, 9, 10, 11, 12],
            },
        },
    },
    "cutlass": {
        "schema_version": 1,
        "library": "cutlass",
        "function": "gemm",
        "inputs": {
            "a": {
                "type": "matrix",
                "dtype": "f32",
                "shape": [2, 2],
                "data": [1, 2, 3, 4],
            },
            "b": {
                "type": "matrix",
                "dtype": "f32",
                "shape": [2, 2],
                "data": [5, 6, 7, 8],
            },
        },
    },
}


def exchange(worker, request):
    worker.stdin.write(json.dumps(request, separators=(",", ":")) + "\n")
    worker.stdin.flush()
    line = worker.stdout.readline()
    if not line:
        raise RuntimeError("worker stopped before returning a response")
    return json.loads(line)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("--library", choices=sorted(CASES), required=True)
    parser.add_argument("--gpu", action="store_true")
    args = parser.parse_args()

    command = ["docker", "run", "--rm", "-i"]
    if args.gpu:
        command.extend(["--gpus", "all"])
    command.append(args.image)
    worker = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    try:
        manifest = exchange(worker, {"command": "describe"})
        result = exchange(worker, CASES[args.library])
        print(json.dumps({"manifest": manifest, "execution": result}, indent=2))
        return 0 if result.get("status") == "success" else 1
    finally:
        worker.stdin.close()
        worker.terminate()
        worker.wait(timeout=5)


if __name__ == "__main__":
    sys.exit(main())
