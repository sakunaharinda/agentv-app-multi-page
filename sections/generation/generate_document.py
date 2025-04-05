import streamlit as st
from hierarchy_visualizer import visualize_hierarchy_expander
from utils import *
from ml_layer import agentv_batch


@st.fragment
def generate_doc(hierarchy, models):

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

    st.title("Policy Generation")

    visualize_hierarchy_expander(key='policy_doc_hierarchy')

    with st.container(border=False, height=155):
        policy_doc = st.file_uploader("Upload a high-level requirement specification document", key='policy_doc', help='Upload a high-level requirement specification document written in natural language (i.e., English), that specifies who can access what information in the organization.', type=['md'])


    # with st.container(border=True, height=210) as status:
    status_container = st.container(border=False, height=215)

    generate_button = st.button(label='Generate', type='primary', key='generate_doc_btn', use_container_width=True, disabled=st.session_state.is_generating, on_click=on_click_generate, help=f"Click to start generating access control policies")

    if st.session_state.is_generating:

        if policy_doc is None:
            st.error(
                "Please upload a high-level requirement specification document before starting the generation.",
                icon="🚨",
            )
        else:
            st.session_state['is_generating'] = True
            content = policy_doc.getvalue().decode('utf-8')
        
            agentv_batch(status_container, content, models.id_tokenizer, models.id_model, models.gen_tokenizer, models.gen_model, models.ver_model, models.ver_tokenizer, models.loc_tokenizer, models.loc_model, models.vectorestores, hierarchy, do_align=True)
            st.rerun()
            
    
    summary = get_summary()
    status_container.text_area("Summary", summary, help=f"A summary of the completed access control policy generation process, outlining the total number of sentences found in the input document, the number of access control requirement found among the sentences, the number of correctly translated access control requirements into structured access control policies (See **Correct Policies** tab), and the number of failed translations (See **Incorrect Policies** tab)",disabled=True, height=150)
            

hierarchy = st.session_state.hierarchies
models = st.session_state.models

generate_doc(hierarchy, models)