#!/bin/bash
seed="${@: -1}"
compiler_cmd="${@:1:$#-1}"
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

echo ">> RUN $compiler_cmd -x c -w $seed"
$compiler_cmd -x c -w "$seed"
./a.out
