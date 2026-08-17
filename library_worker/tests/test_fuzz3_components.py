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
from Fuzz3.mutators import (
    library_resize_mutator,
    library_shuffle_mutator,
    library_value_mutator,
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
                os.environ, {"FUZZ3_LIBRARY": "thrust", "FUZZ3_FUNCTION": "sort"}
            ):
                count = library_worker_generator(7, Path(directory))
            seeds = sorted(Path(directory).glob("*.json"))
            requests = [json.loads(seed.read_text(encoding="utf-8")) for seed in seeds]

        self.assertEqual(count, 7)
        self.assertEqual(len(requests), 7)
        for request in requests:
            self.assertEqual(request["library"], "thrust")
            self.assertEqual(request["function"], "sort")
            values = request["inputs"]["values"]
            self.assertEqual(values["shape"][0], len(values["data"]))


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
            "function": "transform_axpby",
            "inputs": {
                "x": {"type": "vector", "dtype": "f32", "shape": [2], "data": [1, 2]},
                "y": {"type": "vector", "dtype": "f32", "shape": [2], "data": [3, 4]},
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


if __name__ == "__main__":
    unittest.main()
