#!/bin/bash
inseed=$1 # clang-format-seeds
out=$2    # out
crash=$3  # crashes
itr=$4    # 10000
python3 ../blackbox.py -i $inseed -o $out -c $crash \
        --executor script_executor \
        --executor-args "./Cirq/script.sh" \
        --mutators none \
        --observers entropy_sliding_window_observer \
        --oracles entropy_oracle \
        --iterations $itr  
        