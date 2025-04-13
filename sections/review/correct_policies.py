import streamlit as st
from loading import load_policy 
from ac_engine_service import AccessControlEngine
from sections.review.review_utils import publish_all, publish_policy
from sections.review.review_utils import get_updated_description
from models.pages import PAGE

@st.fragment
def show_correct_policies(ac_engine: AccessControlEngine):
    
    st.session_state.current_page = PAGE.CORRECT_POL
    
    # [data-testid="stVerticalBlock"] .st-key-table_container {
    #             position: fixed !important;
    #             top: 170px !important;
    #             overflow-y: auto !important;
    #         }
    
    st.markdown("""
        <style>
            /* Target the container with the specific key */
            [data-testid="stVerticalBlock"] .st-key-correct_container {
                position: fixed !important;
                bottom: -0.8% !important;
                background-color: white !important;
                padding-top: 10px !important;
                padding-bottom: 15px !important;
                z-index: 9999 !important;
            }
            
            
        
            /* Add padding at the bottom of the page to prevent content from being hidden */
            section.main {
                padding-bottom: 100px !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.title("Access Control Policies")
    
    cor_pol_container = st.container(border=False)
    
    
    for correct_pol_object in st.session_state.corrected_policies_pdp:
        
        with cor_pol_container.chat_message('user', avatar=":material/create:"):
            nlacp_col, btn_col = st.columns([7,1])
            publish_policy(correct_pol_object, ac_engine, btn_col)
            nlacp_col.markdown(get_updated_description(correct_pol_object))
            with st.expander("Generated Policy", expanded=False):
                corr_df = st.dataframe(load_policy(correct_pol_object.policy), use_container_width=True, key=f"correct_policy_{correct_pol_object.policyId}")
    
    
    
    with st.container(border=False, height=100, key="correct_container"):

        publish_all_btn = st.button(
            "Publish All",
            type="primary",
            use_container_width=True,
            key="publish_all",
            disabled=len(st.session_state.corrected_policies) < 1,
            help="Publish all the policies above to the policy database"
        )
        
        if publish_all_btn:
            publish_all(ac_engine)
            
        
ac_engine = AccessControlEngine()
show_correct_policies(ac_engine)