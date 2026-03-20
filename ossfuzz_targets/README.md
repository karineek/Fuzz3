# Google Fuzzing Targets

This directory contains scripts to pull, build, and fetch Google OSS-Fuzz seed corpora.

## Selected Targets:
1. **zlib**
2. **fastjson**
3. **jsoncpp**

## Workflow:
1. `./pull_targets.sh` - Clones the target repositories.
2. `./build_targets.sh [--instrument]` - Builds the targets. Pass `--instrument` to compile with AFL++ instrumentation, otherwise, it builds native binaries.
3. `./fetch_corpora.sh` - Downloads the public `public.zip` seed corpora directly from Google's OSS-Fuzz Cloud Storage.
