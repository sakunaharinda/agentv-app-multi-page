#!/bin/bash

CONTAINER_NAME="vectorstore_server"
DEFAULT_AGENTV_PORT=8506

# Use first argument as port, or default to 8506
AGENTV_PORT=${1:-$DEFAULT_AGENTV_PORT}

# Check if the container is running
if [ "$(docker ps -q -f name=^/${CONTAINER_NAME}$)" ]; then
    echo "Container '$CONTAINER_NAME' is already running."
else
    echo "Container '$CONTAINER_NAME' is not running. Attempting to start..."
    
    # Check if the container exists (but stopped)
    if [ "$(docker ps -aq -f name=^/${CONTAINER_NAME}$)" ]; then
        docker start "$CONTAINER_NAME"
        echo "Container '$CONTAINER_NAME' started."
    else
        echo "Container '$CONTAINER_NAME' does not exist. Creating and starting..."
        docker run -d --name "$CONTAINER_NAME" -v ./data/vectorstores/:/data -p 8001:8000 chromadb/chroma
    fi
fi

# Once the container is running, launch the Streamlit app
echo "Launching AGentV..."
CUDA_VISIBLE_DEVICES=0 HF_HOME=/mnt/huggingface/ streamlit run AGentV.py --server.port "$AGENTV_PORT"
