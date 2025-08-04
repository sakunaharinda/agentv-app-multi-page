import streamlit as st
from utils import on_click_generate, store_value_pol_doc
from ml_layer import agentv_batch
from pages.generation_utils import show_summary, review_incorrects, show_bar_chart, review_incorrects_notification
from models.pages import PAGE
from menus import standard_menu
from feedback import success_generation_feedback, failed_generation_feedback
from hierarchy_visualizer import visualize_hierarchy_dialog
from init_ui import init
from hierarchy_visualizer import set_hierarchy
import yaml

# @st.fragment
def generate_doc(hierarchy, models):
    
    st.session_state.current_page = PAGE.GEN_DOC
    
    st.markdown("""
        <style>
            /* Target the container with the specific key */
            [data-testid="stVerticalBlock"] .st-key-doc_container {
                position: fixed !important;
                bottom: 0.0% !important;
                background-color: #F9F9F9 !important;
                padding-top: 10px !important;
                padding-bottom: 20px !important;
                z-index: 9999 !important;
            }
            
            [data-testid=stToastContainer] {
                z-index: 9999 !important;
            }
            
            //div[data-testid=stToast] {
            //    background-color: #E6F2E9;
            //}
            
            /* Add padding at the bottom of the page to prevent content from being hidden */
            section.main {
                padding-bottom: 100px !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
    if (st.session_state.show_ask_hierarchy_dialog_document) and st.session_state.hierarchies==None:
        st.session_state.show_ask_hierarchy_dialog_document = False
        visualize_hierarchy_dialog()

    st.session_state['document_page'] = True
    st.session_state['sentence_page'] = False

    st.title("Policy Generation from a Document")
    st.container(height=1, border=False)
    status_container = st.container(border=False, height=173)
    barchart = st.container(border=False, height=145)
    
    footer_container = st.container(key='doc_container')
    
    with footer_container:
    
        with st.container(border=False, height=162):
            policy_doc = st.file_uploader("Upload the provided high-level requirement specification document", key='_policy_doc', help='Upload a high-level requirement specification document provided to you. It specifies who can access what information under what circumstances in the organization.', type=['md'], on_change=store_value_pol_doc, args=('policy_doc',), disabled=st.session_state.is_generating)

        generate_button = st.button(label='Generate', type='primary', key='generate_doc_btn', use_container_width=True, disabled=st.session_state.is_generating or policy_doc == None, on_click=on_click_generate, args=('gen_doc_icon',), help=f"Click to start generating access control policies from the uploaded high-level requirement specification document", icon=":material/play_circle:")

    if st.session_state.is_generating:

        if st.session_state.policy_doc is None:
            status_container.error(
                "Please upload a high-level requirement specification document before starting the generation.",
                icon=":material/dangerous:",
            )
            st.session_state.is_generating = False
            # st.rerun()
        else:
            # if st.session_state.hierarchy_upload == None and not st.session_state.generate_wo_context:
                
            #     generating_wo_hierarchy()
                
            # else:
            # TODO: Add document editing    
            content = st.session_state.policy_doc.getvalue().decode('utf-8')
            agentv_batch(status_container, content, models.id_tokenizer, models.id_model, models.gen_tokenizer, models.gen_model, models.ver_model, models.ver_tokenizer, models.loc_tokenizer, models.loc_model, models.vectorestores, hierarchy, do_align=st.session_state.do_align)
            
            
            st.session_state.is_generating = False
            if st.session_state.refresh:
                st.session_state.refresh = False
                st.rerun()

    if 'results_document' in st.session_state:
    
        incorrects = len(st.session_state.results_document['final_verification'])-st.session_state.results_document['final_verification'].count(11)
        if (not st.session_state.reviewed) and incorrects>0:
            
            # review_incorrects_notification(incorrects)
            
            failed_generation_feedback()
            st.session_state.reviewed = True

        elif (not st.session_state.reviewed) and incorrects==0:
            
            # st.toast("Policies are generated successfully. Go to **Access Control Policies** page to review and publish.",icon=":material/check:")
            
            success_generation_feedback(mode='multiple')
            st.session_state.reviewed = True
    
    if 'results_document' in st.session_state and not st.session_state.new_doc:
        show_summary(status_container)
        show_bar_chart(barchart)
        
    
    # footer_container.float("bottom: 10px;")
if 'new_session' not in st.session_state:
    init()
    set_hierarchy('data/Hierarchies.yaml')
    visualize_hierarchy_dialog()
    

hierarchy = st.session_state.hierarchies
models = st.session_state.models

standard_menu()
generate_doc(hierarchy, models)