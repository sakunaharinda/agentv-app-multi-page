import streamlit as st
from utils import on_click_generate
from ml_layer import agentv_batch
from sections.generation.generation_utils import generating_wo_hierarchy, show_summary, review_incorrects
import time

@st.fragment
def generate_doc(hierarchy, models):

    st.session_state['document_page'] = True
    st.session_state['sentence_page'] = False
    # st.markdown(
    #         f"""
    #         <style>
    #             .st-key-fab button {{
    #                 position: fixed;
    #                 top: 50%;
    #                 box-shadow: rgba(0, 0, 0, 0.16) 0px 4px 16px;
    #                 z-index: 999;
    #                 border-radius: 2rem;
    #             }}
    #         </style>
    #         """,
    #         unsafe_allow_html=True,
    #     )

    st.title("Policy Generation from a Document")

    # visualize_hierarchy_expander(key='policy_doc_hierarchy')


    # with st.container(border=True, height=210) as status:
    status_container = st.container(border=False, height=305)
    
    with st.container(border=False, height=162):
        policy_doc = st.file_uploader("Upload a high-level requirement specification document", key='policy_doc', help='Upload a high-level requirement specification document written in natural language (i.e., English), that specifies who can access what information in the organization.', type=['md'])

    generate_button = st.button(label='Generate', type='primary', key='generate_doc_btn', use_container_width=True, disabled=st.session_state.is_generating, on_click=on_click_generate, help=f"Click to start generating access control policies")

    if st.session_state.is_generating:

        if policy_doc is None:
            status_container.error(
                "Please upload a high-level requirement specification document before starting the generation.",
                icon="🚨",
            )
            st.session_state.is_generating = False
        else:
            # if st.session_state.hierarchy_upload == None and not st.session_state.generate_wo_context:
                
            #     generating_wo_hierarchy()
                
            # else:
                
            content = policy_doc.getvalue().decode('utf-8')
        
            agentv_batch(status_container, content, models.id_tokenizer, models.id_model, models.gen_tokenizer, models.gen_model, models.ver_model, models.ver_tokenizer, models.loc_tokenizer, models.loc_model, models.vectorestores, hierarchy, do_align=st.session_state.do_align)
            
            # st.session_state.generate_wo_context = False
            # st.rerun()
            incorrects = len(st.session_state.results_document['final_verification'])-st.session_state.results_document['final_verification'].count(11)
            if (not st.session_state.reviewed) and incorrects>0:
                review_incorrects(incorrects)
            
    
    show_summary(status_container)
    

hierarchy = st.session_state.hierarchies
models = st.session_state.models

generate_doc(hierarchy, models)