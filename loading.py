import os
import torch
import streamlit as st
import json
import pandas as pd
from transformers import AutoTokenizer, BertForSequenceClassification, BertTokenizerFast, AutoModelForCausalLM, BertForQuestionAnswering, AutoModelForSequenceClassification
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import yaml
from yaml.loader import SafeLoader
from models.record_dto import Hierarchy
from typing import Literal
import chromadb
import chromadb.utils.embedding_functions as embedding_functions

@st.cache_data
def load_json_output(data):    
    return json.dumps([p.to_dict() for p in data])

@st.cache_data
def load_policy(data):
    df = pd.DataFrame(data)
    df.rename(columns={
        'decision': 'Decision',
        'subject': 'Subject',
        'action': 'Action',
        'resource': 'Resource',
        'condition': 'Condition',
        'purpose': 'Purpose'
    }, inplace=True)
    return df

@st.cache_data
def load_hierarchy_yaml(file):
    content = file.getvalue().decode('utf-8')
    return yaml.safe_load(content)
    
@st.cache_data(show_spinner=False)
def flatten(nested_list):
    result = {}
    
    def process_item(item, parent_keys=None):
        if parent_keys is None:
            parent_keys = []
        
        if isinstance(item, dict):
            # Process dictionary
            for key, value in item.items():
                current_keys = parent_keys + [key]
                # Add the key itself to the result
                if key not in result:
                    result[key] = [key]
                # Update parent keys' values to include this key
                for pk in parent_keys:
                    if key not in result[pk]:
                        result[pk].append(key)
                process_item(value, current_keys)
        
        elif isinstance(item, list):
            # Process list
            for element in item:
                process_item(element, parent_keys)
        
        else:
            # Process string or other primitive
            if item not in result:
                result[item] = [item]
            # Update parent keys' values to include this item
            for pk in parent_keys:
                if item not in result[pk]:
                    result[pk].append(item)
    
    # Process each top-level item
    for item in nested_list:
        process_item(item)
    
    return result

@st.cache_data(show_spinner=False)
def remove_itself(hierarchy: dict):
    
    new_hierarchy = {}
    
    for k,v in hierarchy.items():
        if len(v)>1:
            new_hierarchy[k] = v[1:]
        else:
            new_hierarchy[k] = v
            
    return new_hierarchy
    
@st.cache_resource(show_spinner=False)
def get_entity_hierarchy(hierarchy_file):
    
    main_hierarchy = load_hierarchy_yaml(hierarchy_file)
    
    subject_h = flatten(main_hierarchy.get('subjects', {}))
    action_h = remove_itself(flatten(main_hierarchy.get('actions', {})))
    resource_h = remove_itself(flatten(main_hierarchy.get('resources', {})))
    condition_h = remove_itself(flatten(main_hierarchy.get('conditions', {})))
    
    return main_hierarchy, Hierarchy([subject_h, action_h, resource_h, condition_h])

@st.cache_resource
def load_models():
    
    id_model, id_tokenizer = load_id_model()
    gen_model, gen_tokenizer = load_gen_model()
    ver_model, ver_tokenizer = load_ver_model()
    loc_model, loc_tokenizer = load_loc_model()
    vectorestores = None #load_vectorstores("data/vectorstores")
    if st.session_state.use_chroma:
        embedding_model = None
        chroma_client = chromadb.HttpClient(host=os.environ['CHROMA_HOST'], port=os.environ['CHROMA_PORT'])
        vectorestores = load_vectorstores(chroma_client) 
    else:
        embedding_model = HuggingFaceEmbeddings(model_name="mixedbread-ai/mxbai-embed-large-v1",
                                    model_kwargs={'device':"cuda", "trust_remote_code": True})
        vectorestores = None 
    
    return id_model, id_tokenizer, gen_model, gen_tokenizer, ver_model, ver_tokenizer, loc_model, loc_tokenizer, vectorestores, embedding_model
    

@st.cache_resource
def load_id_model():
    
    checkpoint = "Sakuna/RAGent_id"
    
    id_model = BertForSequenceClassification.from_pretrained(checkpoint, num_labels=2).to('cuda:0')
    id_tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
    id_model.eval()
    return id_model, id_tokenizer    
    
    
@st.cache_resource
def load_gen_model():
    
    model_kwargs = dict(
        trust_remote_code=True,
        attn_implementation="flash_attention_2",  # loading the model with flash-attenstion support
        torch_dtype=torch.bfloat16,
    )
    
    checkpoint = "Sakuna/RAGent_gen"
    base_model = "meta-llama/Meta-Llama-3-8B-Instruct"
    
    gen_model = AutoModelForCausalLM.from_pretrained(checkpoint, 
                                                    **model_kwargs
                                                     ).to('cuda:0')
    gen_tokenizer = AutoTokenizer.from_pretrained(base_model, use_fast=True)
    gen_tokenizer.pad_token = gen_tokenizer.eos_token
    gen_tokenizer.padding_side = 'left'
    gen_model.eval()
    return gen_model, gen_tokenizer    


@st.cache_resource
def load_ver_model():
    
    checkpoint = "Sakuna/RAGent_ver"
    base_model = "facebook/bart-large"
    
    ver_tokenizer = AutoTokenizer.from_pretrained(base_model)
    ver_model = AutoModelForSequenceClassification.from_pretrained(
        checkpoint).to('cuda:0')
    ver_model.eval()
    return ver_model, ver_tokenizer 

@st.cache_resource
def load_loc_model():
    
    checkpoint = "Sakuna/RAGent_ver_local"
    
    model = BertForQuestionAnswering.from_pretrained(checkpoint).to('cuda:0')
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
    model.eval()
    return model, tokenizer  

def load_vectorstores(client):

    stores = {
        "subject": client.get_or_create_collection(name="subject", embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="mixedbread-ai/mxbai-embed-large-v1", device='cuda'), metadata={"hnsw:space": "cosine"}),
        "action": client.get_or_create_collection(name="action", embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="mixedbread-ai/mxbai-embed-large-v1", device='cuda'), metadata={"hnsw:space": "cosine"}),
        "resource": client.get_or_create_collection(name="resource", embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="mixedbread-ai/mxbai-embed-large-v1", device='cuda'), metadata={"hnsw:space": "cosine"}),
        # "purpose": vector_store_purposes,
        "condition": client.get_or_create_collection(name="condition", embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="mixedbread-ai/mxbai-embed-large-v1", device='cuda'), metadata={"hnsw:space": "cosine"}),
        # "nlacps": client.get_or_create_collection(name="nlacps", embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="mixedbread-ai/mxbai-embed-large-v1", device='cuda'), metadata={"hnsw:space": "cosine"})
        "bm25": None
    }

    return stores

@st.cache_data(show_spinner=False)
def load_auth_config(auth_file = 'auth_config.yaml'):
    with open(f'.streamlit/{auth_file}') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

class ModelStore:
    
    def __init__(self, fake=False):
            
        if fake:
            self.id_model, self.id_tokenizer, self.gen_model, self.gen_tokenizer, self.ver_model, self.ver_tokenizer, self.loc_model, self.loc_tokenizer, self.vectorestores, self.embedding_model = 10*[None]
        
        else:
            self.id_model, self.id_tokenizer, self.gen_model, self.gen_tokenizer, self.ver_model, self.ver_tokenizer, self.loc_model, self.loc_tokenizer, self.vectorestores, self.embedding_model = load_models()