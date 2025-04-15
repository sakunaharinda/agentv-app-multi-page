cd data
docker run -d --name vectorstore_server -v ./vectorstores:/data -p 8001:8000 chromadb/chroma