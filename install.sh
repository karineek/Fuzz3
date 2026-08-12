#!/usr/bin/env bash
set -e

echo ">> Start installation of Fuzz3..."

python -m pip install --upgrade pip
python -m pip install scipy
python -m pip install -e .

rc=`echo $?`
echo ">> Done installing Fuzz3 (rc=$rc)"
