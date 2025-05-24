import streamlit as st
from loading import load_policy
from pages.policy_tester import PolicyTester
from pages.testing_utils import test_policy, test_system
from pages.review_utils import filter
from ac_engine_service import AccessControlEngine
from models.pages import PAGE
from menus import standard_menu

@st.fragment
def test_policies(policy_tester: PolicyTester):
    
    st.markdown("""
        <style>
            /* Target the container with the specific key */
            [data-testid="stVerticalBlock"] .st-key-test_container {
                position: fixed !important;
                bottom: 0.0% !important;
                background-color: white !important;
                padding-top: 10px !important;
                padding-bottom: 20px !important;
                z-index: 9999 !important;
            }
            
            [data-testid="stVerticalBlock"] .st-key-filter_container_test {
                position: fixed !important;
                top: 140px !important;
                padding-top: 20px !important;
                background-color: white !important;
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
    for pdp_pol_object in policies_from_pdp:
        
        with pdp_pol_container.chat_message('user', avatar=":material/gavel:"):
            nlacp_col, btn_col = st.columns([7,1])
            test_policy(pdp_pol_object, policy_tester, btn_col)
            nlacp_col.markdown(f"**Policy Id: {pdp_pol_object.policyId}**")
            st.markdown(pdp_pol_object.policyDescription + (" :red-badge[:material/family_history: Outside context]" if not pdp_pol_object.with_context else ""))
            with st.expander(f"Generated Policy", expanded=False):
                st.dataframe(load_policy(pdp_pol_object.policy), use_container_width=True, key=f"pdp_policy_{pdp_pol_object.policyId}", hide_index=True)

    test_container = st.container(key="test_container")
    with test_container:

        test_sys = st.button(
            "Test All",
            type="primary",
            help="Test all the policies by sending an access request",
            use_container_width=True,
            key="test_all",
            disabled=len(st.session_state.pdp_policies) < 1,
            # on_click=test_system,
            # args=(policy_tester,),
            icon=":material/output:"
        )
        
        if test_sys:
            test_system(policy_tester)

hierarchy = st.session_state.hierarchies

standard_menu()

ac_engine = AccessControlEngine()
policy_tester = PolicyTester(hierarchy, ac_engine)
test_policies(policy_tester)