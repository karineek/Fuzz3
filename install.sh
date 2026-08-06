#!/usr/bin/env bash
set -euo pipefail

FORCE=false

usage() {
    echo "Usage: $0 [--force]"
    echo
    echo "  --force  Continue when apt-get is unavailable."
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --force)
            FORCE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "ERROR: Unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

echo ">> Starting Fuzz3 installation..."

if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y \
        python3 \
        python3-venv \
        python3-pip \
        fdupes
elif [[ "$FORCE" == true ]]; then
    echo "WARNING: apt-get is unavailable; skipping system dependencies." >&2
    echo "Please install these dependencies separately:" >&2
    echo "  - python3" >&2
    echo "  - python3-venv, or equivalent venv support" >&2
    echo "  - python3-pip" >&2
    echo "  - fdupes" >&2
else
    echo "ERROR: This installer currently supports apt-based systems only." >&2
    echo "If you are running MacOS or Windows based systems, you first need to install:" >&2
    echo "  - python3" >&2
    echo "  - python3-venv, or equivalent venv support" >&2
    echo "  - python3-pip" >&2
    echo "  - fdupes" >&2
    echo "Install the dependencies manually, then rerun with --force." >&2
    exit 1
fi

for command in python3 fdupes; do
    if ! command -v "$command" >/dev/null 2>&1; then
        echo "ERROR: Required command is unavailable: $command" >&2
        echo "Please install these dependencies separately manually." >&2
        exit 1
    fi
done

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .

echo ">> Done installing Fuzz3"
echo ">> Activate with: source .venv/bin/activate"
