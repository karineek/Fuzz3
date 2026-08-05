import importlib.util
import json
import math
import subprocess
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "forkserver.py"
SPEC = importlib.util.spec_from_file_location("gpu_forkserver", MODULE_PATH)
forkserver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(forkserver)


def request(repetitions=1):
    return json.dumps(
        {
            "function": "sort",
            "inputs": {
                "values": {
                    "type": "vector",
                    "dtype": "f32",
                    "shape": [2],
                    "data": [2, 1],
                }
            },
            "controls": {"repetitions": repetitions},
        }
    )


class ForkserverTests(unittest.TestCase):
    def test_rejects_malformed_request_as_invalid(self):
        response = forkserver.process_payload("not-json")
        self.assertEqual(response["status"], "invalid")
        self.assertEqual(response["return_code"], 300)

    @mock.patch.object(forkserver.subprocess, "run")
    def test_single_observation_is_canonical(self, run):
        run.return_value = subprocess.CompletedProcess(
            [], 0, '{"result":{"data":[1,2],"shape":[2]}}\n', ""
        )
        response = forkserver.process_payload(request())
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["output"], '{"data":[1,2],"shape":[2]}')
        self.assertEqual(response["entropy_bits"], 0.0)

    @mock.patch.object(forkserver.subprocess, "run")
    def test_repetitions_measure_nondeterminism(self, run):
        run.side_effect = [
            subprocess.CompletedProcess([], 0, '{"result":{"value":1}}', ""),
            subprocess.CompletedProcess([], 0, '{"result":{"value":2}}', ""),
        ]
        response = forkserver.process_payload(request(2))
        self.assertEqual(response["unique_outputs"], 2)
        self.assertTrue(math.isclose(response["entropy_bits"], 1.0))
        self.assertEqual(response["completed_repetitions"], 2)

    @mock.patch.object(forkserver.subprocess, "run")
    def test_native_input_errors_are_not_crashes(self, run):
        run.return_value = subprocess.CompletedProcess(
            [], 2, "", '{"error":"invalid_input","message":"bad shape"}'
        )
        response = forkserver.process_payload(request())
        self.assertEqual(response["status"], "invalid")
        self.assertEqual(response["return_code"], 300)

    def test_rejects_nonfinite_timeout_as_invalid(self):
        value = json.loads(request())
        value["controls"]["timeout_sec"] = float("nan")
        response = forkserver.process_payload(json.dumps(value))
        self.assertEqual(response["status"], "invalid")
        self.assertEqual(response["return_code"], 300)

    @mock.patch.object(forkserver.subprocess, "run")
    def test_describe_returns_manifest(self, run):
        run.return_value = subprocess.CompletedProcess(
            [], 0, '{"library":"thrust","functions":{}}', ""
        )
        response = forkserver.process_payload('{"command":"describe"}')
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["manifest"]["library"], "thrust")


if __name__ == "__main__":
    unittest.main()
