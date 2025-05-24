import streamlit as st
from models.pages import PAGE
from pages.review_utils import get_updated_description_inc, review_policy, review_policy_aggrid
from menus import standard_menu
from feedback import get_locate_warning_msg
from uuid import uuid4

@st.fragment
def show_incorrect_policies(models, hierarchy):
    
    ADD_INC = False
    
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
            
            [data-testid=stToastContainer] {
                z-index: 9999 !important;
                //position: fixed !important;
                //top: 30% !important;
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
    
    if len(st.session_state.inc_policies)>0:
    
        for incorrect_pol_object in st.session_state.inc_policies:
            
            if incorrect_pol_object['solved'] == False:
                break
        else:
            st.toast("All the policies are refined successfully. Go to **Access Control Policies** page to review and publish.", icon=":material/check:")
            
    if ADD_INC and len(st.session_state.inc_policies) == 0:
        
        inc_policy = [
            {
                'decision': 'deny',
                'subject': 'lhcp',
                'action': 'access',
                'resource': 'medical record',
                'purpose': 'protect patient confidentiality',
                'condition': 'none'
            },
            {
                'decision': 'deny',
                'subject': 'administrator',
                'action': 'access',
                'resource': 'medical record',
                'purpose': 'protect patient confidentiality',
                'condition': 'none'
            }
        ]
        
        warning = get_locate_warning_msg('incorrect subject', [0])
        st.session_state.inc_policies.append(
            {
                "id": str(uuid4()),
                "nlacp": "Medical records cannot be accessed either by LTs or administrators, to protect patient confidentiality.",
                "policy": inc_policy,
                "warning": warning,
                "solved": False,
                "show": True
            }
        )
    
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