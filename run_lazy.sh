#!/bin/bash

export $(grep -v '^#' .env | xargs)

docker start agentv-db-cleaner
docker start agentv-app-ac-engine agentv-app-agentv-app-preprocessing-server-1 agentv-app-vectorstore-server agentv-app-db
LOAD_PREV=false streamlit run AGentV.py --server.port 8506