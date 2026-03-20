#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="$PROJECT_ROOT/build"
TMP_BUILD="$OUT_DIR/tmp_zlib_build"
NUM_JOBS="$(nproc || echo 1)"

if [ "${1:-}" == "--afl" ]; then
    if command -v afl-clang-lto >/dev/null 2>&1; then TARGET_CC="afl-clang-lto"
    elif command -v afl-clang-fast >/dev/null 2>&1; then TARGET_CC="afl-clang-fast"
    elif command -v afl-cc >/dev/null 2>&1; then TARGET_CC="afl-cc"
    else echo "ERROR: No AFL compiler found." >&2; exit 1; fi
    TARGET_CXX="${TARGET_CC}++"
else
    TARGET_CC="clang"
    TARGET_CXX="clang++"
fi

CFLAGS=( -g -O1 -fno-omit-frame-pointer )
CXXFLAGS=( -g -O1 -fno-omit-frame-pointer -std=c++11 )
LDFLAGS=()

rm -rf "$TMP_BUILD" && mkdir -p "$TMP_BUILD"
cp -r "$PROJECT_ROOT/projects/zlib" "$TMP_BUILD/zlib"
cd "$TMP_BUILD/zlib"

echo "[*] Building zlib..."
CC="$TARGET_CC" CFLAGS="${CFLAGS[*]}" ./configure --static
make -j"$NUM_JOBS" clean && make -j"$NUM_JOBS" all

ZLIB_LIB="$PWD/libz.a"
ZLIB_INC="$PWD"
WRAPPER_SRC="$PROJECT_ROOT/oss-harness-wrapper.cpp"
OSS_FUZZ_DIR="$PROJECT_ROOT/projects/oss-fuzz"

echo "[*] Building uncompress fuzzers..."
for f in "$OSS_FUZZ_DIR/projects/zlib/zlib_uncompress"*fuzzer.cc; do
    [ -f "$f" ] || continue
    b=$(basename -s .cc "$f")
    echo "  -> $b"
    "$TARGET_CXX" "${CXXFLAGS[@]}" -I"$ZLIB_INC" -c "$f" -o "$b.o"
    "$TARGET_CXX" "${CXXFLAGS[@]}" -I"$ZLIB_INC" "$WRAPPER_SRC" "$b.o" "$ZLIB_LIB" -o "$OUT_DIR/$b" "${LDFLAGS[@]}"
done

# Check for dictionaries in the pinned commit
if ls "$OSS_FUZZ_DIR/projects/zlib/"*.dict 1> /dev/null 2>&1; then
    cp "$OSS_FUZZ_DIR/projects/zlib/"*.dict "$OUT_DIR/"
fi
