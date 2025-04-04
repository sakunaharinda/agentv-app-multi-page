import streamlit as st

def set_state(state, value):
    if state not in st.session_state:
        st.session_state[state] = value
        
        
def init():
    set_state('start_title', 'Getting Started')
    set_state('generate_doc_title', 'Upload Policy Document')
    set_state('generate_single_title', 'Write Policy')
    set_state('cor_policies_title', 'Correct Policies')
    set_state('inc_policies_title', 'Incorrect Policies')
    
    set_state('start_icon', '')
    set_state('inputs_icon', '')
    set_state('cor_policies_icon', '')
    set_state('inc_policies_icon', '')
    
    set_state('enable_generation', False)
    
    if 'expand' not in st.session_state:
        st.session_state.expand = True
    else:
        st.session_state.expand = False
    
def update_status(page_title):
    st.session_state[page_title] += " ✔️"
    
    
def store_value(key):
    st.session_state[key] = st.session_state["_"+key]
def load_value(key):
    if key not in st.session_state:
        st.session_state[key] = None
    st.session_state["_"+key] = st.session_state[key]
    