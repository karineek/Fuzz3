# WBL 22 March 2026 merge triangle_executor
from pathlib import Path
import subprocess
import shlex
import sys

# List here all the SUTs


## Dummy target
def dummy_executor(
    arguments: str, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
    print(f"Running on {seed} with args {arguments}")
    return "TEST", 0, "TEST", "TEST"


def httpcore_executor(
    arguments: str, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
    try:
        s = seed.read_text().strip()
        url = str(s.replace(",", " ").split()[2])
    except Exception as e:
        return e

    code = "import httpcore;" f'print(httpcore.request("GET", "{url}")).status;'

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


## Target flaky_triangle (ok to use for triangle too) based on olc_encode_executor
def triangle_executor(
    arguments: str, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
    try:
        s = seed.read_text().strip()
        a, b, c = s.replace(",", " ").split()
        # a, b = s.replace(",", " ").split()[:2]
        # lat = float(a)
        # lng = float(b)
    except Exception as e:
        return "", 1, "", str(e)

    cmd = ["flaky_triangle", a, b, c]

    # print(f"subprocess.run({cmd},True,True,timeout={timeout},)")
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return s, r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        return s, 124, e.stdout or "", e.stderr or "timeout"


############################ Target: Clang Format #############################
# Install via the LLVM project, or via apt install
# See the readme of Fuzz3 regarding how to install it
##############################################################################
def output_formatter_clang_format(in_text :str):
    commands = [
        'grep -vF "^" | grep -ve "fuzz3" | grep -vF ".c:" | uniq',
        "grep -e 'fuzz3_' | cut -d'[' -f2 | uniq",
        "grep -F '.c:' | cut -d'[' -f2 | uniq"  
    ]

    final_output = ""
    for cmd in commands:
        result = subprocess.run(
            cmd,
            shell=True,
            input=in_text,
            text=True,
            capture_output=True
        )
        # Add the output of each command to our final string
        if result.stdout:
            final_output += result.stdout

    print(final_output)
    return final_output.strip()

def clang_format_executor(
    arguments, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
    try:
        code_in = seed.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError as e:
        return "", 125, "", f"input decode error: {e}"

    arg_parsed = shlex.split(arguments)
    cmd = ["clang-format", *arg_parsed, str(seed)]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        rc = 0 if result.returncode in [0, 1] else result.returncode
        ## print(f">>>> (executors) is {result.returncode} with RC is {rc}")
        return code_in, rc, output_formatter_clang_format(result.stdout.strip()), output_formatter_clang_format(result.stderr.strip()) 
            
    except subprocess.TimeoutExpired as e:
        return code_in, 124, (e.stdout or "").strip(), (e.stderr or "timeout").strip()


################################ Target: OLC #################################
# Source code from https://github.com/google/open-location-code.
# See the readme of Fuzz3 regarding how to install it
##############################################################################
## Target OLC
def olc_encode_executor(
    arguments: str, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
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
def olc_decode_executor(
    arguments: str, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
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


################################# Target: H3 #################################
# Source code from https://github.com/uber/h3.
# See the readme of Fuzz3 regarding how to install it
##############################################################################
def h3_encode_executor(
    arguments: str, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
    try:
        s = seed.read_text().strip()
        parts = s.replace(",", " ").split()
        lat = float(parts[0])
        lng = float(parts[1])
        res = int(arguments) if arguments else 10
    except Exception as e:
        return "", 1, "", str(e)

    code = "import h3;" f"print(h3.latlng_to_cell({lat},{lng},{res}))"

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


def h3_decode_executor(
    arguments: str, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
    try:
        h3_index = seed.read_text().strip()
    except Exception as e:
        return "", 1, "", str(e)

    code = (
        "import h3;"
        f"b=h3.cell_to_boundary('{h3_index}');"
        "print('\\n'.join(f'{lat} {lng}' for lat,lng in b))"
    )

    try:
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return h3_index, r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        return h3_index, 124, e.stdout or "", e.stderr or "timeout"
