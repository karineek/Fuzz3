#!/bin/sh
set -eu

if [ "$#" -lt 5 ] || [ "$#" -gt 7 ]; then
    echo "Usage: $0 <seeds> <output> <crashes> <iterations> <container> [library] [function|all]" >&2
    exit 2
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
inseed=$1
out=$2
crash=$3
iterations=$4
container=$5
library=${6:-thrust}
function=${7:-sort}

export DOCKER_CONTAINER="$container"
export FUZZ3_LIBRARY="$library"
export FUZZ3_FUNCTION="$function"

if ! docker inspect "$DOCKER_CONTAINER" >/dev/null 2>&1; then
    echo "Container does not exist: $DOCKER_CONTAINER" >&2
    exit 1
fi

docker start "$DOCKER_CONTAINER" >/dev/null
if ! docker exec "$DOCKER_CONTAINER" sh -lc ':' >/dev/null 2>&1; then
    echo "Container is not running: $DOCKER_CONTAINER" >&2
    exit 1
fi

python3 "$script_dir/../blackbox.py" \
    -i "$inseed" -o "$out" -c "$crash" \
    --executor docker_executor \
    --generators library_worker_generator \
    --seedsno "${FUZZ3_SEEDS:-200}" \
    --mutators library_worker_mutator \
    --observers entropy_sliding_window_observer \
    --oracles entropy_oracle \
    --iterations "$iterations"
