from pathlib import Path
import random


def olc_encoder_generator_legal(seedsno: int, outputfolder: Path) -> int:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    for i in range(seedsno):
        lat = random.randint(-90, 90)
        long = random.randint(-180, 180)

        seed_path = outputfolder / f"fuzz3_olc_{i}.seed"
        seed_path.write_text(f"{lat},{long}\n")

        total += 1

    return total


def olc_encoder_generator_illegal(seedsno: int, outputfolder: Path) -> int:
    for i in range(seedsno):
        lat = random.randint(-1024, 1024)
        long = random.randint(-1024, 1024)

        seed_path = outputfolder / f"fuzz3_olc_{i}.seed"
        seed_path.write_text(f"{lat},{long}\n")

        total += 1

    return total


def olc_decoder_generator(seedsno: int, outputfolder: Path) -> tuple[int, int]:
    pass
