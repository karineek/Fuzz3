#!/bin/bash
inseed=$1 # httpcore/seeds
out=$2    # httpcore/out
crash=$3  # httpcore/crashes
python3 blackbox.py -i $inseed -o $out -c $crash --executor httpcore_executor -r 1 > httpcode-replay.log 2>&1
