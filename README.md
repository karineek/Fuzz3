# Fuzz3

EntFuzz is a fuzzer extension that uses entropy on input/output of a SUT to guide exploration.

## Demo Repositories

- Google OLC Open location code (Plus codes): https://github.com/google/open-location-code

  previously with OLC I tried resolution 1,2,3,4..15
  and 2000 samples drawn from GB post codes open_postcode_geo.csv.gz


  
- Uber's H3 A Hexagonal Hierarchical Geospatial Indexing System: https://github.com/uber/h3
  
- The data directory has the locations (lat,long) from 
   https://www.getthedata.com/downloads/open_postcode_geo.csv.zip
  (3 august 2022)
  
  Perhaps to break OLC or H3 we will need to test edge cases, eg North or South Pole, invalid regions, numbers bigger/smaller than 360, positionns very close to valid places, linear interpolation between valid places.

Code: https://github.com/google/open-location-code 

## Evaluation

**0. flaky_triangle:**
   
   Run it
   (note all files in ```out_tri``` and ```crashes_tri``` will be deleted) 
   with:
```
python3 blackbox.py	\
  -i tri/seeds_encoder/	\
  -o out_tri	\
  -c crashes_tri	\
  --executor triangle_executor	\
  --mutators add_one sub_one equilateral isosceles	\
  --observers entropy_observer	\
  --oracles entropy_oracle	\
  --iterations 1000
```
Can add ```--replay 1``` and blackbox.py will re-run all the input, output and crash seeds. 

**1. Clang-fuzzer:**
   
   Run it with:
   ```
python3 blackbox.py   -i clang-format-seeds   -o out   -c crashes   --executor "clang_format_executor"   --executor-args "--dry-run --Werror"  --mutators bit_flip delete_line duplicate_line --observers entropy_observer --oracles entropy_oracle --iterations 400
   ```
Other flags to try:  --verbose, --sort-includes:
```
python3 blackbox.py -i clang-format-seeds -o out -c crashes --executor "clang_format_executor" --executor-args "--dry-run --Werror --verbose --sort-includes" --mutators bit_flip delete_line duplicate_line crazy_indentation --observers entropy_observer --oracles entropy_sliding_window_observer --iterations 2000
```


   Replay all seeds:
   ```
python3 blackbox.py   -i clang-format-seeds   -o out   -c crashes   --executor "clang_format_executor"   --executor-args "--dry-run --Werror"  --mutators bit_flip delete_line duplicate_line --observers entropy_observer --oracles entropy_oracle --iterations 400 --replay 1
   ```
   
**1.1 missing clang-format**

If you get an error similar to 
```
File "...subprocess.py", in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'clang-format'
```
ensure clang-format is installed.

**2. OLC**
   
   Run it with:
   ```
python3 blackbox.py   -i OLC/seeds_encoder/   -o out_olc   -c crashes_olc   --executor olc_encode_executor  --mutators bit_flip --generators olc_encoder_generator_legal olc_encoder_generator_illegal --observers entropy_observer --oracles entropy_oracle

python3 blackbox.py   -i OLC/seeds_decoder/   -o out_olc_d   -c crashes_olc_d   --executor "olc_decode_executor"  --mutators bit_flip --generators olc_decode_generator --observers entropy_observer --oracles entropy_oracle
   ```

Possible output:
```
>> (Fuzz3) Fuzzing seed: out_olc/fuzz3_olc_162.seed
(7.302306551868582, 7.5820459851906, 207, 242)
>> (Fuzz3) Writing to crash dir fuzz3_1773937800538520095
 
>> (Fuzz3) Fuzzing seed: out_olc/fuzz3_olc_155.seed
(7.310793088510061, 7.589381330748454, 208, 243)
>> (Fuzz3) Writing to output dir fuzz3_1773937800541461205
 
>> (Fuzz3) Fuzzing seed: out_olc/fuzz3_olc_167.seed
(7.319234395479836, 7.596680882627089, 209, 244)
>> (Fuzz3) Writing to output dir fuzz3_1773937800578597227
 
>> (Fuzz3) Fuzzing seed: out_olc/fuzz3_olc_0.seed
(7.301617181361808, 7.603944979801258, 210, 245)
>> (Fuzz3) Writing to crash dir fuzz3_1773937800605264933
 
>> (Fuzz3) Fuzzing seed: out_olc/fuzz3_olc_34.seed
(7.283977919973422, 7.611173956541192, 211, 246)
>> (Fuzz3) Writing to crash dir fuzz3_1773937800608207135
 
>> (Fuzz3) Fuzzing seed: out_olc/fuzz3_olc_1.seed
(7.266322673127904, 7.61836814249836, 212, 247)
>> (Fuzz3) Writing to crash dir fuzz3_1773937800611328752
 
>> (Fuzz3) Fuzzing seed: out_olc/fuzz3_olc_112.seed
(7.248657049892898, 7.625527862788801, 213, 248)
>> (Fuzz3) Writing to crash dir fuzz3_1773937800614272558
 
>> (Fuzz3) Fuzzing seed: out_olc/fuzz3_olc_103.seed
(7.249264034066028, 7.6246213095607445, 213, 249)
>> (Fuzz3) Writing to output dir fuzz3_1773937800617236001
 
>> (Fuzz3) Fuzzing seed: out_olc/fuzz3_olc_144.seed
(7.231684662289803, 7.631745184644791, 214, 250)
>> (Fuzz3) Writing to crash dir fuzz3_1773937800651496053
 
>> (Fuzz3) Fuzzing seed: out_olc/fuzz3_olc_74.seed
(7.240368631269197, 7.630867159511216, 214, 251)
>> (Fuzz3) Writing to output dir fuzz3_1773937800654448745
 
>> (Fuzz3) Fuzzing seed: out_olc/fuzz3_olc_176.seed
(7.249006488606776, 7.637955419514501, 215, 252)
>> (Fuzz3) Writing to output dir fuzz3_1773937800690675614
```

   Replay all seeds:
   ```
python3 blackbox.py   -i OLC/seeds_encoder/   -o out_olc   -c crashes_olc   --executor olc_encode_executor  --mutators bit_flip --generators olc_encoder_generator_legal olc_encoder_generator_illegal --observers entropy_observer --oracles entropy_oracle --replay 1

python3 blackbox.py   -i OLC/seeds_decoder/   -o out_olc_d   -c crashes_olc_d   --executor "olc_decode_executor"  --mutators bit_flip --generators olc_decode_generator --observers entropy_observer --oracles entropy_oracle -r 1
   ```

Possible output:
```
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800272130400
('', 1, '', "'utf-8' codec can't decode byte 0xb6 in position 0: invalid start byte")
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800344085087
('', 1, '', 'not enough values to unpack (expected 2, got 1)')
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800538520095
('', 1, '', "could not convert string to float: '/374'")
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800283388869
('', 1, '', "could not convert string to float: '-12*'")
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800286245704
('', 1, '', "could not convert string to float: '104J'")
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800335576250
('', 1, '', "could not convert string to float: '1t4'")
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800166236828
('', 1, '', "'utf-8' codec can't decode byte 0xb7 in position 5: invalid start byte")
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800160602449
('', 1, '', 'not enough values to unpack (expected 2, got 1)')
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800605264933
('', 1, '', "could not convert string to float: '7;1'")
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800338415351
('', 1, '', 'not enough values to unpack (expected 2, got 1)')
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800422869621
('', 1, '', 'not enough values to unpack (expected 2, got 1)')
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800349775981
('', 1, '', "could not convert string to float: '>'")
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800346927784
('', 1, '', "could not convert string to float: '60&'")
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800355499498
('', 1, '', "could not convert string to float: '/841'")
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800459078505
('', 1, '', "could not convert string to float: '7v6'")
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800118451681
('', 1, '', "could not convert string to float: '-75\\x14'")
>> (Fuzz3, Reply) crashes_olc/fuzz3_1773937800352570739
('', 1, '', 'not enough values to unpack (expected 2, got 1)')
```
   
   
**3. H3**

   Run it with:
   ```
python3 blackbox.py   -i h3/seeds_encoder/   -o out_h3   -c crashes_h3   --executor h3_encode_executor  --mutators bit_flip --generators h3_encode_generator --observers entropy_observer --oracles entropy_oracle

python3 blackbox.py   -i h3/seeds_decoder/   -o out_h3_d   -c crashes_h3_d   --executor "h3_decode_executor"  --mutators bit_flip --generators h3_decode_generator --observers entropy_observer --oracles entropy_oracle
   ```

   Replay all seeds:
   ```
python3 blackbox.py   -i h3/seeds_encoder/   -o out_h3   -c crashes_h3   --executor h3_encode_executor  --mutators bit_flip --generators h3_encode_generator --observers entropy_observer --oracles entropy_oracle --replay 1

python3 blackbox.py   -i h3/seeds_decoder/   -o out_h3_d   -c crashes_h3_d   --executor "h3_decode_executor"  --mutators bit_flip --generators h3_decode_generator --observers entropy_observer --oracles entropy_oracle -r 1
   ```

   

## Evaluation at Scale

We will use FuzzBench:
- https://google.github.io/fuzzbench/

- Reported bug (confirmed): https://github.com/llvm/llvm-project/issues/188500


## Replay Seeds

```--replay 1``` is a command-line flag used when running blackbox.py in this project to re-run previously generated test cases (seeds) instead of creating new ones. 

Unlike the fuzzing campaign, where the tool mutates inputs and discovers new behaviours or crashes, saving those inputs in output (out_*) or crash (crashes_*) folders, when you add ```--replay 1```, the fuzzer switches into a replay mode where it takes those saved inputs and executes them again through the target program. This is mainly useful for verifying results, reproducing crashes, or analysing how the system behaves on known inputs without continuing the fuzzing process.

TODO: We should consider adding *.CSV output to this stage once we know which graphs can support the findings presenation.

## TODO

- Karine add more targets and seeds.
- Karine add more projects.
- Phil is doing the link up with the sliding window. 
- Janine is modifying one_step to separate the mutator, executor and entropy calculation functions
- ok lets call it fuzz3 (since HFuzz name used at ICSE last year (2025) https://conf.researchr.org/details/icse-2025/sbft-2025-papers/13/HFuzz-Havoc-Mode-Guided-Fuzzing )

## Emails
* Phil: p.mcminn@sheffield.ac.uk
* Janine: janine.obiri.25@ucl.ac.uk
* j.petke@ucl.ac.uk,
* karine.even_mendoza@kcl.ac.uk,
* <strike> "dif": Thanatad Songpetchmongkol <thanatad.songpetchmongkol.22@ucl.ac.uk>,</strike>
* w.langdon@cs.ucl.ac.uk
