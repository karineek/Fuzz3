#!/bin/bash
inseed=$1 # clang-format-seeds
out=$2    # out
crash=$3  # crashes
itr=$4    # 10000
python3 ../blackbox.py -i $inseed -o $out -c $crash \
        --executor "clang_format_executor" \
        --executor-args "--dry-run --Werror --sort-includes" \
        --mutators bit_flip delete_line duplicate_line crazy_indentation cmutation_assignment_expression_mutator cmutation_assignment_expression_mutator cmutation_duplicate_statement_mutator cmutation_jump_mutator cmutation_unary delete_char duplicate_char insert_block_comment \
        --observers entropy_sliding_window_observer --oracles entropy_oracle --iterations $itr
        