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
    set_state('main_hierarchy', None)
    
    set_state('inc_count', -1)
    set_state('cor_count', -1)
    set_state('inc_policies', [])
    set_state('corrected_policies', [])
    set_state('is_generating', False)
    
    if 'expand' not in st.session_state:
        st.session_state.expand = True
    else:
        st.session_state.expand = False
    
    st.session_state.num_correct_policies = len(st.session_state.corrected_policies)
    st.session_state.num_incorrect_policies = len(st.session_state.inc_policies)
    