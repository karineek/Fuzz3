"""The type grammar shared by library-worker generators and mutators.

Dimension names unify inputs such as ``[m, k]`` and ``[k, n]``. Output shapes
reuse those names, so compatible calls can be chained without knowing the
library implementation.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
import math
import operator
import os
import random


DTYPE_ALIASES = {"number": ("f32", "f64", "i32", "i64")}
SHAPE_OPERATORS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul}
WEIRD_EXTENTS = (1, 3, 5, 7, 9, 15, 17, 31, 33)


@dataclass(frozen=True)
class ValueSpec:
    kind: str
    dtypes: tuple[str, ...]
    shape: tuple[str, ...] = ()
    optional: bool = False


@dataclass(frozen=True)
class SameAs:
    input_name: str


@dataclass(frozen=True)
class OperationSpec:
    inputs: dict[str, ValueSpec]
    outputs: dict[str, ValueSpec | SameAs]


@dataclass(frozen=True)
class ValueType:
    kind: str
    dtype: str
    shape: tuple[int | None, ...] = ()


def value(kind, dtype, *shape, optional=False):
    dtypes = DTYPE_ALIASES.get(dtype, (dtype,))
    return ValueSpec(kind, dtypes, shape, optional)


def operation(inputs, outputs):
    return OperationSpec(inputs, outputs)


def same_as(input_name):
    return SameAs(input_name)


GRAMMARS = {
    "thrust": {
        "sort": operation(
            {
                "values": value("vector", "number", "n"),
                "descending": value("scalar", "bool", optional=True),
            },
            {"": same_as("values")},
        ),
        "reduce_sum": operation(
            {"values": value("vector", "f32", "n")},
            {"": value("scalar", "f32")},
        ),
        "exclusive_scan": operation(
            {"values": value("vector", "i32", "n")},
            {"": same_as("values")},
        ),
        "stable_sort_by_key": operation(
            {
                "keys": value("vector", "i32", "n"),
                "values": value("vector", "f32", "n"),
            },
            {"keys": same_as("keys"), "values": same_as("values")},
        ),
        "reduce_by_key": operation(
            {
                "keys": value("vector", "i32", "n"),
                "values": value("vector", "f32", "n"),
            },
            {
                "keys": value("vector", "i32", "?"),
                "values": value("vector", "f32", "?"),
            },
        ),
        "transform_axpby": operation(
            {
                "x": value("vector", "f32", "n"),
                "y": value("vector", "f32", "n"),
                "alpha": value("scalar", "f32"),
                "beta": value("scalar", "f32"),
            },
            {"": same_as("x")},
        ),
    },
    "arrayfire": {
        "sort": operation(
            {"values": value("vector", "f32", "n")},
            {"": same_as("values")},
        ),
        "reduce_sum": operation(
            {"values": value("vector", "f32", "n")},
            {"": value("scalar", "f64")},
        ),
        "matmul": operation(
            {
                "a": value("matrix", "f32", "m", "k"),
                "b": value("matrix", "f32", "k", "n"),
            },
            {"": value("matrix", "f32", "m", "n")},
        ),
        "transpose": operation(
            {"matrix": value("matrix", "f32", "m", "n")},
            {"": value("matrix", "f32", "n", "m")},
        ),
        "fft": operation(
            {"values": value("vector", "f32", "n")},
            {"real": same_as("values"), "imag": same_as("values")},
        ),
        "convolve1": operation(
            {
                "signal": value("vector", "f32", "n"),
                "kernel": value("vector", "f32", "k"),
            },
            {"": value("vector", "f32", "n+k-1")},
        ),
    },
    "cutlass": {
        "gemm": operation(
            {
                "a": value("matrix", "f32", "m", "k"),
                "b": value("matrix", "f32", "k", "n"),
            },
            {"": value("matrix", "f32", "m", "n")},
        ),
        "gemm_accumulate": operation(
            {
                "a": value("matrix", "f32", "m", "k"),
                "b": value("matrix", "f32", "k", "n"),
                "c": value("matrix", "f32", "m", "n"),
                "alpha": value("scalar", "f32"),
                "beta": value("scalar", "f32"),
            },
            {"": value("matrix", "f32", "m", "n")},
        ),
        "batched_gemm": operation(
            {
                "a": value("tensor", "f32", "batch", "m", "k"),
                "b": value("tensor", "f32", "batch", "k", "n"),
            },
            {"": value("tensor", "f32", "batch", "m", "n")},
        ),
        "gemm_chain": operation(
            {
                "a": value("matrix", "f32", "m", "k"),
                "b": value("matrix", "f32", "k", "n"),
                "c": value("matrix", "f32", "n", "p"),
            },
            {"": value("matrix", "f32", "m", "p")},
        ),
    },
}

DEFAULT_FUNCTION = {"thrust": "sort", "arrayfire": "sort", "cutlass": "gemm"}


def max_chain_depth(value=None):
    try:
        configured = value if value is not None else os.environ.get("FUZZ3_MAX_CHAIN_DEPTH", 4)
        depth = int(configured)
    except (TypeError, ValueError) as error:
        raise ValueError("FUZZ3_MAX_CHAIN_DEPTH must be an integer") from error
    if not 1 <= depth <= 64:
        raise ValueError("FUZZ3_MAX_CHAIN_DEPTH must be between 1 and 64")
    return depth


def operations(request):
    if isinstance(request.get("operations"), list):
        return request["operations"]
    if isinstance(request.get("function"), str) and isinstance(request.get("inputs"), dict):
        return [{"id": "op0", "function": request["function"], "inputs": request["inputs"]}]
    return []


def _evaluate_shape(expression, dimensions):
    if expression == "?":
        return None

    def evaluate(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return node.value
        if isinstance(node, ast.Name):
            return dimensions[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in SHAPE_OPERATORS:
            left, right = evaluate(node.left), evaluate(node.right)
            return (
                None
                if left is None or right is None
                else SHAPE_OPERATORS[type(node.op)](left, right)
            )
        raise ValueError(f"unsupported shape expression: {expression}")

    return evaluate(ast.parse(expression, mode="eval").body)


def _matches(actual, expected, dimensions):
    if actual.kind != expected.kind or actual.dtype not in expected.dtypes:
        return False
    if len(actual.shape) != len(expected.shape):
        return False

    for expression, extent in zip(expected.shape, actual.shape):
        if expression == "?":
            continue
        if expression.isidentifier():
            if expression not in dimensions:
                dimensions[expression] = extent
                continue
            if dimensions[expression] != extent:
                return False
        elif _evaluate_shape(expression, dimensions) != extent:
            return False
    return True


def _concrete_type(spec, dimensions, dtype=None):
    return ValueType(
        spec.kind,
        dtype or random.choice(spec.dtypes),
        tuple(_evaluate_shape(part, dimensions) for part in spec.shape),
    )


def _output_types(spec, input_types, dimensions):
    return {
        path: input_types[output.input_name]
        if isinstance(output, SameAs)
        else _concrete_type(output, dimensions)
        for path, output in spec.outputs.items()
    }


def _literal(value_type):
    if value_type.kind == "scalar":
        if value_type.dtype == "bool":
            scalar = random.choice((False, True))
        elif value_type.dtype.startswith("i"):
            scalar = random.randint(-8, 8)
        else:
            scalar = random.choice((-2.0, -0.5, 0.5, 2.0))
        return {"type": "scalar", "dtype": value_type.dtype, "value": scalar}

    count = math.prod(value_type.shape)
    if value_type.dtype.startswith("i"):
        data = [random.randint(-8, 8) for _ in range(count)]
    else:
        data = [round(random.uniform(-10.0, 10.0), 4) for _ in range(count)]
    return {
        "type": value_type.kind,
        "dtype": value_type.dtype,
        "shape": list(value_type.shape),
        "data": data,
    }


def _safe_runtime_link(spec, dimensions):
    unknown = {name for name, extent in dimensions.items() if extent is None}
    return all(
        sum(name in input_spec.shape for input_spec in spec.inputs.values()) == 1
        for name in unknown
    )


def _compatible_links(spec, previous):
    links = []
    for path, output_type in (previous or {}).items():
        for input_name, input_spec in spec.inputs.items():
            dimensions = {}
            if (
                not input_spec.optional
                and _matches(output_type, input_spec, dimensions)
                and _safe_runtime_link(spec, dimensions)
            ):
                links.append((path, input_name, dimensions, output_type))
    return links


def _build_operation(library, function, index, previous, weird):
    spec = GRAMMARS[library][function]
    links = _compatible_links(spec, previous)
    if previous and not links:
        return None

    link = random.choice(links) if links else None
    dimensions = dict(link[2]) if link else {}
    extents = WEIRD_EXTENTS if weird else range(1, 11)
    for input_spec in spec.inputs.values():
        for name in input_spec.shape:
            if name.isidentifier() and name not in dimensions:
                dimensions[name] = random.choice(extents)

    inputs = {}
    input_types = {}
    for input_name, input_spec in spec.inputs.items():
        if input_spec.optional and random.choice((False, True)):
            continue
        linked = link and input_name == link[1]
        input_type = link[3] if linked else _concrete_type(input_spec, dimensions)
        input_types[input_name] = input_type
        if linked:
            reference = {"ref": f"op{index - 1}"}
            if link[0]:
                reference["path"] = link[0].split(".")
            inputs[input_name] = reference
        else:
            inputs[input_name] = _literal(input_type)

    operation_value = {"id": f"op{index}", "function": function, "inputs": inputs}
    return operation_value, _output_types(spec, input_types, dimensions)


def generate_program(library, functions=None, max_depth=1, *, sequence=None, weird=False):
    allowed = tuple(functions or GRAMMARS[library])
    depth = max_depth if sequence else random.randint(1, max_depth)
    prefix = tuple(sequence or ())
    program = []
    previous = None

    for index in range(depth):
        candidates = [prefix[index]] if index < len(prefix) else list(allowed)
        random.shuffle(candidates)
        built = None
        for function in candidates:
            built = _build_operation(library, function, index, previous, weird)
            if built is not None:
                break
        if built is None:
            break
        operation_value, previous = built
        program.append(operation_value)

    if len(program) == 1:
        first = program[0]
        return {
            "schema_version": 1,
            "library": library,
            "function": first["function"],
            "inputs": first["inputs"],
        }
    return {"schema_version": 2, "library": library, "operations": program}


def _literal_type(payload):
    if payload.get("type") == "scalar" and "value" in payload:
        return ValueType("scalar", payload.get("dtype"))
    shape, data = payload.get("shape"), payload.get("data")
    if not isinstance(shape, list) or not isinstance(data, list):
        return None
    if any(type(extent) is not int or extent < 0 for extent in shape):
        return None
    if math.prod(shape) != len(data):
        return None
    return ValueType(payload.get("type"), payload.get("dtype"), tuple(shape))


def validate_program(request):
    library = request.get("library")
    program = operations(request)
    if library not in GRAMMARS or not program:
        return False

    available = {}
    operation_ids = set()
    for index, operation_value in enumerate(program):
        function = operation_value.get("function")
        inputs = operation_value.get("inputs")
        if function not in GRAMMARS[library] or not isinstance(inputs, dict):
            return False

        spec = GRAMMARS[library][function]
        dimensions = {}
        input_types = {}
        for input_name, input_spec in spec.inputs.items():
            if input_name not in inputs:
                if input_spec.optional:
                    continue
                return False

            payload = inputs[input_name]
            if not isinstance(payload, dict):
                return False
            if isinstance(payload.get("ref"), str):
                path = ".".join(payload.get("path", []))
                input_type = available.get((payload["ref"], path))
            else:
                input_type = _literal_type(payload)
            if input_type is None or not _matches(input_type, input_spec, dimensions):
                return False
            input_types[input_name] = input_type

        operation_id = operation_value.get("id", f"op{index}")
        if not isinstance(operation_id, str) or operation_id in operation_ids:
            return False
        operation_ids.add(operation_id)
        for path, output_type in _output_types(spec, input_types, dimensions).items():
            available[(operation_id, path)] = output_type
    return True
