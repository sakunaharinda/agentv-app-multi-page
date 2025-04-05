import json
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.json_loader import JSONLoader
from models.record_dto import Hierarchy
from langchain_core.documents import Document
import streamlit as st

def create_ent_list(h_dict: dict, combine_key_val = False, save_path = None):
    
    l = []
    for k,v in h_dict.items():
        # TODO Currently only supports =
        if combine_key_val:
            for vv in v:
                if k!=vv:
                    l.append(f"{k}={vv}")
        else:
            if k not in l:
                l.append(k)
            for vv in v:
                if vv not in l:
                    l.append(vv)
                
    if save_path is not None:
        with open(save_path, 'w') as f:
            json.dump(l, f)
    return l


def extract_entities(hierarchies: Hierarchy, save_path = None):
    
    subjects = create_ent_list(hierarchies.subject_hierarchy, save_path= save_path + "/subjects.json" if save_path is not None else None)
    actions = create_ent_list(hierarchies.action_hierarchy, save_path= save_path + "/actions.json" if save_path is not None else None)
    resources = create_ent_list(hierarchies.resource_hierarchy, save_path= save_path + "/resources.json" if save_path is not None else None)
    conditions = create_ent_list(hierarchies.condition_hierarchy, combine_key_val=True, save_path= save_path + "/conditions.json" if save_path is not None else None)
    
    return subjects, actions, resources, conditions 
    


@st.cache_resource(show_spinner=False)
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
    
@st.cache_resource(show_spinner=False)
def build_vectorstores(_hierarchies, save_path = 'data/entities'):
    
    subjects, actions, resources, conditions = extract_entities(_hierarchies, save_path)
    
    stores = {}
    progress_text = "Processing the hierarchy ..."
    vs_build_bar = st.progress(0, text=progress_text)
    
    for i, ent in enumerate([('subject', subjects), ('action', actions), ('resource', resources), ('condition', conditions)]):
        stores[ent[0]] = load_vectorstore(ent[0], ent[1])
        if i==3:
            progress_text = "Uploaded hierarchy is processed successfully!"
        vs_build_bar.progress((i+1)*25, text=progress_text)
    # stores = {
    #     "subject": load_vectorstore('subject', subjects),
    #     "action": load_vectorstore('action', actions),
    #     "resource": load_vectorstore('resource', resources),
    #     # "purpose": vector_store_purposes,
    #     "condition": load_vectorstore('condition', conditions),
    # }
    
    return stores