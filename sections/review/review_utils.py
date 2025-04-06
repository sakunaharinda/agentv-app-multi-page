import streamlit as st
from ac_engine_service import AccessControlEngine

def publish_cur(ac_engine: AccessControlEngine):
    cur_policy = st.session_state.corrected_policies[st.session_state.cor_count]
    return ac_engine.create_policy(cur_policy)
    
def publish_all(ac_engine: AccessControlEngine):
    
    policies = st.session_state.corrected_policies
    return ac_engine.create_multiple_policies(policies)