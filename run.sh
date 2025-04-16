#!/bin/bash

CONTAINER_VECTOR="vectorstore_server"
CONTAINER_PRE="agentv-app-preprocessing-server"
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
        git clone https://github.com/sakunaharinda/agentv-app-preprocessing-server.git
        cd agentv-app-preprocessing-server
        docker build -t "$CONTAINER_PRE" .
        docker run -d --name "$CONTAINER_PRE" -p 8000:8000 "$CONTAINER_PRE"
        # docker run -d --name "$CONTAINER_PRE" -v ./data/vectorstores/:/data -p 8001:8000 chromadb/chroma
    fi
fi

# Once the container is running, launch the Streamlit app
echo "Launching AGentV..."
CUDA_VISIBLE_DEVICES=0 HF_HOME=/mnt/huggingface/ streamlit run AGentV.py --server.port "$AGENTV_PORT"
