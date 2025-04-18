import streamlit as st
from loading import load_policy 
from ac_engine_service import AccessControlEngine
from pages.review_utils import publish_all, publish_delete_policy, get_updated_description
from models.pages import PAGE
from menus import standard_menu

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
                background-color: white !important;
                padding-top: 10px !important;
                padding-bottom: 20px !important;
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
        
        with cor_pol_container.chat_message('user', avatar=":material/gavel:"):
            nlacp_col, btn_col, cancel_col = st.columns([7,1.5, 1.7])
            publish_delete_policy(correct_pol_object, ac_engine, btn_col, cancel_col)
            nlacp_col.markdown(f"**Policy Id: {correct_pol_object.policyId}**")
            st.markdown(get_updated_description(correct_pol_object))
            cbox, expander = st.columns([1,70])
            ready_publish = cbox.checkbox(label="Ready to publish", label_visibility='collapsed', key=f'publish_cbox_{correct_pol_object.policyId}', disabled=correct_pol_object.published, value=correct_pol_object.published)
            if ready_publish and not correct_pol_object.published:
                correct_pol_object.ready_to_publish = True
                select_count+=1
            else:
                correct_pol_object.ready_to_publish = False
            with expander.expander("Generated Policy", expanded=False):
                corr_df = st.dataframe(load_policy(correct_pol_object.policy), use_container_width=True, key=f"correct_policy_{correct_pol_object.policyId}", hide_index=True)
    
    # print('rerun')
    if select_count == 0 or select_count == len(st.session_state.corrected_policies_pdp):
        MODE = 'All'
    else:
        MODE = f"({select_count})"
    
    with st.container(border=False, height=100, key="correct_container"):

        publish_all_btn = st.button(
            f"Publish {MODE}",
            type="primary",
            use_container_width=True,
            key="publish_all",
            disabled=len(st.session_state.corrected_policies) < 1,
            help="Publish all the policies above to the policy database",
            icon=":material/database_upload:",
            on_click=publish_all,
            args=(ac_engine, select_count,)
        )
        
        if publish_all_btn and MODE == 'All':
            st.switch_page("pages/test_policies.py")
            
standard_menu()
ac_engine = AccessControlEngine()
show_correct_policies(ac_engine)