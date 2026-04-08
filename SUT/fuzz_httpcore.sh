#!/bin/bash
inseed=$1 # httpcore/seeds
out=$2    # httpcore/out
crash=$3  # httpcore/crashes
itr=$4    # 10000
# This SUT needs a window of 800 instead of 1024
python3 blackbox.py -i $inseed -o $out -c $crash --executor httpcore_executor \
                    --mutators bit_flip delete_line duplicate_line delete_char duplicate_char crazy_indentation add_one_mixed_tokens \
                    --observers entropy_sliding_window_observer --oracles entropy_oracle --iterations $itr > httpcode-output.$itr.log 2>&1
