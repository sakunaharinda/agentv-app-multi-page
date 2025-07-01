import streamlit as st
from hierarchy_visualizer import visualize_hierarchy_dialog
from what_to_do import show_page_help
import streamlit as st
# from streamlit_authenticator.utilities import LoginError

def switch_login(arg):
    st.switch_page('pages/login.py')
    
    
def update_nav_lable(init_lable, var, badge = 'error'):
    if var > 0:
        return init_lable + f' :material/{badge}:'
    else:
        return init_lable


def standard_menu(turn_on=True):
    
    # authenticator = st.session_state.authenticator
    
    st.markdown(f"""<style>
        
        /* Hide original header text */
        [data-testid="stSidebarHeader"] > div {{
            display: none;
        }}
        //[data-testid="stSidebarUserContent"] {{
        //       top: 50%;
        //        display: flex;
        //        flex-direction: column;
        //        justify-content: center;
        //        align-items: center;
        //        height: 100%;
        //    }}
        .st-key-fab button {{
                position: fixed;
                bottom: 20px;
                right: 1%;
                box-shadow: rgba(0, 0, 0, 0.16) 0px 4px 16px;
                z-index: 999;
                border-radius: 4rem;
                //transform: rotate(90deg);
            }}
            
        
        [data-testid="stHeading"] {{
                position: fixed !important;
                top: 60px !important;
                left: auto !important; /* Don't use left: 0 */
                width: calc(100% - var(--sidebar-width, 21rem)) !important; /* Subtract sidebar width */
                margin-left: 0 !important;
                background-color: #F9F9F9 !important;
                z-index: 999 !important;
                padding: 10px !important;
                
            }}
            
        .st-key-org_hierarchy {{
                position: fixed !important;
                bottom: 20px !important;
            }}
            
        img[data-testid="stLogo"] {{
            height: 3.5rem;
            }}
        [data-testid="stSidebar"] .st-key-Logout,
        .css-1d391kg .st-key-Logout,
        section[data-testid="stSidebar"] .st-key-Logout {{
            position: absolute !important;
            top: -15.5% !important;
            right: -1px !important; /* 1cm from right edge */
            z-index: 999 !important;
        }}

        /* Ensure sidebar has positioning context */
        [data-testid="stSidebar"],
        .css-1d391kg,
        section[data-testid="stSidebar"] {{
            position: relative !important;
        }}
            
        
    </style>""", unsafe_allow_html=True)
    
    # try:
    #     authenticator.login(location='unrendered')
    # except LoginError as e:
    #     st.error(e)
        
    # if st.session_state["authentication_status"]:
        
    st.logo("images/logo2.png", size='large')
    st.sidebar.container(height=20, border=False)
    st.sidebar.page_link("pages/get_started.py", label=st.session_state.start_title, icon=":material/home:", disabled=st.session_state.is_generating)
    st.sidebar.write("**Policy Generation**")
    st.sidebar.page_link("pages/generate_document.py", label=st.session_state.generate_doc_title, icon=":material/article:", disabled=st.session_state.is_generating or not turn_on)
    st.sidebar.page_link("pages/generate_individual.py", label=st.session_state.generate_single_title, icon=":material/create:", disabled=st.session_state.is_generating or not turn_on)
    # st.sidebar.page_link("pages/write_policy.py", label=st.session_state.write_xacml_title, icon=":material/code:", disabled=st.session_state.is_generating or not turn_on)
    st.sidebar.write("**Policy Review**")
    st.sidebar.page_link("pages/incorrect_policies.py", label=st.session_state.inc_policies_title, icon=":material/gpp_bad:", disabled=st.session_state.is_generating or not turn_on)
    st.sidebar.page_link("pages/correct_policies.py", label=st.session_state.cor_policies_title, icon=":material/verified_user:", disabled=st.session_state.is_generating or not turn_on)
    st.sidebar.write("**Policy Testing**")
    st.sidebar.page_link("pages/policy_visualization.py", label=st.session_state.policy_viz_title, icon=":material/bar_chart:", disabled=st.session_state.is_generating or not turn_on)
    st.sidebar.page_link("pages/test_policies.py", label=st.session_state.policy_test_title, icon=":material/assignment:", disabled=st.session_state.is_generating or not turn_on)
    st.sidebar.write("**Policy Exporting**")
    st.sidebar.page_link("pages/policy_export.py", label=st.session_state.policy_export_title, icon=":material/download:", disabled=st.session_state.is_generating or not turn_on)
    
    help = st.button(label="", icon=":material/help:", type='primary',key='fab')
    
    if help:
        show_page_help()
    
    
    st.sidebar.container(height=10, border=False)
    h_btn = st.sidebar.button(":material/family_history: Organization Hierarchy", use_container_width=True, key='org_hierarchy', type='primary', disabled=st.session_state.is_generating)
                                
                            #   disabled=(not st.session_state.hierarchies or st.session_state.is_generating or not ('hierarchy_upload' in st.session_state and st.session_state.hierarchy_upload!=None) or st.session_state.no_hierarchy)
                                
    if h_btn:
        visualize_hierarchy_dialog()
    # authenticator.logout(button_name=":material/logout: Logout", location='sidebar', use_container_width=False, callback=switch_login)