sudo apt-get update

# Fix the users
sudo groupadd docker
sudo usermod -aG docker $(whoami)

# Install docker
sudo apt install apt-transport-https curl gnupg-agent ca-certificates software-properties-common -y
sudo apt install docker.io
sudo systemctl stop docker
sudo systemctl stop docker.socket
sudo systemctl stop containerd
sudo systemctl start docker

docker --version
groups $(whoami)
sudo chmod 666 /var/run/docker.sock
docker run hello-world

# Needed for the parameterised dockers
sudo apt-get install -y docker-buildx

echo ">> To build image run: docker build -t dockerfuzzer ."
