#!/usr/bin/env bash
set -euo pipefail

echo "[*] Setting up projects directory..."
mkdir -p projects
cd projects

echo "[*] Pulling target repositories..."
[ ! -d "zlib" ] && git clone --depth 1 -b develop https://github.com/madler/zlib.git
[ ! -d "jsoncpp" ] && git clone --depth 1 https://github.com/open-source-parsers/jsoncpp.git
[ ! -d "fastjson2" ] && git clone --depth 1 https://github.com/alibaba/fastjson2.git
[ ! -d "libprotobuf-mutator" ] && git clone --depth 1 https://github.com/google/libprotobuf-mutator.git

echo "[*] Pulling OSS-Fuzz and checking out commit 801c2423b0bea9e7cb33403f003c7c108967c11e..."
if [ ! -d "oss-fuzz" ]; then
    git clone https://github.com/google/oss-fuzz.git
fi

echo "[+] Pull complete. All sources are in the projects/ directory."
