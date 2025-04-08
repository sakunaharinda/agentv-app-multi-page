import streamlit as st

def inc_policy_nav_next():
    st.session_state.inc_count+=1
    st.session_state.inc_count = min(st.session_state.inc_count, len(st.session_state.inc_policies)-1)
    
def inc_policy_nav_last():
    st.session_state.inc_count = len(st.session_state.inc_policies)-1
        
def inc_policy_nav_prev():
    st.session_state.inc_count-=1
    st.session_state.inc_count = max(st.session_state.inc_count, 0)
    
def reset_inc_count_last():
    st.session_state.inc_count = len(st.session_state.inc_policies)-1
    
def cor_policy_nav_next():
    st.session_state.cor_count+=1
    st.session_state.cor_count = min(st.session_state.cor_count, len(st.session_state.corrected_policies)-1)
        
def cor_policy_nav_prev():
    st.session_state.cor_count-=1
    st.session_state.cor_count = max(st.session_state.cor_count, 0)
    
def cor_policy_nav_last():
    st.session_state.cor_count = len(st.session_state.corrected_policies)-1
    
def pdp_policy_nav_next():
    st.session_state.pdp_count+=1
    st.session_state.pdp_count = min(st.session_state.pdp_count, len(st.session_state.pdp_policies)-1)
        
def pdp_policy_nav_prev():
    st.session_state.pdp_count-=1
    st.session_state.pdp_count = max(st.session_state.pdp_count, 0)
    
def pdp_policy_nav_last():
    st.session_state.pdp_count = len(st.session_state.pdp_policies)-1
    
def get_inc_nlacp():
    if len(st.session_state.inc_policies)<1:
        return ""
    return st.session_state.inc_policies[st.session_state.inc_count]['nlacp']
    
def get_inc_policy():
    if len(st.session_state.inc_policies)<1:
        return []
    return st.session_state.inc_policies[st.session_state.inc_count]['policy']
    
def get_cor_nlacp():
    if len(st.session_state.corrected_policies)<1:
        return ""
    return st.session_state.corrected_policies[st.session_state.cor_count].to_dict()['policyDescription']
    
    
def get_cor_policy():
    if len(st.session_state.corrected_policies)<1:
        return []
    return st.session_state.corrected_policies[st.session_state.cor_count].to_dict()['policy']

def get_pdp_nlacp():
    if len(st.session_state.pdp_policies)<1:
        return ""
    return st.session_state.pdp_policies[st.session_state.pdp_count].to_dict()['policyDescription']
    
    
def get_pdp_policy():
    if len(st.session_state.pdp_policies)<1:
        return []
    return st.session_state.pdp_policies[st.session_state.pdp_count].to_dict()['policy']
    

def submit_callback():
    inc_policy_nav_next()
    