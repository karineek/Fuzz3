## Install:
```
sudo apt update
sudo apt install texlive-latex-extra texlive-fonts-recommended texlive-latex-recommended
./setup-cirq.sh
```

## Fuzz:

To run with none mutator

```
python3 blackbox.py \
   -i Cirq/in \
   -o Cirq/out \
   -c Cirq/crashes \
   --executor script_executor \
   --executor-args "./Cirq/script.sh" \
   --mutators none \
   --observers entropy_sliding_window_observer \
   --oracles entropy_oracle \
   --iterations 1000
>> (Fuzz3) Parsing input arguments
>> (Fuzz3) Start
>> (Fuzz3) Copy good seeds into output folder
....
```

