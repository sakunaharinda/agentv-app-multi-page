import streamlit as st
from loading import load_policy
from pages.policy_tester import PolicyTester
from pages.testing_utils import test_policy, test_system
from pages.review_utils import filter
from ac_engine_service import AccessControlEngine
from models.pages import PAGE
from menus import standard_menu
from hierarchy_visualizer import visualize_hierarchy_dialog, set_hierarchy
from init_ui import init

@st.fragment
def test_policies():
    
    st.markdown("""
        <style>
            /* Target the container with the specific key */
            [data-testid="stVerticalBlock"] .st-key-test_container {
                position: fixed !important;
                bottom: 0.0% !important;
                background-color: #F9F9F9 !important;
                padding-top: 10px !important;
                padding-bottom: 20px !important;
                z-index: 9999 !important;
            }
            
            [data-testid="stVerticalBlock"] .st-key-filter_container_test {
                position: fixed !important;
                top: 140px !important;
                padding-top: 20px !important;
                background-color: #F9F9F9 !important;
                padding-bottom: 10px !important;
                z-index: 9999 !important;
            }
            
            [data-testid="stVerticalBlock"] .st-key-pad_container_test {
                position: fixed !important;
                top: 180px !important;
            }
            
            
            /* Add padding at the bottom of the page to prevent content from being hidden */
            section.main {
                padding-bottom: 100px !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.session_state.current_page = PAGE.TEST_POLICY
    
    st.title("Test Policies")
    
    filter_container = st.container(border=False, key='filter_container_test')
    
    policies_from_pdp = filter(st.session_state.pdp_policies, filter_container)

    st.container(border=False, key='pad_container_test', height=50)
    
    pdp_pol_container = st.container(border=False, key='pdp_container')
    # pdp_policies = st.session_state.pdp_policies
    
    if len(st.session_state.pdp_policies) > 0:
        for pdp_pol_object in policies_from_pdp:
            
            with pdp_pol_container.chat_message('user', avatar=":material/gavel:"):
                nlacp_col, btn_col = st.columns([7,1])
                test_policy(pdp_pol_object, st.session_state.policy_tester, btn_col)
                nlacp_col.markdown(f"Policy Id: {pdp_pol_object.policyId}")
                st.markdown("**" + pdp_pol_object.policyDescription + (" :red-badge[:material/family_history: Outside context]" if not pdp_pol_object.with_context else "") + "**")
                with st.expander(f"Generated Policy", expanded=False):
                    st.dataframe(load_policy(pdp_pol_object.policy), use_container_width=True, key=f"pdp_policy_{pdp_pol_object.policyId}", hide_index=True)
    else:
        
        pdp_pol_container.info(icon=":material/info:", body="You don't have access control policies published to test. Please go to the **:material/verified_user: Access Control Policies** page, publish the access control policies, and come back.")

    test_container = st.container(key="test_container")
    with test_container:
        col,_,_ = st.columns([1,1,1])
        col.write(f"{len(policies_from_pdp)}/{len(st.session_state.pdp_policies)} records are shown.")
        test_sys = st.button(
            "Test with all Policies",
            type="primary",
            help="Test by sending an access request to the entire policy database",
            use_container_width=True,
            key="test_all",
            disabled=len(st.session_state.pdp_policies) < 1,
            # on_click=test_system,
            # args=(policy_tester,),
            icon=":material/output:"
        )
        
        
        if test_sys:
            test_system(st.session_state.policy_tester)
    if st.session_state.test_overall:
        st.session_state.test_overall = False
        st.session_state.policy_tester.test_overall()


if 'new_session' not in st.session_state:
    init()
    set_hierarchy('data/Hierarchies.yaml')
    visualize_hierarchy_dialog()

hierarchy = st.session_state.hierarchies

standard_menu()

ac_engine = AccessControlEngine()
st.session_state.policy_tester = PolicyTester(hierarchy, ac_engine)
test_policies()