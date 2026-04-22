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

## General executor
def script_executor(
    arguments: str, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
    try:
        code_in = seed.read_text(encoding="utf-8")
    except Exception as e:
        return "", 1, "", "Invalid (Fuzz3)"

    arg_parsed = shlex.split(arguments)
    cmd = [*arg_parsed, str(seed)]
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
    
    except Exception as e:
        return code_in, 123, "", f"Execution System Error: {str(e)}"

def httpcore_executor(
    arguments: str, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
    try:
        s = seed.read_text(encoding="utf-8").strip()
        url = str(s)
    except Exception as e:
        return "", 125, "", "Invalid (Fuzz3)"

    code = "import httpcore;" f"a= httpcore.request('GET', '{url}').status;" "print(a)"

    try:
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return url, r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        return url, 124, e.stdout or "", e.stderr or "timeout"        
    except Exception as e:
        return url, 123, "", f"System Error: {str(e)}"

## Target flaky_triangle (ok to use for triangle too) based on olc_encode_executor
def triangle_executor(
    arguments: str, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
    try:
        s = seed.read_text().strip()
        a, b, c = s.replace(",", " ").split()
    except Exception as e:
        return "", 1, "", "Invalid (Fuzz3)"

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


############################ Target: C compilers #############################
# See the readme of clang-format/ in Fuzz3 regarding how to run it
##############################################################################
def c_compiler_executor(
    arguments: str, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
    
    if (not seed):
        return "", 122, "", "Invalid Path"
    elif not seed.is_file():
       return "", 121, "", "Not a File"

    return script_executor(f"{arguments} -x c", seed, timeout) # All good, it is a file + it ends with .c

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

    return final_output.strip()

def clang_format_executor(
    arguments, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
    try:
        code_in = seed.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        return "", 125, "", "Invalid (Fuzz3)"

    arg_parsed = shlex.split(arguments)
    cmd = ["clang-format", *arg_parsed, str(seed)]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return code_in, result.returncode, output_formatter_clang_format(result.stdout.strip()), output_formatter_clang_format(result.stderr.strip()) 
            
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
        return "", 1, "", "Invalid (Fuzz3)"

    code = (
        "from openlocationcode import openlocationcode as olc;"
        f"print(olc.encode({lat},{lng}), end='')"
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
        return "", 1, "", "Invalid (Fuzz3)"

    code = (
        "from openlocationcode import openlocationcode as olc;"
        f'a=olc.decode("{code_in}");'
        "print(f'{a.latitudeCenter:.3f},{a.longitudeCenter:.3f}', end='')"
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
        return "", 1, "", "Invalid (Fuzz3)"

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
        return "", 1, "", "Invalid (Fuzz3)"

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
