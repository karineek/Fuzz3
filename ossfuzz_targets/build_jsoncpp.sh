#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="$PROJECT_ROOT/build"
TMP_BUILD="$OUT_DIR/tmp_jsoncpp_build"
LPM_DIR="$TMP_BUILD/LPM"
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

CXXFLAGS=( -g -O1 -fno-omit-frame-pointer -std=c++17 )
CFLAGS=( -g -O1 -fno-omit-frame-pointer )
LDFLAGS=()

rm -rf "$TMP_BUILD" && mkdir -p "$TMP_BUILD" "$LPM_DIR"
cp -r "$PROJECT_ROOT/projects/libprotobuf-mutator" "$TMP_BUILD/"
cp -r "$PROJECT_ROOT/projects/jsoncpp" "$TMP_BUILD/"

echo "[*] Building libprotobuf-mutator (LPM)..."
cd "$LPM_DIR"
cmake ../libprotobuf-mutator -GNinja -DLIB_PROTO_MUTATOR_DOWNLOAD_PROTOBUF=ON -DLIB_PROTO_MUTATOR_TESTING=OFF -DCMAKE_BUILD_TYPE=Release
ninja

echo "[*] Building jsoncpp..."
cd "$TMP_BUILD/jsoncpp"
if grep -q "CMAKE_CXX_STANDARD 11" CMakeLists.txt >/dev/null 2>&1; then
    sed -i 's/set(CMAKE_CXX_STANDARD 11)/set(CMAKE_CXX_STANDARD 17)/' CMakeLists.txt || true
fi

BUILD_DIR="$TMP_BUILD/jsoncpp/build"
mkdir -p "$BUILD_DIR" && cd "$BUILD_DIR"

cmake -DCMAKE_CXX_COMPILER="$TARGET_CXX" -DCMAKE_C_COMPILER="$TARGET_CC" -DCMAKE_CXX_FLAGS="${CXXFLAGS[*]}" -DCMAKE_C_FLAGS="${CFLAGS[*]}" -DBUILD_SHARED_LIBS=OFF -DJSONCPP_WITH_TESTS=ON -DJSONCPP_WITH_POST_BUILD_UNITTEST=OFF -G "Unix Makefiles" ..
make -j"$NUM_JOBS"

JSONCPP_LIB="$BUILD_DIR/lib/libjsoncpp.a"
[ ! -f "$JSONCPP_LIB" ] && JSONCPP_LIB="$BUILD_DIR/libjsoncpp.a"
JSONCPP_INCLUDE="$TMP_BUILD/jsoncpp/include"

# The C++ Harness
HARNESS_SRC="$TMP_BUILD/jsoncpp/src/test_lib_json/fuzz.cpp"
WRAPPER_SRC="$PROJECT_ROOT/oss-harness-wrapper.cpp"
OUT_BINARY="$OUT_DIR/jsoncpp_fuzzer"

echo "[*] Compiling harness & wrapper..."
"$TARGET_CXX" "${CXXFLAGS[@]}" -I"$JSONCPP_INCLUDE" -c "$HARNESS_SRC" -o fuzz_fuzz_o.o
"$TARGET_CXX" "${CXXFLAGS[@]}" -I"$JSONCPP_INCLUDE" "$WRAPPER_SRC" fuzz_fuzz_o.o "$JSONCPP_LIB" -o "$OUT_BINARY" "${LDFLAGS[@]}"

if [ -f "$TMP_BUILD/jsoncpp/src/test_lib_json/fuzz.dict" ]; then
    cp "$TMP_BUILD/jsoncpp/src/test_lib_json/fuzz.dict" "$OUT_DIR/jsoncpp_fuzzer.dict"
fi

# =========================================================================
# Proto Fuzzer - Sourced from the PINNED OSS-Fuzz commit
# =========================================================================
OSS_JSON_DIR="$PROJECT_ROOT/projects/oss-fuzz/projects/jsoncpp"
PROTO_SRC="$OSS_JSON_DIR/json.proto"
PROTO_FUZZ_SRC="$OSS_JSON_DIR/jsoncpp_fuzz_proto.cc"
PROTO_CONVERTER="$OSS_JSON_DIR/json_proto_converter.cc"

if [ -f "$PROTO_SRC" ]; then
    echo "[*] Building proto fuzzer using LPM..."
    PROTOC_BIN="$LPM_DIR/external.protobuf/bin/protoc"
    GEN_DIR="$TMP_BUILD/genfiles"
    mkdir -p "$GEN_DIR"
    
    "$PROTOC_BIN" "$PROTO_SRC" --cpp_out="$GEN_DIR" --proto_path="$OSS_JSON_DIR"

    # Grouping all includes for a clean build command
    PROTO_INCLUDES=(
        "-I$JSONCPP_INCLUDE"
        "-I$GEN_DIR"
        "-I$LPM_DIR/external.protobuf/include"
        "-I$TMP_BUILD"
        "-I$OSS_JSON_DIR"
    )

    "$TARGET_CXX" "${CXXFLAGS[@]}" "${PROTO_INCLUDES[@]}" -c "$GEN_DIR/json.pb.cc" -o gen_json_pb_o.o
    "$TARGET_CXX" "${CXXFLAGS[@]}" "${PROTO_INCLUDES[@]}" -c "$PROTO_CONVERTER" -o proto_converter_o.o
    "$TARGET_CXX" "${CXXFLAGS[@]}" "${PROTO_INCLUDES[@]}" -c "$PROTO_FUZZ_SRC" -o proto_fuzz_o.o

    LPM_LIB_A="$LPM_DIR/src/libprotobuf-mutator.a"
    LPM_LIB_LIBFUZZER="$LPM_DIR/src/libprotobuf-mutator-libfuzzer.a"
    PROTO_A_DIR="$LPM_DIR/external.protobuf/lib"
    
    echo "[*] Linking proto fuzzer..."
    # Added $WRAPPER_SRC so we actually have a main() function for Native testing!
    "$TARGET_CXX" "${CXXFLAGS[@]}" "${PROTO_INCLUDES[@]}" \
        "$WRAPPER_SRC" gen_json_pb_o.o proto_converter_o.o proto_fuzz_o.o \
        "$LPM_LIB_LIBFUZZER" "$LPM_LIB_A" -Wl,--start-group "$PROTO_A_DIR"/lib*.a -Wl,--end-group \
        "$JSONCPP_LIB" -o "$OUT_DIR/jsoncpp_proto_fuzzer"
fi
