from pathlib import Path
import random
import subprocess


################################ Target: OLC #################################
# Source code from https://github.com/google/open-location-code.
# See the readme of Fuzz3 regarding how to install it
##############################################################################

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
    outputfolder.mkdir(parents=True, exist_ok=True)
    
    total = 0
    for i in range(seedsno):
        lat = random.randint(-1024, 1024)
        long = random.randint(-1024, 1024)

        seed_path = outputfolder / f"fuzz3_olc_{i}.seed"
        seed_path.write_text(f"{lat},{long}\n")

        total += 1

    return total

def _helper_gen_olc_code() -> str:
    alphabet = "23456789CFGHJMPQRVWX"
    length = random.randint(2, 15)

    return "".join(random.choice(alphabet) for _ in range(length))

def olc_decoder_generator_illegal(seedsno: int, outputfolder: Path) -> tuple[int, int]:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    for i in range(seedsno):
        ret = _helper_gen_olc_code() 
        seed_path = outputfolder / f"fuzz3_olc_{i}.seed"
        seed_path.write_text(f"{ret}\n")
        total += 1

    return total


def olc_decoder_generator_legal(seedsno: int, outputfolder: Path) -> int:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    for i in range(seedsno):
        lat = random.randint(-90, 90)
        long = random.randint(-180, 180)

        # Then encode it, and we get legal decoder seeds!
        code = (
            "from openlocationcode import openlocationcode as olc;"
            f"print(olc.encode({lat},{long}))"
        )

        try:
            r = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if r.returncode == 0:
                seed_path = outputfolder / f"fuzz3_olc_{i}.seed"
                seed_path.write_text(f"{r.stdou}\n")
                total += 1
            else:
                print(f"(Fuzz3:INFO) Failed to generate 1 seed {lat},{long} mapped to invalid seed. Skip.")
        except subprocess.TimeoutExpired as e:
            print(f"(Fuzz3:INFO) Failed to generate 1 seed {lat},{long} timed out. Skip.")

    return total


################################# Target: H3 #################################
# Source code from https://github.com/uber/h3.
# See the readme of Fuzz3 regarding how to install it
##############################################################################

def _helper_gen_h3_encode_seed() -> str:
    lat = random.uniform(-90, 90)
    lng = random.uniform(-180, 180)
    res = 10
    return f"{lat},{lng},{res}"

def _helper_gen_h3_index() -> str:
    value = random.getrandbits(64)
    return f"{value:016x}"

def h3_encoder_generator(seedsno: int, outputfolder: Path) -> tuple[int, int]:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    for i in range(seedsno):
        ret = _helper_gen_h3_encode_seed() 
        seed_path = outputfolder / f"fuzz3_olc_{i}.seed"
        seed_path.write_text(f"{ret}\n")
        total += 1

    return total
    
def h3_decoder_generator(seedsno: int, outputfolder: Path) -> tuple[int, int]:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    for i in range(seedsno):
        ret = _helper_gen_h3_index() 
        seed_path = outputfolder / f"fuzz3_olc_{i}.seed"
        seed_path.write_text(f"{ret}\n")
        total += 1

    return total


