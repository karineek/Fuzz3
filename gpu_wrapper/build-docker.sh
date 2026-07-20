docker build -t dockerfile .
docker rm -f fuzz3-worker
docker run -dit --name fuzz3-worker dockerfile /bin/bash
