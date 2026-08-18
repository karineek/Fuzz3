sudo apt update
sudo apt install -y linux-headers-$(uname -r) nvidia-driver-470-server
sudo apt install nvidia-cuda-toolkit
sudo reboot

echo ">> Run: `nvidia-smi` to see the status of the GPUs."
