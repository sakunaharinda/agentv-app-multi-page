import streamlit as st
from hierarchy_visualizer import visualize_hierarchy_dialog
from what_to_do import show_page_help
import streamlit as st
from streamlit_authenticator.utilities import LoginError

def switch_login(arg):
    st.switch_page('pages/login.py')


def standard_menu():
    
    authenticator = st.session_state.authenticator
    
    st.markdown(f"""<style>
        
        /* Hide original header text */
        [data-testid="stSidebarHeader"] > div {{
            display: none;
        }}
        .st-key-fab button {{
                position: fixed;
                top: 50%;
                right: -3.0%;
                box-shadow: rgba(0, 0, 0, 0.16) 0px 4px 16px;
                z-index: 999;
                border-radius: 2rem;
                transform: rotate(90deg);
            }}
            
        [data-testid="stSidebarUserContent"] {{
                top: 50%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100%;
            }}
        [data-testid="stHeading"] {{
                position: fixed !important;
                top: 60px !important;
                left: auto !important; /* Don't use left: 0 */
                width: calc(100% - var(--sidebar-width, 21rem)) !important; /* Subtract sidebar width */
                margin-left: 0 !important;
                background-color: white !important;
                z-index: 999 !important;
                padding: 10px !important;
                
            }}
            
        .st-key-Logout {{
                position: fixed !important;
                bottom: 20px !important;
            }}
            
        
        /* Target the container with the specific key */
            
        
    </style>""", unsafe_allow_html=True)
    
    try:
        authenticator.login(location='unrendered')
    except LoginError as e:
        st.error(e)
        
    if st.session_state["authentication_status"]:
        st.sidebar.page_link("pages/get_started.py", label=st.session_state.start_title, icon=st.session_state.start_icon, disabled=st.session_state.is_generating)
        st.sidebar.write("**Policy Generation**")
        st.sidebar.page_link("pages/generate_document.py", label=st.session_state.generate_doc_title, icon=st.session_state.gen_doc_icon, disabled=st.session_state.is_generating or not st.session_state.hierarchy_upload)
        st.sidebar.page_link("pages/generate_individual.py", label=st.session_state.generate_single_title, icon=st.session_state.gen_sent_icon, disabled=st.session_state.is_generating or not st.session_state.hierarchy_upload)
        st.sidebar.page_link("pages/write_policy.py", label=st.session_state.write_xacml_title, icon=st.session_state.write_xacml_icon, disabled=st.session_state.is_generating or not st.session_state.hierarchy_upload)
        st.sidebar.write("**Policy Review**")
        st.sidebar.page_link("pages/correct_policies.py", label=st.session_state.cor_policies_title, icon=st.session_state.correct_pol_icon, disabled=st.session_state.is_generating or not st.session_state.hierarchy_upload)
        st.sidebar.page_link("pages/incorrect_policies.py", label=st.session_state.inc_policies_title, icon=st.session_state.incorrect_pol_icon, disabled=st.session_state.is_generating or not st.session_state.hierarchy_upload)
        st.sidebar.write("**Policy Testing**")
        st.sidebar.page_link("pages/policy_visualization.py", label=st.session_state.policy_viz_title, icon=st.session_state.viz_icon, disabled=st.session_state.is_generating or not st.session_state.hierarchy_upload)
        st.sidebar.page_link("pages/test_policies.py", label=st.session_state.policy_test_title, icon=st.session_state.test_icon, disabled=st.session_state.is_generating or not st.session_state.hierarchy_upload)
        st.sidebar.write("**Policy Exporting**")
        st.sidebar.page_link("pages/policy_export.py", label=st.session_state.policy_export_title, icon=st.session_state.save_icon, disabled=st.session_state.is_generating or not st.session_state.hierarchy_upload)
        
        st.button(label="What should I do?", icon=":material/help:", type='primary',key='fab', on_click=show_page_help)
        st.sidebar.container(height=10, border=False)
        h_btn = st.sidebar.button(":material/family_history: Organization Hierarchy", use_container_width=True, key='org_hierarchy', type='primary', disabled=(not st.session_state.hierarchies or st.session_state.is_generating))
        if h_btn:
            visualize_hierarchy_dialog()
        authenticator.logout(button_name=":material/logout: Logout", location='sidebar', use_container_width=True, callback=switch_login)