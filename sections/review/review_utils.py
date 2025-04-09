import streamlit as st
from ac_engine_service import AccessControlEngine

def publish_cur(ac_engine: AccessControlEngine):
    cur_policy = st.session_state.corrected_policies[st.session_state.cor_count]
    return ac_engine.create_policy(cur_policy)
    
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