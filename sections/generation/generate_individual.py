import streamlit as st
from hierarchy_visualizer import visualize_hierarchy_expander
from utils import *
from models.record_dto import WrittenPolicy
from loading import load_policy
from ml_layer import agentv_single
from uuid import uuid4
from feedback import *

@st.fragment
def generate_sent(hierarchy, models):

    st.session_state['sentence_page'] = True
    st.session_state['document_page'] = False
    
    st.title("Policy Generation from a Sentence")

    # st.markdown(
    #         f"""
    #         <style>
    #             .st-key-fab button {{
    #                 position: fixed;
    #                 bottom: 0%;
    #                 box-shadow: rgba(0, 0, 0, 0.16) 0px 4px 16px;
    #                 z-index: 999;
    #                 border-radius: 2rem;
    #             }}
    #         </style>
    #         """,
    #         unsafe_allow_html=True,
    #     )

    visualize_hierarchy_expander(key='policy_sent_hierarchy')

    nlacp_container = st.container(height=330)

    for written_p in st.session_state.written_nlacps:
        with nlacp_container.chat_message("user", avatar=":material/create:"):
            st.markdown(written_p.sentence)
            if written_p.error == None:
                policy = load_policy(written_p.policy)
                with st.expander("Generated Policy", expanded=False):
                    st.dataframe(policy, use_container_width=True, key=written_p.id)
            else:
                st.error(body=written_p.error, icon="🚨")

    cur_nlacp = st.text_input(label="Enter the NLACP", label_visibility='collapsed', placeholder="E.g., The LHCP can read medical records.")
        
    generate_button = st.button(label='Generate', type='primary', key='generate_sent_btn', use_container_width=True, disabled=st.session_state.is_generating, on_click=on_click_generate, help=f"Click to start generating access control policies")

    if st.session_state.is_generating:

        if cur_nlacp == "":
            nlacp_container.error(
                "Please enter an access control requirement in natural language (i.e., English) before starting the generation.",
                icon="🚨",
            )
            st.rerun()
        else:
            st.session_state['is_generating'] = True
            
            with nlacp_container.chat_message("user", avatar=":material/create:"):
                st.markdown(cur_nlacp)
        
            agentv_single(nlacp_container, cur_nlacp, models.id_tokenizer, models.id_model, models.gen_tokenizer, models.gen_model, models.ver_model, models.ver_tokenizer, models.loc_tokenizer, models.loc_model, models.vectorestores, hierarchy, True)
            
            if len(st.session_state.results_individual['interrupted_errors']) > 0:
                st.session_state.written_nlacps.append(
                    WrittenPolicy(
                        id = str(uuid4()),
                        sentence=cur_nlacp,
                        policy=[],
                        error=st.session_state.results_individual['interrupted_errors'][0]
                    )
                )
                
            else:
            
                st.session_state.written_nlacps.append(
                    WrittenPolicy(
                        id = str(uuid4()),
                        sentence=cur_nlacp,
                        policy=st.session_state.results_individual['final_policies'][0]
                    )
                )
            
            st.rerun()
            
            
hierarchy = st.session_state.hierarchies
models = st.session_state.models

generate_sent(hierarchy, models)

            
        