import streamlit as st
from handlers import get_pdp_nlacp, pdp_policy_nav_prev, pdp_policy_nav_next, get_pdp_policy
from loading import load_policy
from sections.testing.policy_tester import PolicyTester
from ac_engine_service import AccessControlEngine

@st.fragment
def test_policies(policy_tester: PolicyTester):
    
    st.title("Test Policies")
    
    pdp_policy = st.text_input(
        label="Policy submitted to the Policy Database",
        value=get_pdp_nlacp(),
        disabled=True,
        help="Natural Language Access Control Policies corresponding to access control policies submitted to the policy database.",
    )
    _, pclc, nclc, _ = st.columns([5, 2, 2, 5])
    prev_button_pdp = pclc.button(
        label="Previous",
        key="pdp_prev",
        on_click=pdp_policy_nav_prev,
        disabled=st.session_state.pdp_count <= 0,
        use_container_width=True,
    )
    next_button_pdp = nclc.button(
        label="Next",
        key="pdp_next",
        on_click=pdp_policy_nav_next,
        disabled=st.session_state.pdp_count
        == len(st.session_state.pdp_policies) - 1,
        use_container_width=True,
    )

    cdf = load_policy(get_pdp_policy())

    pdp_pol_container = st.container(border=False, height=343)
    if len(st.session_state.pdp_policies)>0:
        pdp_df = pdp_pol_container.dataframe(cdf, use_container_width=True, key="pdp_record")


    with st.container(border=False, height=100):
        out_col1, out_col2 = st.columns([1, 1])
        # json_btn = viz_col1.button('Export as JSON', use_container_width=True, key='json_btn')

        test_system_btn = out_col2.button(
            "Test System",
            type="secondary",
            use_container_width=True,
            key="test_all",
            disabled=len(st.session_state.pdp_policies) < 1,
        )
        
        test_policy_btn = out_col1.button(
            "Test Policy",
            type="primary",
            use_container_width=True,
            key="test_cur",
            disabled=len(st.session_state.pdp_policies) < 1,
        )
        
        if test_policy_btn:
            
            policy_tester.test_policy(st.session_state.pdp_policies[st.session_state.pdp_count])
            # st.write(st.session_state.corrected_policies[st.session_state.cor_count])
            
        elif test_system_btn:
            
            policy_tester.test_overall()

hierarchy = st.session_state.hierarchies
ac_engine = AccessControlEngine()
policy_tester = PolicyTester(hierarchy, ac_engine)
test_policies(policy_tester)