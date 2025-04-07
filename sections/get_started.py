import streamlit as st
from utils import store_value, change_page_icon
from loading import get_entity_hierarchy
from feedback import *
from hierarchy_visualizer import set_hierarchy
from streamlit_float import *
from introduction import intro

float_init()

st.markdown(
        f"""
        <style>
            .st-key-gen_doc button,
            .st-key-write_xacml button,
            .st-key-gen_sent button {{
                height: 100px;
                font-size: 100px !important;
                border-radius: 2rem;
                box-shadow: rgba(0, 0, 0, 0.16) 0px 4px 16px;
            }}
            
        </style>
        """,
        unsafe_allow_html=True,
    )

if st.session_state.first_time:
    intro()


full_container = st.container()

with full_container:
    st.title("Welcome to AGentV")
    
    st.container(height=20, border=False)
    
    st.markdown("## To start the policy generation, ")
    
    # load_value("hierarchy_upload")
    with st.container(border=False, height=160):
        hierarchy_file = st.file_uploader("Upload the organization hierarchy", key='_hierarchy_upload', help='Upload the organization hierarchy specified in YAML format', type=['yaml', 'yml'], on_change=store_value, args=("hierarchy_upload",))
        
            
    pbar = st.container(height=50, border=False)
    
    _,col1, col2,col3,_ = st.columns([0.05, 1,1,1, 0.05])
    gen_doc = col1.button(f"Generate from a **Document**", key='gen_doc', type='secondary', icon=":material/article:", use_container_width=True, disabled= not st.session_state.enable_generation)
    
    gen_sent = col2.button(f"Generate from a **Sentence**", key='gen_sent', type='secondary', icon=":material/create:", use_container_width=True, disabled= not st.session_state.enable_generation)
    
    write_xacml = col3.button(f"Write in **XACML**", key='write_xacml', type='secondary', icon=":material/code:", use_container_width=True, disabled= not st.session_state.enable_generation)
        

if gen_doc:
    change_page_icon('start_icon')
    st.switch_page('sections/generation/generate_document.py')
    
elif gen_sent:
    change_page_icon('start_icon')
    st.switch_page('sections/generation/generate_individual.py')
    
elif write_xacml:
    change_page_icon('start_icon')
    st.switch_page('sections/generation/write_policy.py')
    


with pbar:
    set_hierarchy(hierarchy_file)
    
full_container.float("top: 20%;")
