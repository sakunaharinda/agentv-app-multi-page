import streamlit as st
from loading import load_policy
from pages.policy_tester import PolicyTester
from pages.testing_utils import test_policy, test_system
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
    
    st.session_state.current_page = PAGE.TEST_POLICY
    
    st.title("Test Policies")
    
    pdp_pol_container = st.container(border=False, key='test_table_container')
    
    for pdp_pol_object in st.session_state.pdp_policies:
        
        with pdp_pol_container.chat_message('user', avatar=":material/gavel:"):
            nlacp_col, btn_col = st.columns([7,1])
            test_policy(pdp_pol_object, policy_tester, btn_col)
            nlacp_col.markdown(pdp_pol_object.policyDescription)
            with st.expander("Generated Policy", expanded=False):
                st.dataframe(load_policy(pdp_pol_object.policy), use_container_width=True, key=f"pdp_policy_{pdp_pol_object.policyId}")


    with st.container(border=False, height=100, key='test_container'):

        st.button(
            "Test System",
            type="primary",
            help="Test the entire system (i.e., all the policies in the policy database) by sending an access request",
            use_container_width=True,
            key="test_all",
            disabled=len(st.session_state.pdp_policies) < 1,
            on_click=test_system,
            args=(policy_tester,),
            icon=":material/output:"
        )

hierarchy = st.session_state.hierarchies

standard_menu()

ac_engine = AccessControlEngine()
policy_tester = PolicyTester(hierarchy, ac_engine)
test_policies(policy_tester)