import streamlit as st
from hierarchy_visualizer import visualize_hierarchy_expander

st.title("Policy Generation")

visualize_hierarchy_expander(st.session_state.main_hierarchy, key='policy_doc_hierarchy')

with st.container(border=False, height=160):
    policy_doc = st.file_uploader("Upload a high-level requirement specification document", key='policy_doc', help='Upload a high-level requirement specification document written in natural language (i.e., English), that specifies who can access what information in the organization.', type=['md'])
