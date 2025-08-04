docker stop $(docker ps -a -q)
docker container rm $(docker ps -a -q)

echo "Removing Images ..."
docker image prune -a

echo "Removing Volumes ..."
docker volume prune -a