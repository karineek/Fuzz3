#WBL 21 Mar 2026 for triangle add: add_one sub_one equilateral isosceles (and none debug)
import random
import re
from pathlib import Path

def bit_flip(seed: Path) -> bytes | None:
    data = seed.read_bytes()
    if not data:
        return None

    b = bytearray(data)
    i = random.randrange(len(b))
    bit = 1 << random.randrange(8)
    b[i] ^= bit
    return bytes(b)


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
