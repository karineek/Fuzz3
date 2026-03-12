from pathlib import Path
import subprocess
import shlex

def dummy_executor(arguments :str, seed: Path) -> int:
    print(f"Running on {seed} with args {arguments}")
    return 0

def clang_format_executor(arguments, seed: Path) -> int:
    arg_parsed = shlex.split(arguments)
    cmd = ["clang-format", *arg_parsed, str(seed)]
    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode
