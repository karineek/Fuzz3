#!/bin/bash
inseed=$1 # clang-format-seeds
out=$2    # out
crash=$3  # crashes
python3 ../blackbox.py -i $inseed -o $out -c $crash \
        --executor script_executor \
        --executor-args "./Cirq/script.sh" \
        --replay 1
        
