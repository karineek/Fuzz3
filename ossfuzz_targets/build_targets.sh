#!/usr/bin/env bash
set -euo pipefail

MODE="--clang"
if [ "${1:-}" == "--afl" ]; then
    MODE="--afl"
    echo "[*] Build mode: AFL Instrumentation"
else
    echo "[*] Build mode: Native Clang (No instrumentation)"
fi

mkdir -p build

echo "======================================"
echo " Building ZLIB "
echo "======================================"
./build_zlib.sh "$MODE"

echo "======================================"
echo " Building FASTJSON2 "
echo "======================================"
./build_fastjson2.sh "$MODE"

echo "======================================"
echo " Building JSONCPP "
echo "======================================"
./build_jsoncpp.sh "$MODE"

echo "[+] All targets built successfully! Check the build/ directory."
