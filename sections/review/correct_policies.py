import streamlit as st
from handlers import pdp_policy_nav_next 
from ac_engine_service import AccessControlEngine
from sections.review.review_utils import publish_all, publish_policy, policy_db_feedback
from utils import change_page_icon
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
    
    cor_pol_container = st.container(border=False, height=500, key="table_container")
    
    
    for correct_pol_object in st.session_state.corrected_policies:
        
        with cor_pol_container.chat_message('user', avatar=":material/create:"):
            publish_policy(correct_pol_object, ac_engine)
            st.markdown(correct_pol_object.policyDescription)
            with st.expander("Generated Policy", expanded=False):
                corr_df = st.dataframe(correct_pol_object.policy, use_container_width=True, key="correct_policies")
    
    
    
    with st.container(border=False, height=100, key="correct_container"):

        publish_all_btn = st.button(
            "Publish All Policies to Database",
            type="primary",
            use_container_width=True,
            key="publish_all",
            disabled=len(st.session_state.corrected_policies) < 1,
        )
        
                
        if publish_all_btn:
            change_page_icon('correct_pol_icon')
            status = publish_all(ac_engine)
            
            if status == 200:
                
                st.session_state.pdp_policies.extend(st.session_state.corrected_policies)
                st.session_state.pdp_policies = list(set(st.session_state.pdp_policies))
                pdp_policy_nav_next()
            
            policy_db_feedback(status)
            
        
ac_engine = AccessControlEngine()
show_correct_policies(ac_engine)