from dataclasses import dataclass, field, asdict
from typing import List, Tuple
import uuid


@dataclass(frozen=True)
class ACR:
    decision: str
    subject: str
    action: str
    resource: str
    purpose: str
    condition: str
    
    def __eq__(self, __value: object) -> bool:
        return (
            self.decision == __value.decision and
            self.subject == __value.subject and
            self.action == __value.action and
            self.resource == __value.resource and
            self.purpose == __value.purpose and
            self.condition == __value.condition
        )
        
    def __hash__(self) -> int:
        return hash((
            self.decision,
            self.subject,
            self.action,
            self.resource,
            self.purpose,
            self.condition
        ))

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
    
    def to_json_record_pdp(self):
        
        return JSONPolicyRecordPDP(
            policyId=self.policyId,
            policyDescription=self.policyDescription,
            policy=self.policy,
            published=False
        )
    
    def __eq__(self, __value: object) -> bool:
        return (
            self.policyDescription == __value.policyDescription and
            self.policy == __value.policy
        )
        
    def __hash__(self) -> int:
        # Convert the list of ACR objects to a tuple for hashing
        policy_tuple = tuple(frozenset((
            acr.decision,
            acr.subject,
            acr.action,
            acr.resource,
            acr.purpose,
            acr.condition
        ) for acr in self.policy))
        
        # Hash the combination of immutable attributes
        return hash((self.policyId, self.policyDescription, policy_tuple))


@dataclass
class JSONPolicyRecordPDP:
    
    policyId: str
    policyDescription: str
    policy: List[ACR] = field(default_factory= list)
    published: bool = False
    
    @staticmethod
    def from_dict(data: dict):
        
        policy = [ACR(**acr) for acr in data.get('policy', [])]
        return JSONPolicyRecordPDP(
            policyId=data.get('policyId', ''),
            policyDescription=data.get('policyDescription', ''),
            policy=policy,
            published=data.get('published', False)
        )
        
    def to_json_record(self):
        
        return JSONPolicyRecord(
            policyId=self.policyId,
            policyDescription=self.policyDescription,
            policy=self.policy
        )
        
    def to_dict(self):
        return asdict(self)
    
    def __eq__(self, __value: object) -> bool:
        return (
            self.policyDescription == __value.policyDescription and
            self.policy == __value.policy and
            self.published == __value.published
        )
        
    def __hash__(self) -> int:
        # Convert the list of ACR objects to a tuple for hashing
        policy_tuple = tuple(frozenset((
            acr.decision,
            acr.subject,
            acr.action,
            acr.resource,
            acr.purpose,
            acr.condition
        ) for acr in self.policy))
        
        # Hash the combination of immutable attributes
        return hash((self.policyId, self.policyDescription, policy_tuple, self.published))
    

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
        
    def to_dict(self):
        return asdict(self)

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