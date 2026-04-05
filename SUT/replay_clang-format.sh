#!/bin/bash
inseed=$1 # clang-format-seeds
out=$2    # out
crash=$3  # crashes
python3 ../blackbox.py -i $inseed -o $out -c $crash \
        --executor "clang_format_executor" \
        --executor-args "--dry-run --Werror --sort-includes" \
         -r 1