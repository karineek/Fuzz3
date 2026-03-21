#WBL 21 Mar 2026 for triangle add: add_one sub_one equilateral isosceles (and none debug)
import random
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

def none(seed: Path) -> bytes | None:
    data = seed.read_bytes()
    if not data:
        return None

    b = bytearray(data)
    return bytes(b)


#randomly increase one side of seed by 1
def add_one(seed: Path) -> str | None:
    data = seed.read_text(errors="ignore")
    if not data:
        return None

    words = data.split()
    i = random.randrange(len(words))
    words[i] = str(int(words[i]) + 1)
    return " ".join(words)

#randomly reduce one side of seed by 1
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
