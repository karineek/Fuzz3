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
