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
from models.record_dto import Hierarchy
from typing import Literal

_ = load_dotenv()

@st.cache_data
def load_json_output(data):    
    return json.dumps([p.to_dict() for p in data])

@st.cache_data
def load_policy(data):
    return pd.DataFrame(data)

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
    
@st.cache_data(show_spinner=False)
def get_entity_hierarchy(hierarchy_file):
    
    main_hierarchy = load_hierarchy_yaml(hierarchy_file)
    
    subject_h = remove_itself(flatten(main_hierarchy.get('subjects', {})))
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
    
    return id_model, id_tokenizer, gen_model, gen_tokenizer, ver_model, ver_tokenizer, loc_model, loc_tokenizer, vectorestores
    

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

@st.cache_resource
def load_vectorstores(store_location = "../data/vectorstores"):
    embeddings = HuggingFaceEmbeddings(
        model_name="mixedbread-ai/mxbai-embed-large-v1", model_kwargs={"device": "cuda:0"}
    )

    vector_store_subjects = FAISS.load_local(
        f"{store_location}/subjects_index",
        embeddings,
        allow_dangerous_deserialization=True,
    )
    vector_store_resources = FAISS.load_local(
        f"{store_location}/resources_index",
        embeddings,
        allow_dangerous_deserialization=True,
    )
    # vector_store_purposes = FAISS.load_local(
    #     f"{store_location}/purposes_index",
    #     embeddings,
    #     allow_dangerous_deserialization=True,
    # )
    vector_store_conditions = FAISS.load_local(
        f"{store_location}/conditions_index",
        embeddings,
        allow_dangerous_deserialization=True,
    )
    
    vector_store_actions = FAISS.load_local(
        f"{store_location}/actions_index",
        embeddings,
        allow_dangerous_deserialization=True,
    )

    stores = {
        "subject": vector_store_subjects,
        "action": vector_store_actions,
        "resource": vector_store_resources,
        # "purpose": vector_store_purposes,
        "condition": vector_store_conditions,
    }

    return stores

class ModelStore:
    
    def __init__(self, fake=False):
        
        if fake:
            self.id_model, self.id_tokenizer, self.gen_model, self.gen_tokenizer, self.ver_model, self.ver_tokenizer, self.loc_model, self.loc_tokenizer, self.vectorestores = 9*[None]
        
        else:
            self.id_model, self.id_tokenizer, self.gen_model, self.gen_tokenizer, self.ver_model, self.ver_tokenizer, self.loc_model, self.loc_tokenizer, self.vectorestores = load_models()