#!/usr/bin/env python3

from pathlib import Path
import argparse
import random
import shutil
import subprocess
import sys
import tempfile
import time
import os
import math

from collections import deque


# We need to add all imports needed for the fuzzing
import Fuzz3.executors
import Fuzz3.mutators
import Fuzz3.observers
import Fuzz3.oracles
import Fuzz3.generators

WINDOW_SIZE = int(os.environ.get("ENTROPY_WINDOW_SIZE", "1024"))
EPSILON = float(os.environ.get("EPSILON_SIZE", "0.05"))
MAX_CAPACITY = math.log2(WINDOW_SIZE)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input-dir", required=True)
    parser.add_argument("-o", "--output-dir", required=True)
    parser.add_argument("-c", "--crash-dir", required=True)

    # Post fuzzing - replay all seeds in input, output and crash folders
    parser.add_argument("-r", "--replay", type=float, default=0)

    # Main functinality: Fuzzing
    parser.add_argument("-t", "--timeout", type=float, default=50)
    parser.add_argument("-n", "--iterations", type=int, default=50)

    parser.add_argument("--executor", required=True)
    parser.add_argument("--executor-args", default="")

    parser.add_argument(
        "-g",
        "--generators",
        nargs="+",
        default=[],
        help="List of enabled generators methods",
    )
    parser.add_argument("-sn", "--seedsno", type=int, default=200)

    parser.add_argument(
        "-m",
        "--mutators",
        nargs="+",
        default=[],
        help="List of enabled mutator methods",
    )

    parser.add_argument(
        "--observers",
        nargs="+",
        default=[],
        help="List of enabled observer methods",
    )

    parser.add_argument(
        "--oracles",
        nargs="+",
        default=[],
        help="List of enabled oracles methods",
    )

    return parser.parse_args()


# Call:  python3 blackbox.py   -i clang-format-seeds   -o out   -c crashes   --executor "clang_format_executor"   --executor-args="--dry-run"
#  python3 blackbox.py   -i clang-format-seeds   -o out   -c crashes   --executor "clang_format_executor"   --executor-args "--dry-run --Werror"  --mutators bit_flip delete_line duplicate_line
# Main of the blackbox fuzzer
def main() -> int:
    # ================================================================
    #                        ---> ARGS <---
    # ================================================================

    print(">> (Fuzz3) Parsing input arguments")
    args = parse_args()

    print(">> (Fuzz3) Start")
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    crash_dir = Path(args.crash_dir)
    output_dir_end = Path(args.output_dir).with_name(
        Path(args.output_dir).name + "_end"
    )  # TO keep the queue not huge!

    # ================================================================
    #                        ---> REPLAY <---
    # ================================================================
    if args.replay:
        # REPLAY

        # Find our executor in the global space name
        func_name = args.executor  # This is a string
        arguments = args.executor_args  # This is a string
        func_to_run = getattr(Fuzz3.executors, func_name, None)

        executor = (
            func_to_run  # Now we can start using our target wrapper to fuzz the SUT
        )

        files = [p for p in input_dir.glob("*") if p.is_file()]
        if files:
            for seed in files:
                print(f">> (Fuzz3, Reply) {seed}")
                print(executor(arguments, seed, args.timeout))

        files = [p for p in output_dir.glob("*") if p.is_file()]
        if files:
            for seed in files:
                print(f">> (Fuzz3, Reply) {seed}")
                print(executor(arguments, seed, args.timeout))

        files = [p for p in crash_dir.glob("*") if p.is_file()]
        if files:
            for seed in files:
                print(f">> (Fuzz3, Reply) {seed}")
                print(executor(arguments, seed, args.timeout))

        return 0

    # ================================================================
    #                        ---> FUZZING <---
    # ================================================================
    results_map = (
        {}
    )  # Here we store all observations, including coverage information (if we have a coverage oracle)
    shutil.rmtree(output_dir, ignore_errors=True)
    shutil.rmtree(crash_dir, ignore_errors=True)

    output_dir.mkdir(parents=True, exist_ok=True)
    crash_dir.mkdir(parents=True, exist_ok=True)

    ############################################
    # Phase 1: collect and validate seeds once #
    ############################################
    if args.generators:
        generators = [
            getattr(Fuzz3.generators, n, None)
            for n in args.generators
            if getattr(Fuzz3.generators, n, None)
        ]
        for g in generators:
            total = g(args.seedsno, input_dir)
            print(f">> (Fuzz3) Generate {total} seeds into output folder")

    print(">> (Fuzz3) Copy good seeds into output folder")
    files = [p for p in input_dir.glob("*") if p.is_file()]
    if not files:
        print(f">> (Fuzz3) No Seeds found in {input_dir}/ folder. Exiting.")
        return 1

    # A file in the input dir that passed the executor with
    # return 0, into the output folder and else into the crash folder
    is_valid = False

    # Find our executor in the global space name
    func_name = args.executor  # This is a string
    arguments = args.executor_args  # This is a string
    func_to_run = getattr(Fuzz3.executors, func_name, None)
    if not func_to_run:
        print(f">> (Fuzz3) No executor found {func_to_run} for {func_name}")
        return 1

    # Build lists of fuzzing components
    mutators = [
        getattr(Fuzz3.mutators, n, None)
        for n in args.mutators
        if getattr(Fuzz3.mutators, n, None)
    ]
    observers = [
        getattr(Fuzz3.observers, n, None)
        for n in args.observers
        if getattr(Fuzz3.observers, n, None)
    ]
    oracles = [
        getattr(Fuzz3.oracles, n, None)
        for n in args.oracles
        if getattr(Fuzz3.oracles, n, None)
    ]
    executor = func_to_run  # Now we can start using our target wrapper to fuzz the SUT
    if not mutators:
        print(f">> (Fuzz3) No mutators list found from {args.mutators}")
        return 1

    init_stage_results = None
    for seed in files:
        _input, _rc, _out, _err = executor(arguments, seed, args.timeout)
        if _rc == 0:
            is_valid = True
            for observer in observers:
                _map_in, _map_out = observer(_input, (_rc, _out, _err))
                results_map[observer.__name__] = (_map_in, _map_out)
            for oracle in oracles:
                if oracle.__name__ == "entropy_oracle":
                    init_stage_results = oracle(
                        seed, results_map
                    )  # Just need the last ones!

            shutil.copy2(seed, output_dir / seed.name)
        else:
            shutil.copy2(seed, crash_dir / seed.name)

    if not is_valid or init_stage_results is None:
        print(">> (Fuzz3) No valid non-crashing seeds found. Exiting.")
        return 1

    # Check that we are not starting with entropy that is already off
    _ein, _eout, _edist, _en = init_stage_results
    if _ein < _eout + EPSILON:
        print(
            f">> (Fuzz3) Init. seeds are not good. Entropy in {_ein} is near entropy out {_eout}. Exiting."
        )
        return 1
    ################## If we got till here, the initial setup is sensible ##################

    ######################
    # Phase 2: fuzz loop #
    ######################
    result_entropy_prev = None
    deads = 0
    recent_active = deque(maxlen=WINDOW_SIZE)  # In case we stall, we
    print(">> (Fuzz3) Start Fuzzing")
    for _ in range(args.iterations):

        # Clean a bit if deads is high!
        if deads > 2 * MAX_CAPACITY:
            print(f">> (Fuzz3) Shaking the seeds after {deads} no interesting seeds.")
            # move 10% of files from output_dir to output_dir_end
            files = [f for f in output_dir.iterdir() if f.is_file()]
            n_to_move = max(1, math.ceil(0.1 * len(files)))  # at least 1 file
            selected = random.sample(files, n_to_move)
            for f in selected:
                dest = output_dir_end / f.name
                shutil.move(str(f), str(dest))
            deads = 0

            # Bring back cold seeds
            for f in [f for f in files if "_coldlist" in f.name]:
                if f.name not in recent_active:
                    new_name = f.with_name(f.name.replace("_coldlist", ""))
                    f.rename(new_name)
                    print(f">> (Fuzz3) Restored: {f.name} → {new_name.name}")
        ## END reducing the queue

        # After reducing the queue, continue with the next iteration of fuzzing
        files = [p for p in output_dir.glob("*") if p.is_file()]

        # Now we have a proper search
        weights = [
            (
                2.0
                if "interesting" in f.name
                else (
                    0.1 if "deadend" in f.name else 0.2 if "coldlist" in f.name else 1.0
                )
            )
            for f in files
        ]
        seed = random.choices(files, weights=weights, k=1)[0]
        recent_active.append(seed.name)

        print(f">> (Fuzz3) Fuzzing seed: {seed}")

        # Mutate
        mutator = random.choice(mutators)
        result = mutator(seed)
        if result is None:
            continue  # Mutation failed

        # Execute the mutated file
        tmp = tempfile.NamedTemporaryFile(delete=False)
        if isinstance(result, str):
            Path(tmp.name).write_text(result)
        else:
            Path(tmp.name).write_bytes(result)

        tmp_path = Path(tmp.name)
        name = f"fuzz3_{int(time.time_ns())}"

        _input, _rc, _out, _err = executor(arguments, tmp_path, args.timeout)
        #################### END Execution ####################

        # Running Oracle - third oracle using data from Observers
        # Here we will use _out and _err

        # Observers
        for observer in observers:
            _map_in, _map_out = observer(_input, (_rc, _out, _err))
            results_map[observer.__name__] = (_map_in, _map_out)

        # Oracles
        for oracle in oracles:
            results = oracle(tmp_path, results_map)
            print(results)  # Not sure yet what to do with it
            if oracle.__name__ == "entropy_oracle":
                if result_entropy_prev is not None:
                    _ein, _eout, _edist, _en = results
                    _prev_ein, _prev_eout, _prev_edist, _prev_en = result_entropy_prev
                    if _en == _prev_en:  # only if stable
                        if (_ein - _eout) > (MAX_CAPACITY - 10 * EPSILON):
                            name = name + "_deadend"
                            deads = deads + 1
                        elif _ein < EPSILON and _eout < EPSILON:
                            name = name + "_deadend"
                            deads = deads + 1
                        elif _eout == 0 or _eout < EPSILON:
                            name = name + "_interesting"
                            deads = 0
                        elif _ein > _prev_ein:
                            name = name + "_interesting"
                            deads = 0
                        elif _eout > _prev_eout:
                            name = name + "_interesting"
                            deads = 0
                        elif _en > _prev_en:
                            name = name + "_interesting"
                            deads = 0

                result_entropy_prev = results

        #################### ORACLE 1+2 #################### 
        ## In future work, this needs to be x2 observers and orcales
        ## CRASH+HANGS ORACLES ##
        # Now check where the seed needs to go
        if _rc == 0:
            print(f">> (Fuzz3) Writing to output dir {name}")
            shutil.copy2(tmp_path, output_dir / name)
        else:
            name_wt_rc = f"{name}-{_rc}" if _rc is not None else name
            print(f">> (Fuzz3) Writing to crash dir {name_wt_rc}")
            shutil.copy2(tmp_path, crash_dir / name_wt_rc)

            # If crashed and not in cold list, add parent
            if all(
                tag not in seed.name
                for tag in ["_coldlist", "_interesting", "_deadend"]
            ):
                print(f">> (Fuzz3) Moving parent to output dir cold list {seed}")
                new_name = seed.with_name(seed.name + "_coldlist")
                seed.rename(new_name)
                # Update recent_active deque (if there)
                try:
                    idx = recent_active.index(seed.name)
                    recent_active[idx] = new_name.name
                except ValueError:
                    # seed.name is not in recent_active; no need to update
                    pass
        #################### END ORACLE 1+2 ####################

        # Cleaning
        tmp_path.unlink(missing_ok=True)
        print(" ")


if __name__ == "__main__":
    raise SystemExit(main())
