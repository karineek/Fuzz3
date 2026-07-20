cp ../gpu_wrapper/harness.cu .
cp ../gpu_wrapper/forkserver.py .

docker build -t dockerfile .
docker rm -f fuzz3-worker-cpu
docker run -dit --name fuzz3-worker-cpu dockerfile /bin/bash
