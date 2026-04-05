#!/bin/bash
inseed=$1 # clang-format-seeds
out=$2    # out
crash=$3  # crashes
SUT=$4    # /home/ubuntu/llvm-clang-1/llvm-install/usr/local/bin/clang-23
itr=$5    # 10000
python3 ../blackbox.py -i $inseed -o $out -c $crash \
        --executor c_compiler_executor \
        --executor-args "$SUT -Wjump-misses-init -pedantic -Wall -Wextra -O3 -I /usr/include/x86_64-linux-gnu/ -I /usr/local/include/ -lcsmith" \
        --mutators bit_flip delete_line duplicate_line crazy_indentation cmutation_assignment_expression_mutator cmutation_assignment_expression_mutator cmutation_duplicate_statement_mutator cmutation_jump_mutator cmutation_unary delete_char duplicate_char insert_block_comment \
        --observers entropy_sliding_window_observer --oracles entropy_oracle --iterations $5
