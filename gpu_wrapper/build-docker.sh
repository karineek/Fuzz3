docker build -t dockerfile .
docker rm -f fuzz3-worker-gpu
docker run -dit --name fuzz3-worker-gpu dockerfile /bin/bash
