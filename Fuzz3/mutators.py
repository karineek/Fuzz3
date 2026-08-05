#WBL 15 Jun 2026 add flip_case_char and olc_short
#WBL 22 Apr 2026 bugfix delete_char
#WBL 21 Mar 2026 for triangle add: add_one sub_one equilateral isosceles (and none debug)
import json
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

def digit_block_to_same(seed: Path) -> str | None:
    digit = str(random.randint(0, 9))
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    start = random.randrange(len(data))
    length = random.randint(1, max(1, len(data) // 4))
    end = min(len(data), start + length)

    return "".join(
        digit if start <= i < end and ch.isdigit() else ch
        for i, ch in enumerate(data)
    )

# More OLC-specific mutators:
def plus_to_many_plus(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None
    return data.replace("+", "++")

def remove_plus(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data or "+" not in data:
        return None
    return data.replace("+", "")

def inject_invalid_olc_chars(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    invalids = "ILOilo!@#$%_"
    return "".join(random.choice(invalids) if ch.isalnum() else ch for ch in data)

def plus_left(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None
        
    pos = data.find("+")
    if pos <= 0:
        return None

    chars = list(data)
    chars[pos], chars[pos - 1] = chars[pos - 1], chars[pos]

    return "".join(chars)

def plus_right(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    pos = data.find("+")
    if pos == -1 or pos >= len(data) - 1:
        return None

    chars = list(data)
    chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]

    return "".join(chars)

##################################################
## Decoder Specific Mutators:
OLC_ALPHABET = "23456789CFGHJMPQRVWX"
def olc_random_char(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    chars = list(data)

    pos = random.randrange(len(chars))
    chars[pos] = random.choice(OLC_ALPHABET)

    return "".join(chars)

#remove area code (first 4 chars) to give short code
#WBL 15 Jun 2026 so far not useful
def olc_short(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    chars = list(data)
    if len(chars) > 7+4:
        return "".join(chars[4:])
    else:
        return None

def flip_case_char(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    chars = list(data)

    pos = random.randrange(len(chars))
    if chars[pos].islower():
        chars[pos] = chars[pos].upper()
    elif chars[pos].isupper():
        chars[pos] = chars[pos].lower()
    else: #no change
        return None

    return "".join(chars)

def olc_neighbour(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    pos = random.randrange(len(data))
    ch = data[pos].upper()

    if ch not in OLC_ALPHABET:
        return None

    idx = OLC_ALPHABET.index(ch)

    if idx == 0:
        new_ch = OLC_ALPHABET[idx + 1]
    elif idx == len(OLC_ALPHABET) - 1:
        new_ch = OLC_ALPHABET[idx - 1]
    elif random.choice([True, False]):
        new_ch = OLC_ALPHABET[idx + 1]
    else:
        new_ch = OLC_ALPHABET[idx - 1]

    if data[pos].islower():
        new_ch = new_ch.lower()

    return data[:pos] + new_ch + data[pos + 1:]

## End of Decoder Specific Mutators.
def _load_request(seed):
    try:
        request = json.loads(seed.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(request, dict) or not isinstance(request.get("inputs"), dict):
        return None
    return request


def _dump_request(request):
    return json.dumps(request, sort_keys=True, separators=(",", ":"), allow_nan=False)


def library_value_mutator(seed: Path) -> str | None:
    request = _load_request(seed)
    if request is None:
        return None
    candidates = []
    for payload in request["inputs"].values():
        if not isinstance(payload, dict):
            continue
        if payload.get("type") == "scalar" and isinstance(payload.get("value"), (bool, int, float)):
            candidates.append((payload, "value", payload.get("dtype")))
        data = payload.get("data")
        if isinstance(data, list):
            candidates.extend((data, index, payload.get("dtype")) for index in range(len(data)))
    if not candidates:
        return None

    container, key, dtype = random.choice(candidates)
    value = container[key]
    if dtype == "bool" and isinstance(value, bool):
        container[key] = not value
    elif dtype in ("i32", "i64") and isinstance(value, (int, float)):
        limits = (-2**31, 2**31 - 1) if dtype == "i32" else (-2**63, 2**63 - 1)
        delta = random.choice((-1, 1))
        candidate = int(value) + delta
        if candidate < limits[0] or candidate > limits[1]:
            candidate = int(value) - delta
        container[key] = candidate
    elif dtype in ("f32", "f64") and isinstance(value, (int, float)):
        numeric = float(value)
        container[key] = 1.0 if numeric == 0.0 else -numeric
    else:
        return None
    return _dump_request(request)


def library_shuffle_mutator(seed: Path) -> str | None:
    request = _load_request(seed)
    if request is None:
        return None
    candidates = []
    for payload in request["inputs"].values():
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            continue
        data = payload["data"]
        if len(data) > 1 and any(value != data[0] for value in data[1:]):
            candidates.append(data)
    if not candidates:
        return None
    data = random.choice(candidates)
    first = random.randrange(len(data))
    different = [index for index, value in enumerate(data) if value != data[first]]
    if not different:
        return None
    second = random.choice(different)
    data[first], data[second] = data[second], data[first]
    return _dump_request(request)


def library_resize_mutator(seed: Path) -> str | None:
    request = _load_request(seed)
    if request is None:
        return None
    inputs = request["inputs"]
    paired = {
        "stable_sort_by_key": ("keys", "values"),
        "reduce_by_key": ("keys", "values"),
        "transform_axpby": ("x", "y"),
    }.get(request.get("function"))
    groups = [paired] if paired else [
        (name,) for name, payload in inputs.items()
        if isinstance(payload, dict) and payload.get("type") == "vector"
    ]
    eligible = []
    for group in groups:
        if not group or any(name not in inputs for name in group):
            continue
        payloads = [inputs[name] for name in group]
        if all(
            payload.get("type") == "vector"
            and isinstance(payload.get("shape"), list)
            and len(payload["shape"]) == 1
            and isinstance(payload.get("data"), list)
            and payload["shape"][0] == len(payload["data"])
            and payload["data"]
            for payload in payloads
        ) and len({len(payload["data"]) for payload in payloads}) == 1:
            eligible.append(payloads)
    if not eligible:
        return None

    payloads = random.choice(eligible)
    size = len(payloads[0]["data"])
    grow = size == 1 or random.choice((False, True))
    index = random.randrange(size)
    for payload in payloads:
        if grow:
            payload["data"].insert(index, payload["data"][index])
        else:
            payload["data"].pop(index)
        payload["shape"][0] = len(payload["data"])
    return _dump_request(request)


def library_worker_mutator(seed: Path) -> str | None:
    mutators = [library_value_mutator, library_shuffle_mutator, library_resize_mutator]
    random.shuffle(mutators)
    for mutator in mutators:
        result = mutator(seed)
        if result is not None:
            return result
    return None
