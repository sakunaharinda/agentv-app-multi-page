import streamlit as st
from hierarchy_visualizer import visualize_hierarchy_expander

def on_click_generate():
    st.session_state.is_generating = True
    
st.markdown(
        f"""
        <style>
            .st-key-fab button {{
                position: fixed;
                top: 50%;
                box-shadow: rgba(0, 0, 0, 0.16) 0px 4px 16px;
                z-index: 999;
                border-radius: 2rem;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

st.title("Policy Generation")

visualize_hierarchy_expander(st.session_state.main_hierarchy, key='policy_doc_hierarchy')

with st.container(border=False, height=150):
    policy_doc = st.file_uploader("Upload a high-level requirement specification document", key='policy_doc', help='Upload a high-level requirement specification document written in natural language (i.e., English), that specifies who can access what information in the organization.', type=['md'])
    

with st.container(border=True, height=210):
    st.write("Statues")
    
generate_button = st.button(label='Generate', type='primary', key='generate_btn', use_container_width=True, disabled=st.session_state.is_generating, on_click=on_click_generate, help=f"Click to start generating access control policies")