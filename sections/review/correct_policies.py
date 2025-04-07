import streamlit as st
from handlers import get_cor_nlacp, get_cor_policy, cor_policy_nav_prev, cor_policy_nav_next, pdp_policy_nav_last, pdp_policy_nav_next 
from loading import load_policy
from ac_engine_service import AccessControlEngine
from sections.review.review_utils import publish_all, publish_cur, policy_db_feedback
from utils import change_page_icon

@st.fragment
def show_correct_policies(ac_engine: AccessControlEngine):
    
    st.title("Correct Policies")
    
    corr_policy = st.text_input(
        label="Correctly generated policy",
        value=get_cor_nlacp(),
        disabled=True,
        help="Natural Language Access Control Policies corresponding to correct access control policies.",
    )
    _, pclc, nclc, _ = st.columns([5, 2, 2, 5])
    prev_button_correct = pclc.button(
        label="Previous",
        key="cor_prev",
        on_click=cor_policy_nav_prev,
        disabled=st.session_state.cor_count <= 0,
        use_container_width=True,
    )
    next_button_correct = nclc.button(
        label="Next",
        key="cor_next",
        on_click=cor_policy_nav_next,
        disabled=st.session_state.cor_count
        == len(st.session_state.corrected_policies) - 1,
        use_container_width=True,
    )

    cdf = load_policy(get_cor_policy())

    cor_pol_container = st.container(border=False, height=343)
    if len(st.session_state.corrected_policies)>0:
        corr_df = cor_pol_container.dataframe(cdf, use_container_width=True, key="correct_policies")


    with st.container(border=False, height=100):
        out_col1, out_col2 = st.columns([1, 1])
        # json_btn = viz_col1.button('Export as JSON', use_container_width=True, key='json_btn')

        publish_all_btn = out_col2.button(
            "Publish All Policies to Database",
            type="secondary",
            use_container_width=True,
            key="publish_all",
            disabled=len(st.session_state.corrected_policies) < 1,
        )
        
        publish_cur_btn = out_col1.button(
            "Publish Policy to Database",
            type="primary",
            use_container_width=True,
            key="publish_cur",
            disabled=len(st.session_state.corrected_policies) < 1,
        )
        
        if publish_cur_btn:
            change_page_icon('correct_pol_icon')
            cur_policy = st.session_state.corrected_policies[st.session_state.cor_count]
            status = publish_cur(ac_engine)
            if status == 200:
                st.session_state.pdp_policies.append(cur_policy)
                cor_pol_container.success("Policy is published sucessfully!", icon='✅')
                pdp_policy_nav_last()
            else:
                cor_pol_container.error(f"An error occured with the HTTP status code {status} while trying to publish the policy.", icon='🚨')
                
        elif publish_all_btn:
            change_page_icon('correct_pol_icon')
            status = publish_all(ac_engine)
            
            # TODO: Add a dialog to show success message
            if status == 200:
                
                st.session_state.pdp_policies.extend(st.session_state.corrected_policies)
                st.session_state.pdp_policies = list(set(st.session_state.pdp_policies))
                pdp_policy_nav_next()
            
            policy_db_feedback(status)
            
        
ac_engine = AccessControlEngine()
show_correct_policies(ac_engine)