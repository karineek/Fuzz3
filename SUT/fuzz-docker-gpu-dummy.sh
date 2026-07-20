#!/bin/bash
inseed=$1 # docker-in-gpu-dummy
out=$2    # out
crash=$3  # crashes
itr=$4    # 10000
container="$5" # e9c4c6988976

# CPU: ./fuzz-docker-gpu-dummy.sh docker-in-gpu-dummy docker-out docker-crash 100 fuzz3-worker-cpu
# GPU: ./fuzz-docker-gpu-dummy.sh docker-in-gpu-dummy docker-out docker-crash 100 fuzz3-worker-gpu

#export DOCKER_CONTAINER=$continaer
export DOCKER_CONTAINER="$container"

if ! docker inspect "$DOCKER_CONTAINER" >/dev/null 2>&1; then
    echo "ERROR: Container $DOCKER_CONTAINER does not exist"
    exit 1
fi

docker start "$DOCKER_CONTAINER" >/dev/null 2>&1 || true

if ! docker exec "$DOCKER_CONTAINER" sh -lc ':' >/dev/null 2>&1; then
    echo "ERROR: Container $DOCKER_CONTAINER is not running"
    echo "Status: $(docker inspect -f '{{.State.Status}}' "$DOCKER_CONTAINER")"
    echo "Exit code: $(docker inspect -f '{{.State.ExitCode}}' "$DOCKER_CONTAINER")"
    docker logs --tail 20 "$DOCKER_CONTAINER"
    exit 1
fi

echo "Container $DOCKER_CONTAINER is running"

python3 ../blackbox.py -i $inseed -o $out -c $crash \
        --executor docker_executor \
        --executor-args "python3 /fuzz_workspace/forkserver.py" \
        --generator sort_generator_legal \
        --mutators shuffle_items dup_item_end add_item_end chop_item flip_item_sign none \
        --observers entropy_sliding_window_observer \
        --oracles entropy_oracle \
        --iterations $itr


cp do-in/* $inseed/  # Debug
