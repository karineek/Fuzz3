sudo apt update
sudo apt install -y linux-headers-$(uname -r) nvidia-driver-470-server
sudo apt install nvidia-cuda-toolkit

./install-docker-cloudlab.sh
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey   | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list   | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g'   | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
which nvidia-ctk
/usr/bin/nvidia-ctk
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
docker info | grep -i runtime

sudo reboot

echo ">> Run: `nvidia-smi` to see the status of the GPUs."
