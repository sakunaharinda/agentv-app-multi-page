import streamlit as st
from hierarchy_visualizer import visualize_hierarchy_expander

st.title("Policy Generation")

visualize_hierarchy_expander(st.session_state.main_hierarchy, key='policy_doc_hierarchy')
