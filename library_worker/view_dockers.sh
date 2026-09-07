docker system df -v

echo "You can remove an image (docker rmi), or a container (docker rm) and stop the container before (docker stop)"
echo "To build: docker build -t dockerfile ."
echo "To run detached: docker run -dt dockerfile 1 Phi 2 2"
echo "To enter it: docker exec -it 5a787568b179 /bin/bash"
echo "Or to view a file: docker exec 5a787568b179 cat repeat_script_2_setting_2_repeat_1.txt"
echo "Or ls docker exec 5a787568b179 ls"
echo "To detach the screen from the bash session in Docker, press: Ctrl+P and then Ctrl+Q"
