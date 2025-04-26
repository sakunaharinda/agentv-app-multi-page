docker stop $(docker ps -a -q)
docker container rm $(docker ps -a -q)