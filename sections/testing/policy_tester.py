import streamlit as st
import uuid
from models.ac_engine_dto import JSONPolicyRecordPDP, PolicyEffectRequest
from ac_engine_service import AccessControlEngine


class PolicyTester():
    
    def __init__(self, hierarchy: dict, ac_engine: AccessControlEngine):
        
        self.subjects = sorted(self.get_values(hierarchy['subject_hierarchy']))
        self.actions = sorted(self.get_values(hierarchy['action_hierarchy']))
        self.resources = sorted(self.get_values(hierarchy['resource_hierarchy']))
        
        self.ac_engine = ac_engine

    def get_values(self, h: dict):
        values = []
        for k, v in h.items():
            values.extend(v)
            
        return list(set(values))


    @st.dialog("Create a request")
    def test_policy(self, policy: JSONPolicyRecordPDP):
        random_rule = policy.to_dict()['policy'][0]
        
        st.write(policy.policyDescription)
        
        subject = st.selectbox(label="Subject", options=self.subjects, index=self.subjects.index(random_rule['subject']))
        action = st.selectbox(label="Action", options=self.actions, index=self.actions.index(random_rule['action']))
        resource = st.selectbox(label="Resource", options=self.resources, index=self.resources.index(random_rule['resource']))
        
        ct = st.container(height=100, border=False)
        col1, col2 = st.columns([1,1])
        with col1:
            req_submit = st.button("Send Request", key='req_submit', help="Send the request", type='primary', use_container_width=True)
            
        with col2:
            req_back = st.button("Back", key='back', help="Go back to Policy Database", type='secondary', use_container_width=True)
            
        if req_submit:
            
            request = PolicyEffectRequest(
                policyId=policy.policyId,
                subject=subject,
                action=action,
                resource=resource
            )
            
            status_code, response = self.ac_engine.get_effect(request)
            
            if status_code == 200:
                if response.decision == 'permit':
                    ct.success("The request is **Allowed!**", icon=":material/check_circle:")
                elif response.decision == 'deny':
                    ct.error("The request is **Denied!**", icon=":material/error:")
                else:
                    ct.warning("The request is **Not Applicable!**", icon=":material/warning:")
            else:
                ct.error(f"Returned the status code {status_code}")
                
        elif req_back:
            st.rerun()
        

    @st.dialog("Create a request")
    def test_overall(self):
        
        # st.write(policy.policyDescription)
        
        subject = st.selectbox(label="Subject", options=self.subjects, index=0)
        action = st.selectbox(label="Action", options=self.actions, index=0)
        resource = st.selectbox(label="Resource", options=self.resources, index=0)
        
        ct = st.container(height=100, border=False)
        col1, col2 = st.columns([1,1])
        with col1:
            req_submit = st.button("Send Request", key='req_submit_overall', help="Send the request", type='primary', use_container_width=True)
            
        with col2:
            req_back = st.button("Back", key='back_overall', help="Go back to Policy Database", type='secondary', use_container_width=True)
            
        if req_submit:
            
            request = PolicyEffectRequest(
                policyId=str(uuid.uuid4()),
                subject=subject,
                action=action,
                resource=resource
            )
            
            status_code, response = self.ac_engine.get_overall_effect(request)
            
            if status_code == 200:
                if response.decision == 'permit':
                    ct.success("The request is **Allowed!**", icon=":material/check_circle:")
                elif response.decision == 'deny':
                    ct.error("The request is **Denied!**", icon=":material/error:")
                else:
                    ct.warning("The request is **Not Applicable!**", icon=":material/warning:")
            else:
                ct.error(f"Returned the status code {status_code}")
                
        elif req_back:
            st.rerun()