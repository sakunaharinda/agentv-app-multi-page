import os
import requests
import uuid
from models.ac_engine_dto import *

# BASE_URL = os.environ['AC_ENGINE_SERVER_BASE_URL']


class AccessControlEngine():
    
    def __init__(self, base_url = os.environ['AC_ENGINE_SERVER_BASE_URL'],
                 get_policies_path = '/policy',
                 get_policies_json_path = '/policy/json',
                 get_published_policies_path = '/policy/published', 
                 get_policy_by_id_path = '/policy/{id}',
                 get_overall_effect_path = '/policy/effectAll',
                 get_effect_path = '/policy/effect',
                 create_policy_path = '/policy/add',
                 create_policies_path = '/policy/addAll',
                 create_policies_json_path = '/policy/addAll/json',
                 delete_policy_by_id_path = '/policy/{id}',
                 create_policy_xacml_path = '/policy/add/xacml',
                 create_policy_json_path = '/policy/add/json'
                 ):
        self.base_url = base_url
        self.get_policies_url = base_url + get_policies_path
        self.get_policy_by_id_url = base_url + get_policy_by_id_path
        self.get_policies_json_url = base_url + get_policies_json_path
        self.get_published_policies_url = base_url + get_published_policies_path
        self.get_overall_effect_url = base_url + get_overall_effect_path
        self.get_effect_url = base_url + get_effect_path
        self.create_policy_url = base_url + create_policy_path
        self.create_policies_url = base_url + create_policies_path
        self.create_policies_json_url = base_url + create_policies_json_path
        self.delete_policy_by_id_url = base_url + delete_policy_by_id_path
        self.create_policy_xacml_url = base_url + create_policy_xacml_path
        self.create_policy_json_url = base_url + create_policy_json_path


    def get_all_policies(self):
        response = requests.get(self.get_policies_url)
        return response.status_code, [XACMLPolicyRecord(**record) for record in response.json()]
    
    def get_all_policies_json(self):
        response = requests.get(self.get_policies_json_url)
        return response.status_code, [JSONPolicyRecordPDP.from_dict(record) for record in response.json()]
    
    def get_published_policies(self):
        response = requests.get(self.get_published_policies_url)
        return response.status_code, [JSONPolicyRecordPDP.from_dict(record) for record in response.json()]

    def get_policy_by_id(self, id):
        response = requests.get(self.get_policy_by_id_url.format_map({'id': id}))
        return response.status_code, XACMLPolicyRecord.from_dict(response.json())


    def get_overall_effect(self, body: PolicyEffectRequest):
        policy_effect_request = body.to_dict()
        response = requests.post(self.get_overall_effect_url, json=policy_effect_request)
        return response.status_code, PolicyEffectResponse.from_dict(response.json())

    def get_effect(self, body: PolicyEffectRequest):
        policy_effect_request = body.to_dict()
        response = requests.post(self.get_effect_url, json=policy_effect_request)
        return response.status_code, PolicyEffectResponse.from_dict(response.json())


    def create_policy(self, body: JSONPolicyRecord):
        policy_create_request = body.to_dict()
        response = requests.post(self.create_policy_url, json=policy_create_request)
        return response.status_code
    
    def create_policy_xacml(self, body: XACMLPolicyRecord):
        policy_create_request = body.to_dict()
        response = requests.post(self.create_policy_xacml_url, json=policy_create_request)
        return response.status_code
    
    def create_policy_json(self, body: JSONPolicyRecordPDP):
        policy_create_request = body.to_dict()
        response = requests.post(self.create_policy_json_url, json=policy_create_request)
        return response.status_code
    
    def create_multiple_policies_json(self, body: List[JSONPolicyRecordPDP]):
        policy_create_request = [r.to_dict() for r in body]
        response = requests.post(self.create_policies_json_url, json=policy_create_request)
        return response.status_code
        
    def create_multiple_policies(self, body: List[JSONPolicyRecord]):
        policy_create_request = [r.to_dict() for r in body]
        response = requests.post(self.create_policies_url, json=policy_create_request)
        return response.status_code
    
    def delete_policy_by_id(self, id):
        response = requests.delete(self.delete_policy_by_id_url.format_map({'id': id}))
        return response.status_code

if __name__ == '__main__':
    
    ac_engine = AccessControlEngine()
    
    p2 = str(uuid.uuid4())
    
    policy = JSONPolicyRecord(
        policyId=p2,
        policyDescription='hcp can read and write prescriptions.',
        policy=[
            ACR(
                decision='allow',
                subject='hcp',
                action='read',
                resource='prescription',
                purpose='none',
                condition='none'
            ),
            ACR(
                decision='allow',
                subject='hcp',
                action='write',
                resource='prescription',
                purpose='none',
                condition='none'
            )
        ]
    )
    
    response = ac_engine.create_policy(policy)
    
    print ("\n------------------------\n")
    
    print(f"Policy to create: {policy}")
    print(f"Response: {response}")
    print ("\n------------------------\n")
    
    request = PolicyEffectRequest(
        policyId=p2,
        subject="hcp",
        action="write",
        resource="prescription"
    )
    
    response_one = ac_engine.get_effect(request)
    
    print(f"Sent request: {request}")
    print(f"Response: {response_one}")
    print ("\n------------------------\n")
    
    p3 = str(uuid.uuid4())
    p4 = str(uuid.uuid4())
    
    policy_list = [
        
        JSONPolicyRecord(
            policyId=p3,
            policyDescription='nurse and doctor can read prescriptions.',
            policy=[
                ACR(
                    decision='allow',
                    subject='nurse',
                    action='read',
                    resource='prescription',
                    purpose='none',
                    condition='none'
                ),
                ACR(
                    decision='allow',
                    subject='doctor',
                    action='read',
                    resource='prescription',
                    purpose='none',
                    condition='none'
                )
            ]
        ),
        JSONPolicyRecord(
            policyId=p4,
            policyDescription='hcp cannot write prescriptions.',
            policy=[
                ACR(
                    decision='deny',
                    subject='hcp',
                    action='write',
                    resource='prescription',
                    purpose='none',
                    condition='none'
                )
            ]
        )         
    ]
    
    response_create_multi = ac_engine.create_multiple_policies(policy_list)
    
    print(f"Policies to create: {policy_list}")
    print(f"Response: {response_create_multi}")
    print ("\n------------------------\n")
    
    response_multi = ac_engine.get_overall_effect(request)
    
    print(f"Sent request (Overall): {request}")
    print(f"Response: {response_multi}")
    print ("\n------------------------\n")
    
    id = p3
    
    xacml_policies = ac_engine.get_policy_by_id(id)
    
    print(f"View Policy: {id}")
    print(f"Response: {xacml_policies}")
    print ("\n------------------------\n")
    
    response_delete = ac_engine.delete_policy_by_id(id)
    
    print(f"Delete Policy: {id}")
    print(f"Response: {response_delete}")
    print ("\n------------------------\n")
    
    xacml_policies = ac_engine.get_all_policies()
    
    print(f"View All Policy")
    print(f"Response: {xacml_policies}")
    print ("\n------------------------\n")