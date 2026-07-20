#WBL 15 Jun 2026 add olc_decoder_generator_corner

from pathlib import Path
import random
import subprocess
import sys


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

        seed_path = outputfolder / f"fuzz3_olce_legal_{i}.seed"
        seed_path.write_text(f"{lat},{long}")

        total += 1

    return total


def olc_encoder_generator_illegal(seedsno: int, outputfolder: Path) -> int:
    outputfolder.mkdir(parents=True, exist_ok=True)
    
    total = 0
    for i in range(seedsno):
        lat = random.randint(-1024, 1024)
        long = random.randint(-1024, 1024)

        seed_path = outputfolder / f"fuzz3_olce_illegal_{i}.seed"
        seed_path.write_text(f"{lat},{long}")

        total += 1

    return total

def _helper_gen_olc_code_semi_legal() -> str:
    alphabet = "123456789CFGHJMPQRVWX"
    
    total_length = random.randint(3, 18)  # must be at least 3 to allow split
    split_index = total_length // 2       # position of '+'
    
    left = "".join(random.choice(alphabet) for _ in range(split_index))
    right = "".join(random.choice(alphabet) for _ in range(total_length - split_index))
    
    return f"{left}+{right}"

def olc_decoder_generator_semi_legal(seedsno: int, outputfolder: Path) -> tuple[int, int]:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    for i in range(seedsno):
        ret = _helper_gen_olc_code_semi_legal() 
        seed_path = outputfolder / f"fuzz3_olcd_sm_{i}.seed"
        seed_path.write_text(f"{ret}")
        total += 1

    return total
    
def _helper_gen_olc_code() -> str:
    alphabet = "123456789CFGHJMPQRVWX+-?"
    length = random.randint(2, 25)

    # 9C5V2RP7+JVXH835 examplple
    return "".join(random.choice(alphabet) for _ in range(length))

def olc_decoder_generator_illegal(seedsno: int, outputfolder: Path) -> tuple[int, int]:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    for i in range(seedsno):
        ret = _helper_gen_olc_code() 
        seed_path = outputfolder / f"fuzz3_olcd_illegal_{i}.seed"
        seed_path.write_text(f"{ret}")
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
                timeout=50,
            )
            if r.returncode == 0:
                seed_path = outputfolder / f"fuzz3_olcd_legal_{i}.seed"
                seed_path.write_text(f"{r.stdout}")
                total += 1
            else:
                print(f"(Fuzz3:INFO) Failed to generate 1 seed {lat},{long} mapped to invalid seed. Skip.")
        except subprocess.TimeoutExpired as e:
            print(f"(Fuzz3:INFO) Failed to generate 1 seed {lat},{long} timed out. Skip.")

    return total

def olc_decoder_generator_corner(seedsno: int, outputfolder: Path) -> int:
    outputfolder.mkdir(parents=True, exist_ok=True)

    OLC_ALPHABET = "23456789CFGHJMPQRVWX"
    total = 0
    for lat in range(12):                    #southpole to northpole plus errors
        for long in range(len(OLC_ALPHABET)):#round equator plus errors
            seed_path = outputfolder / f"fuzz3_olcd_corner_{lat}_{long}.seed"
            text = OLC_ALPHABET[lat]+OLC_ALPHABET[long]+"222222+22"
            seed_path.write_text(f"{text}")
            total += 1

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
        seed_path = outputfolder / f"fuzz3_h3e_{i}.seed"
        seed_path.write_text(f"{ret}")
        total += 1

    return total
    
def h3_decoder_generator(seedsno: int, outputfolder: Path) -> tuple[int, int]:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    for i in range(seedsno):
        ret = _helper_gen_h3_index() 
        seed_path = outputfolder / f"fuzz3_h3d_{i}.seed"
        seed_path.write_text(f"{ret}")
        total += 1

    return total



################################ Target: GPU Utilities #######################
# Source code from TODO
##############################################################################

def sort_generator_legal(seedsno: int, outputfolder: Path) -> int:
    outputfolder.mkdir(parents=True, exist_ok=True)

    total = 0
    while total < seedsno: # finish the loop, no need to be precise +-5 seeds it is okay
        values_count = random.randint(1, 10)
        values = [
            round(random.uniform(-500.0, 500.0), 4)
            for _ in range(values_count)
        ]
        payload = ",".join(str(value) for value in values)
        seed_path = outputfolder / f"fuzz3_sort_legal_{total}.seed"
        seed_path.write_text(payload, encoding="utf-8")
        total += 1

        for lat in range(4): 
            shuffled = values.copy()
            random.shuffle(shuffled)
            payload = ",".join(str(value) for value in shuffled)
            seed_path = outputfolder / f"fuzz3_sort_legal_{total}.seed"
            seed_path.write_text(payload, encoding="utf-8") 
            total += 1
            
    return total
