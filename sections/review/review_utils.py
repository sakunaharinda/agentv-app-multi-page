import streamlit as st
from ac_engine_service import AccessControlEngine
from utils import change_page_icon
from models.ac_engine_dto import JSONPolicyRecord, JSONPolicyRecordPDP
import functools

def publish_single(pdp_policy: JSONPolicyRecordPDP, ac_engine: AccessControlEngine):
    
    change_page_icon('correct_pol_icon')
            
    status = ac_engine.create_policy(pdp_policy.to_json_record())

    if status == 200:
        st.session_state.pdp_policies.append(pdp_policy)
        st.session_state.pdp_policies = list(set(st.session_state.pdp_policies))
        set_published(pdp_policy)

    # else:
    #     update_badge(pdp_policy, f":red-badge[:material/close: Failed - {status}]")

    # policy_db_feedback(status, single=True)
    
def get_updated_description(policy: JSONPolicyRecordPDP):
    
    if policy.published:
        
        return policy.policyDescription + " :green-badge[:material/check: Published]"
    else:
        return policy.policyDescription + " :orange-badge[:material/publish: Ready to Publish]"
    
def set_published(policy: JSONPolicyRecordPDP):
        
    policy.published = True
        
    return policy
    
    
def publish_all(ac_engine: AccessControlEngine):
    
    change_page_icon('correct_pol_icon')
    
    policies = st.session_state.corrected_policies
    status = ac_engine.create_multiple_policies(policies)
    
    if status == 200:
        st.session_state.corrected_policies_pdp = list(map(set_published, st.session_state.corrected_policies_pdp))
        
        st.session_state.pdp_policies.extend(st.session_state.corrected_policies_pdp)
        st.session_state.pdp_policies = list(set(st.session_state.pdp_policies))
        
        st.session_state.all_published = True
        st.switch_page("sections/testing/test_policies.py")
        
        

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
        
        
def publish_policy(policy: JSONPolicyRecordPDP, ac_engine, col):
    
    # _,_,col = st.columns([1,1,1])
    
    col.button("Publish", key=f"publish_{policy.policyId}", use_container_width=True, on_click=publish_single, args=(policy, ac_engine,), type='primary', help = "Publish the policy to the policy database", disabled=policy.published)
    
    
        