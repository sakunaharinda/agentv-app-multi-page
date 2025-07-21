import streamlit as st
from utils import *
from models.ac_engine_dto import WrittenPolicy
from loading import load_policy
from ml_layer import agentv_single
from uuid import uuid4
from pages.generation_utils import review_individual, get_updated_description
from models.pages import PAGE
from ac_engine_service import AccessControlEngine
from menus import standard_menu
from hierarchy_visualizer import visualize_hierarchy_dialog, set_hierarchy
from init_ui import init

# @st.fragment
def generate_sent(hierarchy, models, ac_engine: AccessControlEngine):
    
    st.session_state.current_page = PAGE.GEN_SENT
    
    st.markdown("""
        <style>
            /* Target the container with the specific key */
            [data-testid="stVerticalBlock"] .st-key-individual_container {
                position: fixed !important;
                bottom: 0.0% !important;
                background-color: #F9F9F9 !important;
                padding-top: 10px !important;
                padding-bottom: 20px !important;
                z-index: 9999 !important;
            }
            
            [data-testid=stToastContainer] {
                z-index: 9999 !important;
                //position: fixed !important;
                //top: 30% !important;
            }
            
            /* Add padding at the bottom of the page to prevent content from being hidden */
            section.main {
                padding-bottom: 100px !important;
            }
        </style>
        """, unsafe_allow_html=True)

    st.session_state['sentence_page'] = True
    st.session_state['document_page'] = False
    
    if st.session_state.show_ask_hierarchy_dialog or st.session_state.hierarchies==None:
        visualize_hierarchy_dialog()
    
    st.title("Policy Generation from a Sentence")

    nlacp_container = st.container(border=False)

    for written_p in st.session_state.written_nlacps:
        with nlacp_container.chat_message("user", avatar=":material/create:"):
            st.markdown(f"Policy Id: {written_p.id}")
            st.markdown(get_updated_description(written_p))
            if written_p.error == "":
                policy = load_policy(written_p.policy)
                with st.expander("Generated Policy", expanded=False):
                    st.dataframe(policy, use_container_width=True, key=f'df_{written_p.id}', hide_index=True)
                    review_individual(written_p)
            else:
                st.error(body=written_p.error, icon=":material/dangerous:")

    footer_container = st.container(key='individual_container')
    
    with footer_container:
        cur_nlacp = st.text_input(label="Enter an access control requirement", help="Write a high-level access control requirement in natural language (i.e., English)", label_visibility='visible', placeholder="E.g., The LHCP can read medical records.")
            
        generate_button = st.button(label='Generate', type='primary', key='generate_sent_btn', use_container_width=True, disabled=st.session_state.is_generating, help=f"Click to start generating access control policies", icon=":material/play_circle:", on_click=on_click_generate, args=('gen_sent_icon',))
        
        # if generate_button:
        #     st.session_state.is_generating = True
        #     st.session_state.new_doc = False

    if st.session_state.is_generating:
        

        if cur_nlacp == "":
            nlacp_container.error(
                "Please enter an access control requirement in natural language (i.e., English) before starting the generation.",
                icon=":material/dangerous:",
            )
            st.session_state.is_generating = False

        else:
            
            with nlacp_container.chat_message("user", avatar=":material/create:"):
                st.markdown(cur_nlacp)
        
            uuid = agentv_single(nlacp_container, cur_nlacp, models.id_tokenizer, models.id_model, models.gen_tokenizer, models.gen_model, models.ver_model, models.ver_tokenizer, models.loc_tokenizer, models.loc_model, models.vectorestores, hierarchy, do_align=st.session_state.do_align)
            
            if len(st.session_state.results_individual['interrupted_errors']) > 0:
                written_policy = WrittenPolicy.from_dict({
                        "id": uuid,
                        "sentence": cur_nlacp,
                        "policy": [],
                        "error": st.session_state.results_individual['interrupted_errors'][0],
                        "is_incorrect": True,
                        "is_reviewed": False
                    })
                st.session_state.written_nlacps.append(
                    written_policy
                )
                
            else:
                
                written_policy = WrittenPolicy.from_dict({
                        "id": uuid,
                        "sentence": cur_nlacp,
                        "policy": st.session_state.results_individual['final_policies'][0],
                        "error": "",
                        "is_incorrect": st.session_state.results_individual['final_verification'][0]!=11,
                        "is_reviewed": False
                    })
            
                st.session_state.written_nlacps.append(
                    written_policy
                )
            
            ac_engine.create_written_policy_json(written_policy)

            st.rerun()
            
if 'new_session' not in st.session_state:
    init()
    set_hierarchy('data/Hierarchies.yaml')
    visualize_hierarchy_dialog()

hierarchy = st.session_state.hierarchies
models = st.session_state.models
ac_engine = AccessControlEngine()
standard_menu()
generate_sent(hierarchy, models, ac_engine)

            
        