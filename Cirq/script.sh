#!/bin/bash
cd ~/Cirq
source .venv/bin/activate
which pdflatex
python -m pytest cirq-core/ | grep -e"Crash" -e"Failed" -e"FAILED" -e"failed" -e"error" -e"crash" -e"warnings" -e"Warnings" -e"Error" -e"ERROR"
