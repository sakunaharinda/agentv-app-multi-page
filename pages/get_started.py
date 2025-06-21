import streamlit as st
from utils import change_page_icon, store_value
from feedback import *
from streamlit_float import *
from models.pages import PAGE
from menus import standard_menu
from hierarchy_visualizer import visualize_hierarchy_dialog
from streamlit_tile import streamlit_tile

# @st.fragment
def start():
    st.session_state.current_page = PAGE.START


    full_container = st.container()
    call_name = st.session_state.name.split(" ")[0]
    st.title(f"Welcome to AGentV, {call_name}")

    with full_container:
        
        HEIGHT = 205
        st.container(height=80, border=False)
        
            
        r1col1,s1,r1col2 = st.columns([ 1,0.03, 1])

        
        with r1col1:
            gen_doc = streamlit_tile(
                title="Generate from a Document",
                description="Upload High-level Requirement Specification Document and Generate Access Control Policies from it",
                icon="article",
                color_theme="blue",
                height=HEIGHT,
                width='full',
                key="gen_doc_tile",
                label="Generate"
            )
            
        with r1col2:
            gen_sent = streamlit_tile(
                title="Generate from a Sentence",
                description="Generate an Access Control Policy from an English Sentence",
                icon="create",
                color_theme="indigo",
                height=HEIGHT,
                width='full',
                key="gen_sent_tile",
                label="Generate"
            )
        
        # st.container(height=10, border=False)
        r2col1, s2, r2col2 = st.columns([1,0.03, 1])
        
        with r2col1:
            corr_policies = streamlit_tile(
                title="Access Control Policies",
                description="Review generated access control policies and publish to the policy database for testing",
                icon="verified_user",
                color_theme="green",
                height=HEIGHT,
                width='full',
                key="cor_pol_tile",
                label="Review"
            )
            
        with r2col2:
            inc_policies = streamlit_tile(
                title="Incorrect Access Control Policies",
                description="Review and refine the incorrectly generated policies manually",
                icon="gpp_bad",
                color_theme="red",
                height=HEIGHT,
                width='full',
                key="onc_pol_tile",
                label="Refine"
            )
        
        r3col1, s3, r3col2 = st.columns([1, 0.03, 1])
        
        with r3col1:
            test_policies = streamlit_tile(
                title="Test Policies",
                description="Test the published policies by sending access requests",
                icon="assignment",
                color_theme="purple",
                height=HEIGHT,
                width='full',
                key="tesl_pol_tile",
                label="Test"
            )
            
        with r3col2:
            save_policies = streamlit_tile(
                title="Download Policies",
                description="Download the generated policies",
                icon="download",
                color_theme="yellow",
                height=HEIGHT,
                width='full',
                key="save_pol_tile",
                label="Download"
            )
        
            

        if gen_doc:
            change_page_icon('start_icon')
            st.switch_page('pages/generate_document.py')
            
            
        elif gen_sent:
            change_page_icon('start_icon')
            st.switch_page('pages/generate_individual.py')
        # elif write_xacml:
        #     change_page_icon('start_icon')
        #     st.switch_page('pages/write_policy.py')
        # else:
        #     st.session_state.enable_generation = False
        
        elif corr_policies:
            st.switch_page('pages/correct_policies.py')
        elif inc_policies:
            st.switch_page('pages/incorrect_policies.py')
        elif test_policies:
            st.switch_page('pages/test_policies.py')
        elif save_policies:
            st.switch_page('pages/policy_export.py')

    
start()
standard_menu(turn_on=True)

