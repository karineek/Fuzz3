#WBL 22 Apr 2026 bugfix delete_char
#WBL 21 Mar 2026 for triangle add: add_one sub_one equilateral isosceles (and none debug)
import random
import re
from pathlib import Path
import tempfile
import shutil
import subprocess
from pathlib import Path
import os
import string

GRAYC_PATH = os.getenv("GRAYC", "~/GrayC/build/bin/grayc")
GRAYC = os.path.expanduser(GRAYC_PATH)
# GRAYC = os.path.expanduser("~/GrayC/build/bin/grayc")
timeout = 50

## HELPER function, do not call it directly
def __grayc_mutators(seed: Path, mutator) -> str | None:
    if not seed.exists() or not seed.is_file():
        return None

    suffix = seed.suffix or ".c"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / f"input{suffix}"
        shutil.copy2(seed, tmp_path)

        cmd = [
            GRAYC,
            mutator,
            "--mutate",
            "--apply-mutation",
            str(tmp_path),
            "--",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            data = tmp_path.read_text(errors="ignore")
            if not data:
                return None

            return data

        except subprocess.TimeoutExpired as e:
            return None

def cmutation_assignment_expression_mutator(seed: Path) -> str | None:
    return __grayc_mutators(seed, '-mutations="-*,cmutation-assignment-expression-mutator"')

def cmutation_conditional_expression_mutator(seed: Path) -> str | None:
    return __grayc_mutators(seed, '-mutations="-*,cmutation-conditional-expression-mutator"')

def cmutation_duplicate_statement_mutator(seed: Path) -> str | None:
    return __grayc_mutators(seed, '-mutations="-*,cmutation-duplicate-statement-mutator"')

def cmutation_jump_mutator(seed: Path) -> str | None:
    return __grayc_mutators(seed, '-mutations="-*,cmutation-jump-mutator"')

def cmutation_unary(seed: Path) -> str | None:
    return __grayc_mutators(seed, '-mutations="-*,cmutation-unary"')


#def bit_flip(seed: Path) -> str | None:
#    data = seed.read_bytes()
#    if not data:
#        return None
#
#    b = bytearray(data)
#    i = random.randrange(len(b))
#    bit = 1 << random.randrange(8)
#    b[i] ^= bit
#    res = bytes(b).decode(encoding="utf-8")
#
#    return res


def bit_flip(seed: Path) -> str | None:
    data = seed.read_bytes()
    if not data:
        return None

    b = bytearray(data)
    i = random.randrange(len(b))
    bit = 1 << random.randrange(8)
    b[i] ^= bit

    try:
        return bytes(b).decode(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def delete_line(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    lines = data.splitlines()
    if not lines:
        return None

    i = random.randrange(len(lines))
    del lines[i]
    return "\n".join(lines)

def delete_char(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    l = len(data)
    i = random.randrange(l)
    assert i >= 0 and i < l
    return data[:i] + data[i+1:]

def duplicate_line(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    lines = data.splitlines()
    if not lines:
        return None

    i = random.randrange(len(lines))
    lines.insert(i, lines[i])
    return "\n".join(lines)

def duplicate_char(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    char_to_add = random.choice(data) 
    i = random.randrange(len(data) + 1) # +1 allows adding at the very end
    return data[:i] + char_to_add + data[i:]
    

def crazy_indentation(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None
    s = list(data)
    n = len(s)

    # how many mutations to apply
    num_mutations = max(1, int(n * random.uniform(0.005, 0.03)))
    # What we can mutate here:
    whitespace = [" ", "\t", "\n", "\r\n"]
    punct = list("{}()[];")

    # Mutate
    for _ in range(num_mutations):
        if not s:
            break
        op = random.random()
        i = random.randrange(len(s))

        if op < 0.5:
            ws = random.choice(whitespace)
            s[i:i] = list(ws)

        elif op < 0.7:
            if s[i].isspace():
                del s[i]

        elif op < 0.9:
            s.insert(i, random.choice(punct))

    return "".join(s)

def insert_block_comment(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    size = random.randrange(15) + 4
    chars=string.ascii_uppercase + string.digits
    random_text = ''.join(random.choice(chars) for _ in range(size))
    comment = f"/* TODO: {random_text} */"
    lines = data.splitlines()
    if not lines:
        return None
    i = random.randrange(len(lines))
    lines.insert(i, comment)
    return "\n".join(lines)

def none(seed: Path) -> bytes | None:
    data = seed.read_bytes()
    if not data:
        return None

    b = bytearray(data)
    return bytes(b)


#randomly increase one side of the seed by 1
def add_one(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    words = data.split()
    i = random.randrange(len(words))
    words[i] = str(int(words[i]) + 1)
    return " ".join(words)

def add_one_mixed_tokens(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    matches = list(re.finditer(r"-?\d+", data))
    if not matches:
        return None

    ## NOTE: these 5 lines were debugged with ChatGPT (Thinking 5.4)
    ## 27-03-2026 based on add_one which had an issue where
    ## it fails on non-numeric tokens.
    m = random.choice(matches)
    old_value = m.group(0)
    new_value = str(int(old_value) + 1)

    return data[:m.start()] + new_value + data[m.end():]

#randomly reduce one side of the seed by 1
def sub_one(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    words = data.split()
    i = random.randrange(len(words))
    words[i] = str(int(words[i]) - 1)
    return " ".join(words)

#Try to convert seed to equilateral triangle
def equilateral(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    words = data.split()
    total = sum(map(int,words))
    out = int((total+2)/3)
    return f"{out} {out} {out}"

#Try to randomly convert seed to isosceles triangle
def isosceles(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    words = data.split()
    i = random.randrange(len(words))
    num = map(int,words)
    old = words[i];
    words[i] = "0";
    total = sum(map(int,words))
    side = str(int((total+1)/2))
    ans = ""
    for k in range(0,3):
        #print(f"i={i} k={k} ans={ans}.")
        if k==i:
            ans += old
        else:
            ans += side
        if k<2:
            ans += " "

    #print(f"isosceles data={data} i={i} total={total} ans={ans}.")
    return ans

# Adding YarpGEN style constant mutators
def digits_to_same(seed: Path) -> str | None:
    digit = str(random.randint(0, 9))
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    return "".join(
        digit if ch.isdigit() else ch
        for ch in data
    )

def digits_lower_half_to_same(seed: Path) -> str | None:
    digit = str(random.randint(0, 9))
    data = seed.read_text(errors="ignore")
    if not data:
        return None
        
    midpoint = len(data) // 2
    return "".join(
        digit if i < midpoint and ch.isdigit() else ch
        for i, ch in enumerate(data)
    )

def digits_upper_half_to_same(seed: Path) -> str | None:
    digit = str(random.randint(0, 9))
    data = seed.read_text(errors="ignore")
    if not data:
        return None
        
    midpoint = len(data) // 2
    return "".join(
        digit if i >= midpoint and ch.isdigit() else ch
        for i, ch in enumerate(data)
    )
