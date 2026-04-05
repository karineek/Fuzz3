
# Install cirq
cd ~
git clone https://github.com/quantumlib/Cirq.git
cd Cirq

# use venv - as it is very sensitive to req
python3.11 -m venv .venv
source .venv/bin/activate
python --version
python -m pip install --upgrade pip
python -m pip install -r dev_tools/requirements/dev.env.txt
