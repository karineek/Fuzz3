input=$1
logs=$2
for file in $input/*_interesting; do
  /home/ubuntu/llvm-clang-2/llvm-install/usr/local/bin/clang -x c "$file" -w -O3 -o a1.out
  timeout 10s ./a1.out > out1.txt 2>&1

  clang -x c "$file" -w -O3 -o a1.out
  timeout 10s ./a1.out > out2.txt 2>&1

  echo -n "."
  # compare and print only if different
  if ! diff -q out1.txt out2.txt >/dev/null; then
    echo "DIFF in $file"
    diff out1.txt out2.txt
    echo "=============================="
  fi

done > $logs 2>&1 &
