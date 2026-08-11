# WBL 22 March 2026 merge triangle_executor
from pathlib import Path
import subprocess
import shlex
import sys
import os
import resource

DOCKER_IMAGE = os.environ.get("DOCKER_IMAGE", "10c3cd4d4526")


def limit_memory():
    max_memory = 4 * 1024 * 1024 * 1024  # 4 GB
    resource.setrlimit(
        resource.RLIMIT_AS,
        (max_memory, max_memory),
    )
    
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
        #WBL 1 May 2026
        #input_data = seed.read_text(encoding="utf-8")
        input_data = seed.read_bytes().decode(encoding="utf-8")
    except Exception as e:
        print(f'Execption {e} seed {seed} Invalid (Fuzz3)')
        return "", 300, "", "Invalid (Fuzz3)"

    arg_parsed = shlex.split(arguments)
    cmd = [*arg_parsed, str(seed)]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            preexec_fn=limit_memory,
        )
        return input_data, result.returncode, result.stdout.strip(), result.stderr.strip()

    except subprocess.TimeoutExpired as e:
        return input_data, 124, (e.stdout or "").strip(), (e.stderr or "timeout").strip()

    except Exception as e:
        return input_data, 123, "", f"Execution System Error: {str(e)}"


## General executor of a script in a docker
def docker_executor(
    arguments: str, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
    try:
        input_data = seed.read_bytes().decode(encoding="utf-8")
    except Exception as e:
        print(f'Execption {e} seed {seed} Invalid (Fuzz3)')
        return "", 300, "", "Invalid (Fuzz3)"

    arg_parsed = shlex.split(arguments)
    shell_command = shlex.join([*arg_parsed, str(seed)])
    cmd = ["docker", "exec", "-it", DOCKER_IMAGE, "sh", "-lc", shell_command]
    ## E.g. docker exec -it 10c3cd4d4526 sh -lc 'python3 /opt/test_ollama.py'
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return input_data, result.returncode, result.stdout.strip(), result.stderr.strip()

    except subprocess.TimeoutExpired as e:
        return input_data, 124, (e.stdout or "").strip(), (e.stderr or "timeout").strip()

    except Exception as e:
        return input_data, 123, "", f"Execution System Error: {str(e)}"

# For SUT == httpcore
def httpcore_executor(
    arguments: str, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
    try:
        s = seed.read_text(encoding="utf-8").strip()
        url = str(s)
    except Exception as e:
        print(f'Execption {e} seed {seed} httpcore_executor Invalid (Fuzz3)')
        return "", 300, "", "Invalid (Fuzz3)"

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
        print(f'Execption {e} seed {seed} triangle_executo Invalid (Fuzz3)')
        return "", 300, "", "Invalid (Fuzz3)"

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
        print(f'Execption {e} seed {seed} Invalid Path')
        return "", 300, "", "Invalid Path"
    elif not seed.is_file():
        print(f'Execption {e} seed {seed} Not a File')
        return "", 300, "", "Not a File"

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
        print(f'Execption {e} seed {seed} clang_format_executor')
        return "", 300, "", "Invalid (Fuzz3)"

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
        print(f'Execption {e} seed {seed} olc_encode_executor Invalid (Fuzz3)')
        return "", 300, "", "Invalid (Fuzz3)"

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


#based on https://stackoverflow.com/questions/339537/end-line-characters-from-lines-read-from-text-file-using-python
def strip_trailing_newline(line):
    if line[-1] == '\n':
        return line[:-1]
    else:
        return line

# Target decode olc
def olc_decode_executor(
    arguments: str, seed: Path, timeout: float
) -> tuple[str, int, str, str]:
    try:
        #WBL 30 Apr 2026
        print(f'olc_decode_executor {seed}.read_bytes')
        #code_in = seed.read_text().strip()
        code_in1 = seed.read_bytes()
        #code_in = code_in1.removesuffix('\n')
        code_in2 = strip_trailing_newline(code_in1)
        code_in = code_in2.decode('utf-8').rstrip('\n')
        #code_in = code_in2.rstrip('\n')
        #print(f'code_in={code_in}')
    except Exception as e:
        print(f'Exception {e} seed {seed} olc_decode_executor')
        return "", 300, "", "Invalid (Fuzz3)"

    code = (
        "from openlocationcode import openlocationcode as olc;"
        #f'a=olc.decode("{code_in!r}");'
        f"a=olc.decode({code_in!r});"
        "print(f'{a.latitudeCenter:.3f},{a.longitudeCenter:.3f}', end='')"
    )
    
    try:
        print(f'olc_decode_executor try code={code}')
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        print(f'olc_decode_executor returncode={r.returncode} stdout={r.stdout} stderr={r.stderr}')
        return code_in, r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        print(f'Exception {e} seed {seed} olc_decode_executor TimeoutExpired')
        return code_in, 124, e.stdout or "", e.stderr or "timeout"
    except Exception as e:
        print(f'Exception {e} seed {seed} olc_decode_executor other')


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
        print(f'Execption {e} seed {seed} h3_encode_executor Invalid (Fuzz3)')
        return "", 300, "", "Invalid (Fuzz3)"

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
        print(f'Execption {e} seed {seed} h3_decode_executor Invalid (Fuzz3)')
        return "", 300, "", "Invalid (Fuzz3)"

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
