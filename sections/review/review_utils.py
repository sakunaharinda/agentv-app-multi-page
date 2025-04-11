import streamlit as st
from ac_engine_service import AccessControlEngine
from utils import change_page_icon

def publish_single(policy, ac_engine: AccessControlEngine):
    
    change_page_icon('correct_pol_icon')
    status = ac_engine.create_policy(policy)
    if status == 200:
        st.session_state.pdp_policies.append(policy)
        st.session_state.pdp_policies = list(set(st.session_state.pdp_policies))

    policy_db_feedback(status, single=True)
    
def publish_all(ac_engine: AccessControlEngine):
    
    policies = st.session_state.corrected_policies
    return ac_engine.create_multiple_policies(policies)

@st.dialog(title="Publish to Policy Database")
def policy_db_feedback(status_code, single = False):
    
    if status_code == 200:
        if single:
            st.success("The policy is published to the policy database successfully!", icon=':material/check_circle:')
        else:
            st.success("All the policies are published to the policy database successfully!", icon=':material/check_circle:')
        
    else:
        if single:
            st.error(f"An error occured with the HTTP status code {status_code} while trying to publish the policy to the policy database.", icon=':material/dangerous:')
        else:
            st.error(f"An error occured with the HTTP status code {status_code} while trying to publish the policies to the policy database.", icon=':material/dangerous:')
        
    ok = st.button("OK", key='ok_publish', use_container_width=True, type='primary')
    
    if ok and not single:
        st.switch_page("sections/testing/test_policies.py")
    elif ok:
        st.rerun()
        
        
def publish_policy(policy, ac_engine):
    
    _,_,col = st.columns([1,1,1])
    
    col.button("Publish to Policy Database", key=f"publish_{policy.policyId}", use_container_width=True, on_click=publish_single, args=(policy, ac_engine,), type='primary')
        