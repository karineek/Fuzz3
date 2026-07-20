#!/bin/bash
inseed=$1 # docker-in-gpu-dummy
out=$2    # out
crash=$3  # crashes
itr=$4    # 10000

export DOCKER_CONTAINER=e5e647c5cfb4

if [ "$(docker inspect -f '{{.State.Running}}' "$DOCKER_CONTAINER" 2>/dev/null)" != "true" ]; then
    echo "Docker container $DOCKER_CONTAINER is not running"
    exit 1
fi

python3 ../blackbox.py -i $inseed -o $out -c $crash \
        --executor docker_executor \
        --executor-args "python3 /fuzz_workspace/forkserver.py" \
        --mutators none \
        --observers entropy_sliding_window_observer \
        --oracles entropy_oracle \
        --iterations $itr

