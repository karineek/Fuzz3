#!/usr/bin/env bash
set -euo pipefail

echo ">> Starting Fuzz3 installation..."

python3 -m venv .venv

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .

echo ">> Done installing Fuzz3"
echo ">> Activate with: source .venv/bin/activate"
