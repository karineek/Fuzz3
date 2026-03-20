#!/bin/bash
set -e

echo "[*] Fetching Google OSS-Fuzz seed corpora..."

mkdir -p corpora
cd corpora

download_corpus() {
    TARGET_PROJECT=$1
    FUZZER_NAME=$2
    URL="https://storage.googleapis.com/${TARGET_PROJECT}-backup.clusterfuzz-external.appspot.com/corpus/libFuzzer/${FUZZER_NAME}/public.zip"
    
    echo " -> Fetching ${FUZZER_NAME} corpus..."
    wget -q --show-progress -O "${FUZZER_NAME}_corpus.zip" "$URL"
    
    mkdir -p "${FUZZER_NAME}_seeds"
    unzip -q "${FUZZER_NAME}_corpus.zip" -d "${FUZZER_NAME}_seeds"
    rm "${FUZZER_NAME}_corpus.zip"
}

download_corpus "zlib" "zlib_uncompress_fuzzer"

download_corpus "jsoncpp" "jsoncpp_fuzzer"

echo " -> Fetching fastjson2 corpus (from go-fuzz-corpus)..."
if [ ! -d "go-fuzz-corpus" ]; then
    git clone --depth 1 -q https://github.com/dvyukov/go-fuzz-corpus.git
fi
mkdir -p fastjson2_seeds
cp -r go-fuzz-corpus/json/corpus/* fastjson2_seeds/
rm -rf go-fuzz-corpus

echo "[+] All corpora downloaded and extracted into the 'corpora/' directory."
