import json
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.json_loader import JSONLoader
from models.record_dto import Hierarchy
from langchain_core.documents import Document

def load_vectorstore(component, entity_list, save_location = "data/vectorstores", cache = "/mnt/huggingface/"):
    
    documents = [Document(page_content=ent, metadata={'component': f'{component}'}) for ent in entity_list]
    text_splitter  = RecursiveCharacterTextSplitter(chunk_size=100,chunk_overlap=0)
    text_chunks = text_splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(model_name="mixedbread-ai/mxbai-embed-large-v1",
                                    cache_folder = cache,
                                    model_kwargs={'device':"cuda", "trust_remote_code": True})

    vector_store = FAISS.from_documents(text_chunks,embeddings)
    vector_store.save_local(f'{save_location}/{component}_index')
    
    return vector_store