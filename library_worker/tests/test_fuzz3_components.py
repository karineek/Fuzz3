import json
import os
import random
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from Fuzz3.executors import docker_executor
from Fuzz3.generators import library_worker_generator
from Fuzz3.library_grammar import operations, validate_program
from Fuzz3.mutators import (
    library_resize_mutator,
    library_shuffle_mutator,
    library_subnormal_mutator,
    library_value_mutator,
    library_weird_shape_mutator,
)


class DockerExecutorTests(unittest.TestCase):
    @mock.patch("Fuzz3.executors.subprocess.run")
    def test_streams_request_without_a_tty(self, run):
        run.return_value = subprocess.CompletedProcess(
            [], 0, '{"return_code":0,"output":"ok"}\n', ""
        )
        with tempfile.TemporaryDirectory() as directory:
            seed = Path(directory) / "seed.json"
            seed.write_text('{"function":"sort","inputs":{}}', encoding="utf-8")
            with mock.patch.dict(os.environ, {"DOCKER_CONTAINER": "cpu-worker"}):
                result = docker_executor("", seed, 3)

        self.assertEqual(result[1:3], (0, "ok"))
        command = run.call_args.args[0]
        self.assertEqual(command[:4], ["docker", "exec", "-i", "cpu-worker"])
        self.assertEqual(command[4:], ["python3", "-u", "/fuzz_workspace/forkserver.py"])
        self.assertTrue(run.call_args.kwargs["input"].endswith("\n"))

    @mock.patch("Fuzz3.executors.subprocess.run")
    def test_preserves_application_return_code(self, run):
        run.return_value = subprocess.CompletedProcess(
            [], 0, '{"return_code":300,"output":"invalid"}', ""
        )
        with tempfile.TemporaryDirectory() as directory:
            seed = Path(directory) / "seed.json"
            seed.write_text("{}", encoding="utf-8")
            result = docker_executor("worker", seed, 3)
        self.assertEqual(result[1:3], (300, "invalid"))


class GeneratorTests(unittest.TestCase):
    def test_generates_structured_thrust_requests(self):
        random.seed(7)
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.dict(
                os.environ, {"FUZZ3_LIBRARY": "thrust", "FUZZ3_FUNCTION": "sort",
                             "FUZZ3_MAX_CHAIN_DEPTH": "3"}
            ):
                count = library_worker_generator(7, Path(directory))
            seeds = sorted(Path(directory).glob("*.json"))
            requests = [json.loads(seed.read_text(encoding="utf-8")) for seed in seeds]

        self.assertEqual(count, 7)
        self.assertEqual(len(requests), 7)
        for request in requests:
            self.assertEqual(request["library"], "thrust")
            self.assertTrue(validate_program(request))
            self.assertLessEqual(len(operations(request)), 3)
            self.assertTrue(all(op["function"] == "sort" for op in operations(request)))
            values = operations(request)[0]["inputs"]["values"]
            self.assertEqual(values["shape"][0], len(values["data"]))

    def test_generates_typed_result_references(self):
        random.seed(19)
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.dict(os.environ, {"FUZZ3_LIBRARY": "arrayfire",
                                              "FUZZ3_FUNCTION": "sort,reduce_sum",
                                              "FUZZ3_MAX_CHAIN_DEPTH": "4"}):
                library_worker_generator(20, Path(directory))
            requests = [json.loads(path.read_text()) for path in Path(directory).glob("*.json")]
        self.assertTrue(all(validate_program(request) for request in requests))
        self.assertTrue(any(
            isinstance(value, dict) and "ref" in value
            for request in requests for op in operations(request)
            for value in op["inputs"].values()
        ))


class MutatorTests(unittest.TestCase):
    def write_seed(self, directory, request):
        seed = Path(directory) / "seed.json"
        seed.write_text(json.dumps(request), encoding="utf-8")
        return seed

    def test_value_and_shuffle_preserve_json(self):
        request = {
            "function": "sort",
            "inputs": {
                "values": {
                    "type": "vector",
                    "dtype": "f32",
                    "shape": [3],
                    "data": [1, 2, 3],
                }
            },
        }
        random.seed(3)
        with tempfile.TemporaryDirectory() as directory:
            seed = self.write_seed(directory, request)
            value = json.loads(library_value_mutator(seed))
            shuffled = json.loads(library_shuffle_mutator(seed))
        self.assertEqual(value["inputs"]["values"]["shape"], [3])
        self.assertEqual(sorted(shuffled["inputs"]["values"]["data"]), [1, 2, 3])

    def test_resize_keeps_paired_vectors_aligned(self):
        request = {
            "library": "thrust",
            "function": "transform_axpby",
            "inputs": {
                "x": {"type": "vector", "dtype": "f32", "shape": [2], "data": [1, 2]},
                "y": {"type": "vector", "dtype": "f32", "shape": [2], "data": [3, 4]},
                "alpha": {"type": "scalar", "dtype": "f32", "value": 1},
                "beta": {"type": "scalar", "dtype": "f32", "value": 1},
            },
        }
        random.seed(5)
        with tempfile.TemporaryDirectory() as directory:
            seed = self.write_seed(directory, request)
            result = json.loads(library_resize_mutator(seed))
        self.assertEqual(result["inputs"]["x"]["shape"], result["inputs"]["y"]["shape"])
        self.assertEqual(
            len(result["inputs"]["x"]["data"]), len(result["inputs"]["y"]["data"])
        )

    def test_subnormal_and_weird_shape_mutations_remain_valid(self):
        request = {
            "schema_version": 1, "library": "arrayfire", "function": "matmul",
            "inputs": {
                "a": {"type": "matrix", "dtype": "f32", "shape": [2, 2], "data": [1, 2, 3, 4]},
                "b": {"type": "matrix", "dtype": "f32", "shape": [2, 2], "data": [5, 6, 7, 8]},
            },
        }
        random.seed(23)
        with tempfile.TemporaryDirectory() as directory:
            seed = self.write_seed(directory, request)
            subnormal = json.loads(library_subnormal_mutator(seed))
            weird = json.loads(library_weird_shape_mutator(seed))
        self.assertTrue(validate_program(subnormal))
        self.assertTrue(validate_program(weird))
        floats = [value for payload in subnormal["inputs"].values() for value in payload["data"]]
        self.assertTrue(any(0.0 < abs(value) < 2 ** -126 for value in floats))
        shapes = [size for payload in weird["inputs"].values() for size in payload["shape"]]
        self.assertTrue(all(size in (1, 3, 5, 7, 9, 15, 17, 31, 33) for size in shapes))


if __name__ == "__main__":
    unittest.main()
