#!/bin/bash
inseed=$1 # docker-in
out=$2    # out
crash=$3  # crashes
itr=$4    # 10000
python3 ../blackbox.py -i $inseed -o $out -c $crash \
        --executor docker_executor \
        --executor-args "python3 /opt/test_ollama.py" \
        --mutators none \
        --observers entropy_sliding_window_observer \
        --oracles entropy_oracle \
        --iterations $itr

