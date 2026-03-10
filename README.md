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

## Evaluation at Scale

We will use FuzzBench:
- https://google.github.io/fuzzbench/


## TODO

- Karine add more targets and seeds.
- Karine add more projects.
- Phil is doing the link up with the sliding window. 
- Janine is modifying one_step to separate the mutator, executor and entropy calculation functions
- Everyone new name: HFuzz name used at ICSE last year (2025) https://conf.researchr.org/details/icse-2025/sbft-2025-papers/13/HFuzz-Havoc-Mode-Guided-Fuzzing
- What about Fuzz3 ????

## Emails
* Phil: p.mcminn@sheffield.ac.uk
* Janine: janine.obiri.25@ucl.ac.uk
* j.petke@ucl.ac.uk,
* karine.even_mendoza@kcl.ac.uk,
* <strike> "dif": Thanatad Songpetchmongkol <thanatad.songpetchmongkol.22@ucl.ac.uk>,</strike>
* w.langdon@cs.ucl.ac.uk
