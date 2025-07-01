import streamlit as st
from loading import load_policy
from ac_engine_service import AccessControlEngine
from pages.review_utils import publish_all, publish_delete_policy, get_updated_description, filter
from models.pages import PAGE
from menus import standard_menu
from init_ui import init
from hierarchy_visualizer import set_hierarchy, visualize_hierarchy_dialog
    

@st.fragment
def show_correct_policies(ac_engine: AccessControlEngine):
    select_count = 0
    
    st.session_state.current_page = PAGE.CORRECT_POL
    
    st.markdown("""
        <style>
            /* Target the container with the specific key */
            [data-testid="stVerticalBlock"] .st-key-correct_container {
                position: fixed !important;
                bottom: 0.0% !important;
                background-color: #F9F9F9 !important;
                padding-top: 10px !important;
                padding-bottom: 20px !important;
                z-index: 9999 !important;
            }
            
            [class*="st-key-remove_"] button {
                background-color: #EA4335;
                border: none;
            }
            [class*="st-key-remove_"] button:hover {
                background-color: #DC143C;
                border: none;
            }
            
            [data-testid="stVerticalBlock"] .st-key-filter_container {
                position: fixed !important;
                top: 140px !important;
                padding-top: 20px !important;
                background-color: #F9F9F9 !important;
                padding-bottom: 10px !important;
                z-index: 9999 !important;
            }
            
            [data-testid="stVerticalBlock"] .st-key-pad_container {
                position: fixed !important;
                top: 180px !important;
                //background-color: #F9F9F9 !important;
                //z-index: 9999 !important;
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
        </style>
        """, unsafe_allow_html=True)
    
    st.title("Access Control Policies")
    
    filter_container = st.container(border=False, key='filter_container')
    
    # expander, info = filter_container.columns([10,2])
    
    policies_to_pdp = filter(st.session_state.corrected_policies_pdp, filter_container)

    st.container(border=False, key='pad_container', height=40)
        
    # info.write(f"{len(policies_to_pdp)}/{len(st.session_state.corrected_policies_pdp)} records are shown")
    
    cor_pol_container = st.container(border=False)
    
    overall_select_count = 0
        
    
    for correct_pol_object in policies_to_pdp:

        with cor_pol_container.chat_message('user', avatar=":material/gavel:"):
            nlacp_col, btn_col, cancel_col = st.columns([7,1.5, 1.7])
            publish_delete_policy(correct_pol_object, ac_engine, btn_col, cancel_col)
            nlacp_col.markdown(f"Policy Id: {correct_pol_object.policyId}")
            st.markdown(get_updated_description(correct_pol_object))
            cbox, expander = st.columns([1,70])
            ready_publish = cbox.checkbox(label="Ready to publish", label_visibility='collapsed', key=f'publish_cbox_{correct_pol_object.policyId}', disabled=correct_pol_object.published, value=(correct_pol_object.published or correct_pol_object.ready_to_publish))
            if ready_publish:
                correct_pol_object.ready_to_publish = True
            else:
                correct_pol_object.ready_to_publish = False
            with expander.expander("Generated Policy", expanded=False):
                corr_df = st.dataframe(load_policy(correct_pol_object.policy), use_container_width=True, key=f"correct_policy_{correct_pol_object.policyId}", hide_index=True)
                
    for overall_correct_pol_object in st.session_state.corrected_policies_pdp:
        if overall_correct_pol_object.ready_to_publish and not overall_correct_pol_object.published:
                # correct_pol_object.ready_to_publish = True
            overall_select_count+=1
    
    # print('rerun')
    
    if overall_select_count == 0:
        if len(policies_to_pdp) == len(st.session_state.corrected_policies_pdp):
            MODE = "All"
        else:
            MODE = "Shown"
    else:
        MODE = f"({overall_select_count})"
        
    correct_container = st.container(key="correct_container")
    
    with correct_container:
        col,_,_ = st.columns([1,1,1])
        col.write(f"{len(policies_to_pdp)}/{len(st.session_state.corrected_policies_pdp)} records are shown.")
        publish_all_btn = st.button(
            f"Publish {MODE}",
            type="primary",
            use_container_width=True,
            key="publish_all",
            disabled=len(policies_to_pdp) < 1,
            help="Publish the all/shown the policies to AGentV's policy database.",
            icon=":material/database_upload:",
            on_click=publish_all,
            args=(ac_engine, overall_select_count, policies_to_pdp,)
        )
        
        # if publish_all_btn:
        #     publish_all(ac_engine, overall_select_count, policies_to_pdp)
        
        # if publish_all_btn and MODE == 'All':
            # st.switch_page("pages/test_policies.py")
if 'new_session' not in st.session_state:
    init()
    set_hierarchy('data/Hierarchies.yaml')
    visualize_hierarchy_dialog()

standard_menu()
ac_engine = AccessControlEngine()
show_correct_policies(ac_engine)