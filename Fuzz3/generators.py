#WBL 15 Jun 2026 add olc_decoder_generator_corner

import copy
import json
import os
from pathlib import Path
import random
import subprocess
import sys


################################ Target: OLC #################################
# Source code from https://github.com/google/open-location-code.
# See the readme of Fuzz3 regarding how to install it
##############################################################################

def olc_encoder_generator_legal(seedsno: int, outputfolder: Path) -> int:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    for i in range(seedsno):
        lat = random.randint(-90, 90)
        long = random.randint(-180, 180)

        seed_path = outputfolder / f"fuzz3_olce_legal_{i}.seed"
        seed_path.write_text(f"{lat},{long}")

        total += 1

    return total


def olc_encoder_generator_illegal(seedsno: int, outputfolder: Path) -> int:
    outputfolder.mkdir(parents=True, exist_ok=True)
    
    total = 0
    for i in range(seedsno):
        lat = random.randint(-1024, 1024)
        long = random.randint(-1024, 1024)

        seed_path = outputfolder / f"fuzz3_olce_illegal_{i}.seed"
        seed_path.write_text(f"{lat},{long}")

        total += 1

    return total

def _helper_gen_olc_code_semi_legal() -> str:
    alphabet = "123456789CFGHJMPQRVWX"
    
    total_length = random.randint(3, 18)  # must be at least 3 to allow split
    split_index = total_length // 2       # position of '+'
    
    left = "".join(random.choice(alphabet) for _ in range(split_index))
    right = "".join(random.choice(alphabet) for _ in range(total_length - split_index))
    
    return f"{left}+{right}"

def olc_decoder_generator_semi_legal(seedsno: int, outputfolder: Path) -> tuple[int, int]:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    for i in range(seedsno):
        ret = _helper_gen_olc_code_semi_legal() 
        seed_path = outputfolder / f"fuzz3_olcd_sm_{i}.seed"
        seed_path.write_text(f"{ret}")
        total += 1

    return total
    
def _helper_gen_olc_code() -> str:
    alphabet = "123456789CFGHJMPQRVWX+-?"
    length = random.randint(2, 25)

    # 9C5V2RP7+JVXH835 examplple
    return "".join(random.choice(alphabet) for _ in range(length))

def olc_decoder_generator_illegal(seedsno: int, outputfolder: Path) -> tuple[int, int]:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    for i in range(seedsno):
        ret = _helper_gen_olc_code() 
        seed_path = outputfolder / f"fuzz3_olcd_illegal_{i}.seed"
        seed_path.write_text(f"{ret}")
        total += 1

    return total


def olc_decoder_generator_legal(seedsno: int, outputfolder: Path) -> int:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    for i in range(seedsno):
        lat = random.randint(-90, 90)
        long = random.randint(-180, 180)

        # Then encode it, and we get legal decoder seeds!
        code = (
            "from openlocationcode import openlocationcode as olc;"
            f"print(olc.encode({lat},{long}))"
        )

        try:
            r = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=50,
            )
            if r.returncode == 0:
                seed_path = outputfolder / f"fuzz3_olcd_legal_{i}.seed"
                seed_path.write_text(f"{r.stdout}")
                total += 1
            else:
                print(f"(Fuzz3:INFO) Failed to generate 1 seed {lat},{long} mapped to invalid seed. Skip.")
        except subprocess.TimeoutExpired as e:
            print(f"(Fuzz3:INFO) Failed to generate 1 seed {lat},{long} timed out. Skip.")

    return total

def olc_decoder_generator_corner(seedsno: int, outputfolder: Path) -> int:
    outputfolder.mkdir(parents=True, exist_ok=True)

    OLC_ALPHABET = "23456789CFGHJMPQRVWX"
    total = 0
    for lat in range(12):                    #southpole to northpole plus errors
        for long in range(len(OLC_ALPHABET)):#round equator plus errors
            seed_path = outputfolder / f"fuzz3_olcd_corner_{lat}_{long}.seed"
            text = OLC_ALPHABET[lat]+OLC_ALPHABET[long]+"222222+22"
            seed_path.write_text(f"{text}")
            total += 1

    return total


################################# Target: H3 #################################
# Source code from https://github.com/uber/h3.
# See the readme of Fuzz3 regarding how to install it
##############################################################################

def _helper_gen_h3_encode_seed() -> str:
    lat = random.uniform(-90, 90)
    lng = random.uniform(-180, 180)
    res = 10
    return f"{lat},{lng},{res}"

def _helper_gen_h3_index() -> str:
    value = random.getrandbits(64)
    return f"{value:016x}"

def h3_encoder_generator(seedsno: int, outputfolder: Path) -> tuple[int, int]:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    for i in range(seedsno):
        ret = _helper_gen_h3_encode_seed() 
        seed_path = outputfolder / f"fuzz3_h3e_{i}.seed"
        seed_path.write_text(f"{ret}")
        total += 1

    return total
    
def h3_decoder_generator(seedsno: int, outputfolder: Path) -> tuple[int, int]:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    for i in range(seedsno):
        ret = _helper_gen_h3_index() 
        seed_path = outputfolder / f"fuzz3_h3d_{i}.seed"
        seed_path.write_text(f"{ret}")
        total += 1

    return total
LIBRARY_FUNCTIONS = {
    "thrust": (
        "sort",
        "reduce_sum",
        "exclusive_scan",
        "stable_sort_by_key",
        "reduce_by_key",
        "transform_axpby",
    ),
    "arrayfire": (
        "sort",
        "reduce_sum",
        "matmul",
        "transpose",
        "fft",
        "convolve1",
    ),
    "cutlass": ("gemm", "gemm_accumulate", "batched_gemm", "gemm_chain"),
}
DEFAULT_FUNCTION = {"thrust": "sort", "arrayfire": "sort", "cutlass": "gemm"}
def _dense(kind, dtype, shape, data):
    return {"type": kind, "dtype": dtype, "shape": shape, "data": data}


def _scalar(dtype, value):
    return {"type": "scalar", "dtype": dtype, "value": value}


def _floats(count):
    return [round(random.uniform(-10.0, 10.0), 4) for _ in range(count)]


def _ints(count, low=-8, high=8):
    return [random.randint(low, high) for _ in range(count)]


def _matrix(rows, columns):
    return _dense("matrix", "f32", [rows, columns], _floats(rows * columns))


def _thrust_request(function):
    size = random.randint(2, 10)
    if function == "sort":
        return {
            "values": _dense("vector", "f32", [size], _floats(size)),
            "descending": _scalar("bool", random.choice((False, True))),
        }
    if function == "reduce_sum":
        return {"values": _dense("vector", "f32", [size], _floats(size))}
    if function == "exclusive_scan":
        return {"values": _dense("vector", "i32", [size], _ints(size))}
    if function in ("stable_sort_by_key", "reduce_by_key"):
        return {
            "keys": _dense("vector", "i32", [size], _ints(size, 0, 3)),
            "values": _dense("vector", "f32", [size], _floats(size)),
        }
    if function == "transform_axpby":
        return {
            "x": _dense("vector", "f32", [size], _floats(size)),
            "y": _dense("vector", "f32", [size], _floats(size)),
            "alpha": _scalar("f32", random.choice((-2.0, -0.5, 0.5, 2.0))),
            "beta": _scalar("f32", random.choice((-2.0, -0.5, 0.5, 2.0))),
        }
    raise ValueError(f"unsupported Thrust function: {function}")


def _arrayfire_request(function):
    size = random.randint(2, 10)
    if function in ("sort", "reduce_sum", "fft"):
        return {"values": _dense("vector", "f32", [size], _floats(size))}
    if function == "matmul":
        m, k, n = (random.randint(1, 4) for _ in range(3))
        return {"a": _matrix(m, k), "b": _matrix(k, n)}
    if function == "transpose":
        rows, columns = random.randint(1, 4), random.randint(1, 4)
        return {"matrix": _matrix(rows, columns)}
    if function == "convolve1":
        signal_size = random.randint(2, 10)
        kernel_size = random.randint(1, 5)
        return {
            "signal": _dense("vector", "f32", [signal_size], _floats(signal_size)),
            "kernel": _dense("vector", "f32", [kernel_size], _floats(kernel_size)),
        }
    raise ValueError(f"unsupported ArrayFire function: {function}")


def _cutlass_request(function):
    m, k, n = (random.randint(1, 4) for _ in range(3))
    if function == "gemm":
        return {"a": _matrix(m, k), "b": _matrix(k, n)}
    if function == "gemm_accumulate":
        return {
            "a": _matrix(m, k),
            "b": _matrix(k, n),
            "c": _matrix(m, n),
            "alpha": _scalar("f32", random.choice((-2.0, -0.5, 0.5, 2.0))),
            "beta": _scalar("f32", random.choice((-2.0, -0.5, 0.5, 2.0))),
        }
    if function == "batched_gemm":
        batches = random.randint(1, 3)
        return {
            "a": _dense("tensor", "f32", [batches, m, k], _floats(batches * m * k)),
            "b": _dense("tensor", "f32", [batches, k, n], _floats(batches * k * n)),
        }
    if function == "gemm_chain":
        columns = random.randint(1, 4)
        return {"a": _matrix(m, k), "b": _matrix(k, n), "c": _matrix(n, columns)}
    raise ValueError(f"unsupported CUTLASS function: {function}")


def _new_request(library, function):
    builders = {
        "thrust": _thrust_request,
        "arrayfire": _arrayfire_request,
        "cutlass": _cutlass_request,
    }
    return {
        "schema_version": 1,
        "library": library,
        "function": function,
        "inputs": builders[library](function),
    }


def _scale_pair(inputs, left, right, factor):
    inputs[left]["data"] = [value * factor for value in inputs[left]["data"]]
    inputs[right]["data"] = [value / factor for value in inputs[right]["data"]]


def _variant(request, index):
    result = copy.deepcopy(request)
    function = result["function"]
    inputs = result["inputs"]
    if function in ("sort", "reduce_sum"):
        values = inputs["values"]["data"]
        offset = index % len(values)
        inputs["values"]["data"] = values[offset:] + values[:offset]
    elif function in ("matmul", "gemm", "gemm_accumulate", "batched_gemm"):
        _scale_pair(inputs, "a", "b", (1.0, 2.0, 0.5, -1.0, -2.0)[index % 5])
    elif function == "convolve1":
        _scale_pair(inputs, "signal", "kernel", (1.0, 2.0, 0.5, -1.0, -2.0)[index % 5])
    elif function == "gemm_chain":
        _scale_pair(inputs, "a", "b", (1.0, 2.0, 0.5, -1.0, -2.0)[index % 5])
    return result


def _selected_functions(library):
    selected = os.environ.get("FUZZ3_FUNCTION", DEFAULT_FUNCTION[library]).strip()
    functions = LIBRARY_FUNCTIONS[library] if selected == "all" else tuple(
        item.strip() for item in selected.split(",") if item.strip()
    )
    unknown = set(functions) - set(LIBRARY_FUNCTIONS[library])
    if not functions or unknown:
        raise ValueError(f"unsupported {library} functions: {sorted(unknown)}")
    return functions


def _generate_requests(seedsno, outputfolder, library, functions):
    outputfolder.mkdir(parents=True, exist_ok=True)
    base = None
    for index in range(max(0, seedsno)):
        if index % 5 == 0:
            function = functions[(index // 5) % len(functions)]
            base = _new_request(library, function)
        request = _variant(base, index % 5)
        path = outputfolder / f"fuzz3_{library}_{request['function']}_{index}.json"
        path.write_text(
            json.dumps(request, sort_keys=True, separators=(",", ":"), allow_nan=False),
            encoding="utf-8",
        )
    return max(0, seedsno)


def library_worker_generator(seedsno: int, outputfolder: Path) -> int:
    library = os.environ.get("FUZZ3_LIBRARY", "thrust").strip().lower()
    if library not in LIBRARY_FUNCTIONS:
        raise ValueError(f"unsupported library: {library}")
    return _generate_requests(seedsno, outputfolder, library, _selected_functions(library))


def sort_generator_legal(seedsno: int, outputfolder: Path) -> int:
    return _generate_requests(seedsno, outputfolder, "thrust", ("sort",))
