#!/bin/bash

# Target folder (defaults to current directory)
TARGET_DIR="${1:-.}"

# Find ALL files (-type f) and process them one by one
find "$TARGET_DIR" -type f | while read -r file; do

    # Run clang-format. -i is for in-place.
    # 2>&1 captures both standard output and error messages.
    echo "[TEST] File: $file"
    ERROR_OUTPUT=$(/home/ubuntu/llvm-clang-1/llvm-install/usr/local/bin/clang-format --dry-run --Werror --sort-includes "$file" 2>&1)
    EXIT_CODE=$?

    cat -v $file | grep "@"
    EXIT_CODE_GREP=$?
    echo ">>>>>>>>> INFO: ${ERROR_OUTPUT: -120}"

    # Check for crash or error (exit code not 0)
    if [ $EXIT_CODE -ne 0 ] && [ $EXIT_CODE -ne 1 ] && [ $EXIT_CODE_GREP -ne 0 ]; then
        echo "------------------------------------------------"
        echo "[CRASH] File: $file"
        echo "Exit Code: $EXIT_CODE"
        echo "Error: $ERROR_OUTPUT"
	#cat | grep -B5 -A5 -e"Stack dump" -e"Segmentation fault" -e"Abort" -e"abort"
    fi
    echo "<<<<<<<<<<<<<<<<<<<<<< END"
    echo
done

echo "Finished scanning all files."
