from pathlib import Path
import subprocess
import shlex
import sys

# List here all the SUTs

## Dummy target
def dummy_executor(arguments :str, seed: Path, timeout: float) -> tuple[str, int, str, str]:
    print(f"Running on {seed} with args {arguments}")
    return "TEST", 0, "TEST", "TEST"

## Target Clang-format
def clang_format_executor(arguments, seed: Path, timeout: float) -> tuple[str, int, str, str]:
    code_in = seed.read_text().strip()
    arg_parsed = shlex.split(arguments)
    cmd = ["clang-format", *arg_parsed, str(seed)]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return code_in, result.returncode, result.stdout.strip(), result.stderr.strip()

    except subprocess.TimeoutExpired as e:
            return code_in, 124, (e.stdout or "").strip(), (e.stderr or "timeout").strip()

## Target OLC
def olc_encode_executor(arguments :str, seed: Path, timeout: float) -> tuple[str, int, str, str]:
    try:
        s = seed.read_text().strip()
        a, b = s.replace(",", " ").split()[:2]
        lat = float(a)
        lng = float(b)
    except Exception as e:
        return "", 1, "", str(e)

    code = (
        "from openlocationcode import openlocationcode as olc;"
        f"print(olc.encode({lat},{lng}))"
    )

    try:
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return s, r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        return s, 124, e.stdout or "", e.stderr or "timeout"


# Target decode olc
def olc_decode_executor(arguments :str, seed: Path, timeout: float) -> tuple[str, int, str, str]:
    try:
        code_in = seed.read_text().strip()
    except Exception as e:
        return "", 1, "", str(e)

    code = (
        "from openlocationcode import openlocationcode as olc;"
        f'a=olc.decode("{code_in}");'
        "print(a.latitudeCenter,a.longitudeCenter)"
    )

    try:
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return code_in, r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        return code_in, 124, e.stdout or "", e.stderr or "timeout"
