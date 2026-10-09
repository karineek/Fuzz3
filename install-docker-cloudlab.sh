#!/usr/bin/env bash
set -euo pipefail

# Tested on CloudLab CPU and GPU nodes.
sudo apt-get update

# Install docker
sudo apt-get install -y apt-transport-https curl gnupg-agent ca-certificates software-properties-common
sudo apt-get install -y docker.io docker-buildx

sudo groupadd -f docker
sudo usermod -aG docker "$(whoami)"
sudo systemctl stop docker
sudo systemctl stop docker.socket
sudo systemctl stop containerd
sudo systemctl start docker

docker --version
groups "$(whoami)"
sudo chmod 666 /var/run/docker.sock
docker run hello-world

echo ">> Docker is ready. If docker access fails in a new shell, log out/in or rerun:"
echo ">>   sudo chmod 666 /var/run/docker.sock"
