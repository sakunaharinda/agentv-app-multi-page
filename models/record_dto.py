from dataclasses import dataclass, field
from typing import List

@dataclass
class Results:
    sentences: List[str] = field(default_factory = list)
    nlacps: List[str] = field(default_factory = list)
    nlacps_context: List[List[str]] = field(default_factory = list)
    generated_nlacps: List[str] = field(default_factory = list)
    generated_policies: List[dict] = field(default_factory = list)
    converted_policies: List[str] = field(default_factory = list)
    init_verification: List[int] = field(default_factory = list)
    final_verification: List[int] = field(default_factory = list)
    final_policies: List[dict] = field(default_factory = list)
    final_correct_policies: List[dict] = field(default_factory = list)
    interrupted_errors: List[str] = field(default_factory = list)
    
    def to_dict(self):
        return {
            'sentences': self.sentences,
            'nlacps': self.nlacps,
            'nlacps_context': self.nlacps_context,
            'generated_nlacps': self.generated_nlacps,
            'generated_policies': self.generated_policies,
            'converted_policies': self.converted_policies,
            'init_verification': self.init_verification,
            'final_verification': self.final_verification,
            'final_policies': self.final_policies,
            'final_correct_policies': self.final_correct_policies,
            'interrupted_errors': self.interrupted_errors
        }
        
@dataclass
class WrittenPolicy:
    id: str = "1"
    sentence: str = ""
    policy: List[dict] = field(default_factory = list)
    error: str = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'sentence': self.sentence,
            'policy': self.policy,
            'error': self.error
        }
        

class Hierarchy:
    subject_hierarchy: dict
    action_hierarchy: dict
    resource_hierarchy: dict
    condition_hierarchy: dict
    
    def __init__(self, hierarchies) -> None:
        self.subject_hierarchy = hierarchies[0]
        self.action_hierarchy = hierarchies[1]
        self.resource_hierarchy = hierarchies[2]
        self.condition_hierarchy = hierarchies[3]
        
        