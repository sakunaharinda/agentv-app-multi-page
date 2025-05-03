#!/bin/bash

export $(grep -v '^#' .env | xargs)

CONTAINER_VECTOR="agentv-app-vectorstore-server"
CONTAINER_PRE="sakunaharinda/agentv:agentv-app-preprocessing-server"
CONTAINER_DB="agentv-app-db"
CONTAINER_AE="sakunaharinda/agentv:agentv-app-ac-engine"


if [ "$(docker ps -a --filter "name=^/${CONTAINER_VECTOR}$" --format '{{.Names}}')" == "$CONTAINER_VECTOR" ]; then
        docker start "$CONTAINER_VECTOR"
        echo "Container '$CONTAINER_VECTOR' started."
else
    echo "Container '$CONTAINER_VECTOR' does not exist. Creating and starting..."
    docker run -d --name agentv-app-vectorstore-server -p 8001:8000 chromadb/chroma:latest
fi

if [ "$(docker ps -a --filter "name=^/${CONTAINER_PRE}$" --format '{{.Names}}')" == "$CONTAINER_PRE" ]; then
        docker start "$CONTAINER_PRE"
        echo "Container '$CONTAINER_PRE' started."
else
    echo "Container '$CONTAINER_PRE' does not exist. Creating and starting..."
    docker run -d --name agentv-app-preprocessing-server "$CONTAINER_PRE"
fi

if [ "$(docker ps -a --filter "name=^/${CONTAINER_DB}$" --format '{{.Names}}')" == "$CONTAINER_DB" ]; then
        docker start "$CONTAINER_DB"
        echo "Container '$CONTAINER_DB' started."
else
    echo "Container '$CONTAINER_DB' does not exist. Creating and starting..."
    docker run -d --name "$CONTAINER_DB" -p 27017:27017 mongodb/mongodb-community-server:latest
    python seed_users.py
fi

if [ "$(docker ps -a --filter "name=^/${CONTAINER_AE}$" --format '{{.Names}}')" == "$CONTAINER_AE" ]; then
        docker start "$CONTAINER_AE"
        echo "Container '$CONTAINER_AE' started."
else
    echo "Container '$CONTAINER_AE' does not exist. Creating and starting..."
    docker run -d --name agentv-app-ac-engine "$CONTAINER_AE"
fi




streamlit run AGentV.py --server.port 8506

