#!/bin/bash

export $(grep -v '^#' .env | xargs)

CONTAINER_VECTOR="agentv-app-vectorstore-server"
CONTAINER_PRE="agentv-app-preprocessing-server"
CONTAINER_DB="agentv-app-db"

DEFAULT_AGENTV_PORT=8506

# Use first argument as port, or default to 8506
AGENTV_PORT=${1:-$DEFAULT_AGENTV_PORT}

# Check if the container is running
if [ "$(docker ps -q -f name=^/${CONTAINER_VECTOR}$)" ]; then
    echo "Container '$CONTAINER_VECTOR' is already running."
else
    echo "Container '$CONTAINER_VECTOR' is not running. Attempting to start..."
    
    # Check if the container exists (but stopped)
    if [ "$(docker ps -aq -f name=^/${CONTAINER_VECTOR}$)" ]; then
        docker start "$CONTAINER_VECTOR"
        echo "Container '$CONTAINER_VECTOR' started."
    else
        echo "Container '$CONTAINER_VECTOR' does not exist. Creating and starting..."
        docker run -d --name "$CONTAINER_VECTOR" -v ./data/vectorstores/:/data -p 8001:8000 chromadb/chroma
    fi
fi

if [ "$(docker ps -q -f name=^/${CONTAINER_PRE}$)" ]; then
    echo "Container '$CONTAINER_PRE' is already running."
else
    echo "Container '$CONTAINER_PRE' is not running. Attempting to start..."
    
    # Check if the container exists (but stopped)
    if [ "$(docker ps -aq -f name=^/${CONTAINER_PRE}$)" ]; then
        docker start "$CONTAINER_PRE"
        echo "Container '$CONTAINER_PRE' started."
    else
        echo "Container '$CONTAINER_PRE' does not exist. Creating and starting..."
        if [[ -z $(docker images -q "$CONTAINER_PRE") ]]; then
            git clone https://github.com/sakunaharinda/agentv-app-preprocessing-server.git
            cd agentv-app-preprocessing-server
            docker build -t "$CONTAINER_PRE" .
            cd ../
        fi
        docker run -d --name "$CONTAINER_PRE" -p 8000:8000 "$CONTAINER_PRE"
        # docker run -d --name "$CONTAINER_PRE" -v ./data/vectorstores/:/data -p 8001:8000 chromadb/chroma
    fi
fi

if [ "$(docker ps -q -f name=^/${CONTAINER_DB}$)" ]; then
    echo "Container '$CONTAINER_DB' is already running."
else
    echo "Container '$CONTAINER_DB' is not running. Attempting to start..."
    
    # Check if the container exists (but stopped)
    if [ "$(docker ps -aq -f name=^/${CONTAINER_DB}$)" ]; then
        docker start "$CONTAINER_DB"
        echo "Container '$CONTAINER_DB' started."
    else
        echo "Container '$CONTAINER_DB' does not exist. Creating and starting..."
        docker run -d --name "$CONTAINER_DB" -p 27017:27017 mongodb/mongodb-community-server
    fi
fi

# echo "Adding users..."
# python push_users.py --user_file=seed_users.json

# Once the container is running, launch the Streamlit app
echo "Launching AGentV..."
streamlit run AGentV.py --server.port "$AGENTV_PORT"
