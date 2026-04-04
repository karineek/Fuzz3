# What does this folder contain?

It shall contain a set of seeds to fuzz in *.C or other supported format for clang-format. It can also be used to fuzz C compilers.


This is a target to fuzz. We have a list of seeds, some of which are invalid, leading to an error message, which leads to high entropy.

```
clang-format --dry-run <in.c> >> output.c
```
OR
```
cp in.c out.c
clang-format <out.c> 
```

# Fuzzing C compilers with Fuzz3 mutators and GrayC mutators

Get Csmith: (Taken from: https://github.com/csmith-project/csmith)
```
git clone https://github.com/csmith-project/csmith.git
cd csmith/
mkdir build
cd build
sudo apt install g++ cmake m4
cmake ../
make
sudo make install
```

Then install GrayC: (with Clang-17)
```
git clone https://github.com/dakaidan/GrayC.git
sudo apt-get update
sudo apt-get install -y llvm-17 llvm-17-dev llvm-17-tools clang-17 libclang-common-17-dev libclang-17-dev 
```
This builds both LLVM and Clang on Ubuntu

```
cd GrayC
mkdir build
cd build
cmake -GNinja -DCMAKE_C_COMPILER=clang-17 -DCMAKE_CXX_COMPILER=clang++-17 -DLLVM_CONFIG_BINARY=llvm-config-17 ../
ninja
```
You can edit the path of GRAYC via the Fuzz3 parameter. Just do ```setenv GRAYC </custom/path/to/grayc>``` before running this Fuzz3.

Then run the compiler you wish to test from H-Fuzz$ folder, like this:
```
python3 blackbox.py -i clang-format-seeds -o out -c crashes --executor c_compiler_executor --executor-args "clang -O3 -w -I /usr/include/x86_64-linux-gnu/ -I /usr/local/include/" --mutators bit_flip delete_line duplicate_line crazy_indentation cmutation_assignment_expression_mutator cmutation_assignment_expression_mutator cmutation_duplicate_statement_mutator cmutation_jump_mutator cmutation_unary delete_char duplicate_char insert_block_comment --observers entropy_sliding_window_observer --oracles entropy_oracle --iterations 2000 
```
