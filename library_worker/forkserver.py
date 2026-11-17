#!/usr/bin/env python3
import fcntl
import json
import math
import os
import signal
import socket
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
MAX_CHAIN_DEPTH = int(os.environ.get("FUZZ3_MAX_CHAIN_DEPTH", "4"))
# Must match how native_harness was compiled (set together by the Docker
# EXEC_MODE build arg): exec | forkserver | persistent.
EXEC_MODE = os.environ.get("FUZZ3_EXEC_MODE", "exec")
SOCKET_PATH = os.environ.get("FUZZ3_SOCKET", "/tmp/fuzz3-native.sock")
SERVER_PID_PATH = SOCKET_PATH + ".pid"
SERVER_LOG_PATH = SOCKET_PATH + ".log"
SUPERVISOR_LOCK_PATH = SOCKET_PATH + ".lock"
SERVER_START_TIMEOUT = float(os.environ.get("FUZZ3_SERVER_START_TIMEOUT_SEC", "60"))


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


def validate_program(request):
    if "operations" not in request:
        if not isinstance(request.get("function"), str):
            raise InvalidRequest("function must be a string")
        if not isinstance(request.get("inputs"), dict):
            raise InvalidRequest("inputs must be an object")
        return

    operations = request["operations"]
    if not isinstance(operations, list) or not operations:
        raise InvalidRequest("operations must be a non-empty array")
    if len(operations) > MAX_CHAIN_DEPTH:
        raise InvalidRequest(f"operations cannot exceed {MAX_CHAIN_DEPTH}")
    if any(
        not isinstance(operation, dict)
        or not isinstance(operation.get("function"), str)
        or not isinstance(operation.get("inputs"), dict)
        for operation in operations
    ):
        raise InvalidRequest("each operation needs a function and inputs object")


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
    validate_program(request)

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


def server_connect(timeout):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(timeout)
    try:
        client.connect(SOCKET_PATH)
    except OSError:
        client.close()
        raise
    return client


def supervise():
    """Keep one `native_harness --serve` alive for the container's lifetime."""
    lock = open(SUPERVISOR_LOCK_PATH, "a")
    try:
        # Held until this supervisor dies: guarantees a single supervisor.
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.exit(0)
    restarts = 0
    with open(SERVER_LOG_PATH, "a", buffering=1) as log:
        while True:
            server = subprocess.Popen(
                [HARNESS_PATH, "--serve"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=log,
                start_new_session=True,  # own process group, so hangs can be killed
            )
            Path(SERVER_PID_PATH).write_text(str(server.pid))
            code = server.wait()
            restarts += 1
            log.write(f"[{time.ctime()}] {EXEC_MODE} server exited {code}; restart #{restarts}\n")
            time.sleep(0.1)


def ensure_server():
    """Start the supervisor if none is running, then wait for the socket."""
    with open(SUPERVISOR_LOCK_PATH, "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            pass  # a supervisor holds the lock; its server may be restarting
        else:
            fcntl.flock(lock, fcntl.LOCK_UN)
            subprocess.Popen(
                [sys.executable, "-u", str(Path(__file__).resolve()), "--supervise"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
    deadline = time.monotonic() + SERVER_START_TIMEOUT
    while time.monotonic() < deadline:
        try:
            server_connect(1).close()
            return
        except OSError:
            time.sleep(0.05)
    raise OSError(f"native {EXEC_MODE} server did not start on {SOCKET_PATH}")


def kill_server():
    """Kill the server's process group; the supervisor restarts it."""
    try:
        os.killpg(int(Path(SERVER_PID_PATH).read_text()), signal.SIGKILL)
    except (OSError, ValueError):
        pass


def run_native(payload, timeout):
    if EXEC_MODE == "exec":
        return subprocess.run(
            [HARNESS_PATH],
            input=payload,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    # A reset/refused connection means the server never read this request
    # (it is restarting, or a crashed one is still dumping core), so the input
    # is not to blame: wait for the supervisor's replacement and retry.
    deadline = time.monotonic() + SERVER_START_TIMEOUT
    while True:
        try:
            with server_connect(timeout) as client:
                client.sendall(payload.encode("utf-8") + b"\n")
                data = b""
                while True:
                    chunk = client.recv(65536)
                    if not chunk:
                        break
                    data += chunk
            break
        except socket.timeout:
            kill_server()
            raise subprocess.TimeoutExpired([HARNESS_PATH, "--serve"], timeout)
        except (FileNotFoundError, ConnectionRefusedError):
            if time.monotonic() > deadline:
                raise
            ensure_server()
        except (ConnectionResetError, BrokenPipeError):
            if time.monotonic() > deadline:
                raise
            time.sleep(0.05)

    lines = [line for line in data.decode("utf-8", "replace").splitlines() if line]
    if not lines:
        # Persistent mode: the request took the whole server down.
        return subprocess.CompletedProcess(
            [], -signal.SIGKILL, "", "native server died during the request"
        )
    try:
        envelope = json.loads(lines[-1])
        return subprocess.CompletedProcess(
            [], envelope["return_code"], envelope["stdout"], envelope["stderr"]
        )
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        return subprocess.CompletedProcess(
            [], 1, "", f"invalid native server response: {error}"
        )


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
            result = run_native(payload, timeout)
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
    if sys.argv[1:] == ["--supervise"]:
        supervise()
    for line in sys.stdin:
        payload = line.strip()
        if payload:
            print(compact(process_payload(payload)), flush=True)


if __name__ == "__main__":
    main()
