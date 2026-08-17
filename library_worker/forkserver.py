#!/usr/bin/env python3
import json
import math
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path


HARNESS_PATH = os.environ.get(
    "HARNESS_PATH", str(Path(__file__).resolve().with_name("native_harness"))
)
DEFAULT_TIMEOUT = float(os.environ.get("HARNESS_TIMEOUT_SEC", "5"))
MAX_TIMEOUT = float(os.environ.get("HARNESS_MAX_TIMEOUT_SEC", "30"))
MAX_REPETITIONS = int(os.environ.get("HARNESS_MAX_REPETITIONS", "64"))
MAX_REQUEST_BYTES = int(os.environ.get("HARNESS_MAX_REQUEST_BYTES", str(1 << 20)))


class InvalidRequest(ValueError):
    pass


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def shannon_entropy(histogram, total):
    if total == 0:
        return 0.0
    entropy = -sum(
        (count / total) * math.log2(count / total) for count in histogram.values()
    )
    return entropy if entropy else 0.0


def parse_request(payload):
    if len(payload.encode("utf-8")) > MAX_REQUEST_BYTES:
        raise InvalidRequest("request exceeds the byte limit")
    try:
        request = json.loads(payload)
    except json.JSONDecodeError as error:
        raise InvalidRequest(f"invalid JSON: {error.msg}") from error
    if not isinstance(request, dict):
        raise InvalidRequest("request must be an object")
    if request.get("command") == "describe":
        return request, 1, DEFAULT_TIMEOUT, True
    if not isinstance(request.get("function"), str):
        raise InvalidRequest("function must be a string")
    if not isinstance(request.get("inputs"), dict):
        raise InvalidRequest("inputs must be an object")

    controls = request.get("controls", {})
    if not isinstance(controls, dict):
        raise InvalidRequest("controls must be an object")
    repetitions = controls.get("repetitions", 1)
    if isinstance(repetitions, bool) or not isinstance(repetitions, int):
        raise InvalidRequest("controls.repetitions must be an integer")
    if repetitions < 1 or repetitions > MAX_REPETITIONS:
        raise InvalidRequest(
            f"controls.repetitions must be between 1 and {MAX_REPETITIONS}"
        )
    timeout = controls.get("timeout_sec", DEFAULT_TIMEOUT)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise InvalidRequest("controls.timeout_sec must be a number")
    if not math.isfinite(float(timeout)):
        raise InvalidRequest("controls.timeout_sec must be finite")
    if timeout <= 0 or timeout > MAX_TIMEOUT:
        raise InvalidRequest(
            f"controls.timeout_sec must be greater than 0 and at most {MAX_TIMEOUT}"
        )
    return request, repetitions, float(timeout), False


def failure(status, return_code, started, output, observations=None):
    histogram = Counter(observations or [])
    completed = sum(histogram.values())
    return {
        "status": status,
        "return_code": return_code,
        "runtime_sec": time.perf_counter() - started,
        "output": output,
        "completed_repetitions": completed,
        "unique_outputs": len(histogram),
        "entropy_bits": shannon_entropy(histogram, completed),
    }


def native_error(stderr):
    value = stderr.strip()
    if not value:
        return "native harness returned no error"
    try:
        return compact(json.loads(value))
    except json.JSONDecodeError:
        return value


def process_payload(payload):
    started = time.perf_counter()
    try:
        _, repetitions, timeout, describe = parse_request(payload)
    except InvalidRequest as error:
        return failure("invalid", 300, started, str(error))

    if describe:
        try:
            result = subprocess.run(
                [HARNESS_PATH, "--describe"],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return failure("hang", -1, started, "TIMEOUT")
        except OSError as error:
            return failure("crash", 127, started, str(error))
        if result.returncode != 0:
            return failure(
                "crash", result.returncode, started, native_error(result.stderr)
            )
        try:
            manifest = json.loads(result.stdout)
            output = compact(manifest)
        except (json.JSONDecodeError, ValueError) as error:
            return failure("crash", 1, started, f"invalid native manifest: {error}")
        response = failure("success", 0, started, output, [output])
        response["manifest"] = manifest
        return response

    observations = []
    native_results = []
    for _ in range(repetitions):
        try:
            result = subprocess.run(
                [HARNESS_PATH],
                input=payload,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return failure("hang", -1, started, "TIMEOUT", observations)
        except OSError as error:
            return failure("crash", 127, started, str(error), observations)

        if result.returncode == 2:
            return failure("invalid", 300, started, native_error(result.stderr), observations)
        if result.returncode != 0:
            return failure(
                "crash",
                result.returncode,
                started,
                native_error(result.stderr),
                observations,
            )
        try:
            native = json.loads(result.stdout)
            if not isinstance(native, dict) or "result" not in native:
                raise ValueError("response has no result")
            observation = compact(native["result"])
        except (json.JSONDecodeError, ValueError) as error:
            return failure(
                "crash", 1, started, f"invalid native response: {error}", observations
            )
        observations.append(observation)
        native_results.append(native)

    histogram = Counter(observations)
    if repetitions == 1:
        output = observations[0]
    else:
        samples = [
            {"count": count, "result": json.loads(observation)}
            for observation, count in sorted(histogram.items())
        ]
        output = compact({"samples": samples})
    response = failure("success", 0, started, output, observations)
    response["repetitions"] = repetitions
    response["observation_histogram"] = [
        {"count": count, "result": json.loads(observation)}
        for observation, count in sorted(histogram.items())
    ]
    if repetitions == 1:
        response["native_result"] = native_results[0]
    return response


def main():
    for line in sys.stdin:
        payload = line.strip()
        if payload:
            print(compact(process_payload(payload)), flush=True)


if __name__ == "__main__":
    main()
