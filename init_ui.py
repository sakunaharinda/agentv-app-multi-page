import streamlit as st
from ac_engine_service import AccessControlEngine
from loading import ModelStore
from uuid import uuid4
from models.pages import PAGE
import os

def set_state(state, value):
    if state not in st.session_state:
        st.session_state[state] = value
        
        
def init():
    
    st.set_page_config(layout="wide")
    
    set_state('start_icon', ':material/radio_button_unchecked:')
    set_state('correct_pol_icon', ':material/radio_button_unchecked:')
    set_state('incorrect_pol_icon', ':material/radio_button_unchecked:')
    set_state('gen_doc_icon', ':material/radio_button_unchecked:')
    set_state('gen_sent_icon', ':material/radio_button_unchecked:')
    set_state('write_xacml_icon', ':material/radio_button_unchecked:')
    set_state('viz_icon', ':material/radio_button_unchecked:')
    set_state('test_icon', ':material/radio_button_unchecked:')
    set_state('save_icon', ':material/radio_button_unchecked:')
    
    
    set_state('enable_generation', False)
    set_state('main_hierarchy', None)
    set_state('hierarchies', None)
    
    set_state('inc_count', -1)
    set_state('cor_count', -1)
    set_state('inc_policies', [])
    set_state('corrected_policies', [])
    set_state('corrected_policies_pdp', [])
    set_state('all_published', False)
    set_state('pdp_count', -1)
    set_state('pdp_policies', [])
    
    set_state('is_generating', False)
    set_state('written_nlacps', [])
    set_state('vs_generated', False)
    set_state('hierarchy_upload', None)
    set_state('policy_doc', None)
    set_state('do_align', True)
    set_state('generate_wo_context', False)
    set_state('reviewed', False)
    
    st.session_state.num_correct_policies = len(st.session_state.corrected_policies)
    st.session_state.num_incorrect_policies = len(st.session_state.inc_policies)
    
    set_state('start_title', 'Home')
    set_state('generate_doc_title', 'Generate from a Document')
    set_state('generate_single_title', 'Generate from a Sentence')
    set_state('cor_policies_title', f'Access Control Policies')
    set_state('inc_policies_title', f'Incorrect Access Control Policies')
    set_state('policy_viz_title', 'Visualize Policies')
    set_state('write_xacml_title', 'Write in XACML')
    set_state('policy_test_title', "Test Policies")
    set_state('policy_export_title', "Save Policies")
    set_state('started', False)
    set_state('new_doc', True)
    set_state('use_chroma', os.getenv('USE_CHROMA'))
    # set_state('show_hierarchy', True)

    set_state('current_page', PAGE.START)
    
    # if 'show_hierarchy' not in st.session_state:
    #     st.session_state.show_hierarchy = True
    # else:
    #     st.session_state.show_hierarchy = False
    
    if 'show_hierarchy' not in st.session_state:
        st.session_state.show_hierarchy = True
    else:
        st.session_state.show_hierarchy = False
        
    if 'first_time' not in st.session_state:
        st.session_state.first_time = True
    else:
        st.session_state.first_time = False
        
    if 'ac_engine' not in st.session_state:

        st.session_state["ac_engine"] = AccessControlEngine()
        
    if 'models' not in st.session_state:
        
        st.session_state['models'] = ModelStore(fake=False)
        
    st.session_state.xacml_uuid = str(uuid4())
    
    