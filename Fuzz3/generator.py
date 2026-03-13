from pathlib import Path
import random

def olc_encode_generator(seedsno: int, outputfolder: Path, timeout: float) -> int:
    outputfolder.mkdir(parents=True, exist_ok=True)

    start = time.time()
    total = 0

    for i in range(seedsno):
        lat = random.randint(-90, 90)
        long = random.randint(-180, 180)

        seed_path = outputfolder / f"fuzz3_olc_{i}.seed"
        seed_path.write_text(f"{lat},{long}\n")

        total += 1

    return total
