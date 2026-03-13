#!/usr/bin/env python3

from pathlib import Path
import argparse
import random
import shutil
import subprocess
import sys
import tempfile
import time

# We need to add all imports needed for the fuzzing
import Fuzz3.executors
import Fuzz3.mutators
import Fuzz3.observers
import Fuzz3.oracles
import Fuzz3.generators

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
    print(">> (Fuzz3) Parsing input arguments")
    args = parse_args()

    print(">> (Fuzz3) Start")
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    crash_dir = Path(args.crash_dir)


    
    if (args.replay):
        # REPLAY

        # Find our executor in the gloabl space name
        func_name = args.executor  		# This is the string "greet"
        arguments = args.executor_args  	# This is the string "Alice"
        func_to_run = getattr(Fuzz3.executors, func_name, None)

        executor=func_to_run # Now we can start using our target wrapper to fuzz the SUT

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


    
    # FUZZING:
    shutil.rmtree(output_dir, ignore_errors=True) 
    shutil.rmtree(crash_dir, ignore_errors=True)

    output_dir.mkdir(parents=True, exist_ok=True)
    crash_dir.mkdir(parents=True, exist_ok=True)

    # Phase 1: collect and validate seeds once
    if args.generators:
        generators=[getattr(Fuzz3.generators,n,None) for n in args.generators if getattr(Fuzz3.generators,n,None)]
        for g in generators:
            total=g(args.seedsno, input_dir)
            print(f">> (Fuzz3) Generate {total} seeds into output folder")
    
    print(">> (Fuzz3) Copy good seeds into output folder")
    files = [p for p in input_dir.glob("*") if p.is_file()]
    if not files:
        print(f"No Seeds found in {input_dir}/ folder. Exiting.")
        return 1

    # An file in input dir that passed the executor with 
    # return 0, into output folder and else into crash folder
    is_valid = False

    # Find our executor in the gloabl space name
    func_name = args.executor  		# This is the string "greet"
    arguments = args.executor_args  	# This is the string "Alice"
    func_to_run = getattr(Fuzz3.executors, func_name, None)

    if not func_to_run:
        print(f"No executor found {func_to_run} for {func_name}")
        return 1

    executor=func_to_run # Now we can start using our target wrapper to fuzz the SUT
    for seed in files:
        if executor(arguments, seed, args.timeout)[1] == 0:
           shutil.copy2(seed, output_dir / seed.name)
           is_valid = True
        else:
           shutil.copy2(seed, crash_dir / seed.name)

    if not is_valid:
        print("No valid non-crashing seeds found. Exiting.")
        return 1

    # Build mutators list
    mutators=[getattr(Fuzz3.mutators,n,None) for n in args.mutators if getattr(Fuzz3.mutators,n,None)]
    observers=[getattr(Fuzz3.mutators,n,None) for n in args.observers if getattr(Fuzz3.observers,n,None)]
    oracles=[getattr(Fuzz3.mutators,n,None) for n in args.oracles if getattr(Fuzz3.oracles,n,None)]

    if not mutators:
       print(f"No mutators list found from {args.mutators}")
       return 1

    # Phase 2: fuzz loop
    results_map = {} # Here we store all observations, including coverage information (if we have a coverage oracle)
    print(">> (Fuzz3) Start Fuzzing")
    for _ in range(args.iterations):
        files = [p for p in output_dir.glob("*") if p.is_file()]
        seed = random.choice(files)
        print(f">> (Fuzz3) Fuzzing seed: {seed}")

        # Mutate
        mutator = random.choice(mutators)
        result = mutator(seed)

        #################### ORACLE 1+2 ####################
        ## CRASH+HANGS ORACLES ##
        # Execute the mutated file
        tmp = tempfile.NamedTemporaryFile(delete=False)
        if isinstance(result,str):
            Path(tmp.name).write_text(result)
        else:
            Path(tmp.name).write_bytes(result)

        tmp_path = Path(tmp.name)
        name = f"fuzz3_{int(time.time_ns())}"

        _input, _rc, _out, _err = executor(arguments, tmp_path, args.timeout)
        #################### END ORACLE 1+2 ####################

        # Running Oracle - third oracle using data from Observers
        # Here we will use _out and _err

        # Observers
        for observer in observers:
            _map = observer(_input, (_rc, _out, _err)) 
            results_map[observer.__name__] = _map

        # Oracles
        for oracle in oracles:
            result = oracle(tmp_path, results_map)
            print(result) # Not sure yet what to do with it

        # Now check where the seed needs to go
        if _rc == 0:
            print(f">> (Fuzz3) Writing to output dir {name}")
            shutil.copy2(tmp_path, output_dir / name)
        else:
            print(f">> (Fuzz3) Writing to crash dir {name}")
            shutil.copy2(tmp_path, crash_dir / name)

        # Cleaning
        tmp_path.unlink(missing_ok=True)

if __name__ == "__main__":
    raise SystemExit(main())
