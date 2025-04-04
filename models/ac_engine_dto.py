from dataclasses import dataclass, field, asdict
from typing import List
import uuid


@dataclass
class ACR:
    decision: str
    subject: str
    action: str
    resource: str
    purpose: str
    condition: str

@dataclass
class JSONPolicyRecord:
    
    policyId: str
    policyDescription: str
    policy: List[ACR] = field(default_factory= list)
    
    @staticmethod
    def from_dict(data: dict):
        
        policy = [ACR(**acr) for acr in data.get('policy', [])]
        return JSONPolicyRecord(
            policyId=data.get('policyId', ''),
            policyDescription=data.get('policyDescription', ''),
            policy=policy
        )
        
    def to_dict(self):
        return asdict(self)
    
    def get_null_policy():
        
        return JSONPolicyRecord(
            policyId="000",
            policyDescription="No description",
            acrs= [
                ACR(
                    decision="deny",
                    subject="none",
                    action="none",
                    resource="none",
                    purpose="none",
                    condition="none"
                )
            ]
        )
    

@dataclass
class XACMLPolicyRecord:
    id: str
    policy: str
    
    @staticmethod
    def from_dict(data: dict):
        return XACMLPolicyRecord(
            id = data.get('id', '0'),
            policy=data.get('policy','')
        )

@dataclass     
class PolicyEffectRequest:
    
    policyId: str
    subject: str
    action: str
    resource: str
    
    def to_dict(self):
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict):
        return PolicyEffectRequest(
            policyId = data.get('policyId', '0'),
            subject=data.get('subject','none'),
            action=data.get('action','none'),
            resource=data.get('resource','none'),
        )
    

@dataclass
class PolicyEffectResponse:
    
    decision: str
    advice: List[str] = field(default_factory=list)
    
    @staticmethod
    def from_dict(data: dict):
        return PolicyEffectResponse(
            decision=data['decision'],
            advice=data['advice']
        )