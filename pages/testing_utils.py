from pages.policy_tester import PolicyTester
from models.ac_engine_dto import JSONPolicyRecordPDP
from utils import change_page_icon

def test_policy(policy: JSONPolicyRecordPDP, policy_tester: PolicyTester, col):
    
    
    test_btn = col.button("Test", key=f"test_{policy.policyId}", use_container_width=True, type='primary', help = "Test the policy by sending an access request",icon=":material/output:")
    
    if test_btn:
        change_page_icon('test_icon')
        policy_tester.test_policy(policy)
        
        
def test_system(policy_tester: PolicyTester):
    
    change_page_icon('test_icon')
    policy_tester.test_overall()
    
