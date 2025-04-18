import streamlit as st
from models.pages import PAGE
from pages.review_utils import get_updated_description_inc, review_policy, review_policy_aggrid
from menus import standard_menu

@st.fragment
def show_incorrect_policies(models, hierarchy):
    
    st.session_state.current_page = PAGE.INCORRECT_POL
    
    st.markdown("""
        <style>
            /* Target the container with the specific key */
            [data-testid="stVerticalBlock"] .st-key-incorrect_container {
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
            .ag-center-cols-viewport {
                min-height: unset !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.title("Incorrect Access Control Policies")
    
    inc_policy_container = st.container(key='inc_pol_container')
    
    for incorrect_pol_object in st.session_state.inc_policies:
        
        with inc_policy_container.chat_message('user', avatar=":material/dangerous:"):
            st.markdown(f"**Policy Id: {incorrect_pol_object['id']}**")
            st.markdown(get_updated_description_inc(incorrect_pol_object))
            with st.expander("Errorneous Policy", expanded=incorrect_pol_object['show']):
                warning, info = incorrect_pol_object["warning"]
                st.error(warning)
                # review_policy(incorrect_pol_object, hierarchy, models)
                review_policy_aggrid(incorrect_pol_object, info, hierarchy, models)

        
hierarchy = st.session_state.hierarchies
models = st.session_state.models

standard_menu()

show_incorrect_policies(models, hierarchy)