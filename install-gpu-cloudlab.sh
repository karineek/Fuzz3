#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update

if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "ERROR: nvidia-smi is not available." >&2
    echo "Install a modern NVIDIA host driver first, then reboot." >&2
    echo "The CUDA 12.4 worker images need a driver new enough for CUDA 12.x;" >&2
    echo "the old nvidia-driver-470-server package is not sufficient." >&2
    exit 1
fi

nvidia-smi

./install-docker-cloudlab.sh

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | sudo gpg --batch --yes --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

sudo chmod 666 /var/run/docker.sock
docker info | grep -i runtime
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi

echo ">> GPU container runtime is ready."
