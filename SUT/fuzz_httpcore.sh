cd ..
python3 blackbox.py -i httpcore/seeds -o httpcore/out -c httpcore/crashes --executor httpcore_executor \
                    --mutators bit_flip delete_line duplicate_line delete_char duplicate_char crazy_indentation add_one_mixed_tokens \
                    --observers entropy_sliding_window_observer --oracles entropy_oracle --iterations 50000 > httpcode-output.50k.log 2>&1
