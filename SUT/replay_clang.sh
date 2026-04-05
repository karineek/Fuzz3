#!/bin/bash
inseed=$1 # clang-format-seeds
out=$2    # out
crash=$3  # crashes
SUT=$4    # /home/ubuntu/llvm-clang-1/llvm-install/usr/local/bin/clang-23
python3 ../blackbox.py -i $inseed -o $out -c $crash \
        --executor script_executor \
        --executor-args \
                "./C-compiler-AND-Utils/script-compile-and-run.sh $SUT -Wjump-misses-init -w -O3 -I /usr/include/x86_64-linux-gnu/ -I /usr/local/include/ -lcsmith" \
        -r 1 --replay-executors script_executor script_executor \
        --replay-executors-args \
                "./C-compiler-AND-Utils/script-compile-and-run.sh gcc -Wjump-misses-init -w -O3 -I /usr/include/x86_64-linux-gnu/ -I /usr/local/include/ -lcsmith" \
                "./C-compiler-AND-Utils/script-compile-and-run.sh clang -Wjump-misses-init -w -O3 -I /usr/include/x86_64-linux-gnu/ -I /usr/local/include/ -lcsmith"
