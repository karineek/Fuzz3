# What does this folder contain?

This is a target to fuzz. We have a list of seeds, some of which are invalid, leading to an error message, which leads to high entropy.

```
clang-format --dry-run <in.c> >> output.c
```
OR
```
cp in.c out.c
clang-format <out.c> 
```
