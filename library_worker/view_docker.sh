#!/bin/sh
set -eu

container=${1:-fuzz3-worker-gpu}
docker exec -it "$container" /bin/bash
