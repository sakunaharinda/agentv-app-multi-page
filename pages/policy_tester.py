import streamlit as st
import uuid
from models.ac_engine_dto import JSONPolicyRecordPDP, PolicyEffectRequest
from ac_engine_service import AccessControlEngine


class PolicyTester():
    
    def __init__(self, hierarchy: dict, ac_engine: AccessControlEngine):
        
        if hierarchy:
        
            self.subjects = sorted(self.get_values(hierarchy['subject_hierarchy']))
            self.actions = sorted(self.get_values(hierarchy['action_hierarchy']))
            self.resources = sorted(self.get_values(hierarchy['resource_hierarchy']))
        else:
            self.subjects, self.actions, self.resources = [],[],[]
            
        self.ac_engine = ac_engine

    def get_values(self, h: dict):
        values = []
        for k, v in h.items():
            values.extend(v)
            
        return list(set(values))


    @st.dialog("Create a request")
    def test_policy(self, policy: JSONPolicyRecordPDP):
        random_rule = policy.to_dict()['policy'][0]
        
        with_context = policy.with_context
        
        st.write(policy.policyDescription + (" :red-badge[:material/family_history: Without context]" if not with_context else ""))
        
        if with_context:
        
            subject = st.selectbox(label="Subject", options=self.subjects, index=self.subjects.index(random_rule['subject']) if random_rule['subject'] in self.subjects else 0)
            action = st.selectbox(label="Action", options=self.actions, index=self.actions.index(random_rule['action']) if random_rule['action'] in self.actions else 0)
            resource = st.selectbox(label="Resource", options=self.resources, index=self.resources.index(random_rule['resource']) if random_rule['resource'] in self.resources else 0)
        else:
            
            subject = st.text_input(label="Subject")
            action = st.text_input(label="Action")
            resource = st.text_input(label="Resource")
        
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
        
        self.subjects = ["Write the component ..."] + self.subjects
        self.actions = ["Write the component ..."] + self.actions
        self.resources = ["Write the component ..."] + self.resources
                 
        subject = st.selectbox(label="Subject", options=self.subjects, index=len(self.subjects)-1)
        if subject == 'Write the component ...':
            subject = st.text_input(label="Subject", label_visibility='collapsed', placeholder="Enter the Subject")
            
        action = st.selectbox(label="Action", options=self.actions, index=len(self.actions)-1)
        if action == 'Write the component ...':
            action = st.text_input(label="Action", label_visibility='collapsed', placeholder="Enter the Action")

        resource = st.selectbox(label="Resource", options=self.resources, index=len(self.resources)-1)
        if resource == 'Write the component ...':
            resource = st.text_input(label="Resource", label_visibility='collapsed', placeholder="Enter the Resource")
        
        
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