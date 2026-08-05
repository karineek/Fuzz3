#!/bin/sh
set -eu

if [ "$1" = "cpu" ]; then
    apt-get -o Acquire::Retries=3 -o Acquire::http::No-Cache=True update
    apt-get install -y --no-install-recommends libthrust-dev
    rm -rf /var/lib/apt/lists/*
fi
