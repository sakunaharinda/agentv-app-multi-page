import os
import streamlit as st
from enum import Enum
import random
import ast
import streamlit as st
from typing import List
from torch.utils.data import Dataset, DataLoader
from models.record_dto import Results
from models.ac_engine_dto import JSONPolicyRecord
from ac_engine_service import AccessControlEngine
import distinctipy

def get_random_colors(n):
  colors = distinctipy.get_colors(n, pastel_factor=0.7, exclude_colors=[(0.0, 1.0, 0.0)])  

  colors_hex = ['#{:02x}{:02x}{:02x}'.format(
          int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
      ) for rgb in colors]

  return colors_hex

class Task(Enum):
    NLACP_ID = 'nlacp_identification',
    POLICY_VER = 'policy_verification'
    

class Error(Enum):
    MISSING_COMPONENT = 'missing_component'
    INCORRECT_COMPONENT = 'incorrect_component'
    CHANGED_DECISION = 'changed_decision'
    MISSING_RULES = 'missing_rules'

ID2AUGS = {
    0: "allow_deny",
    1: "csub",
    2: 'cact',
    3: "cres",
    4: "ccond",
    5: "cpur",
    6: "msub",
    7: "mres",
    8: "mcond",
    9: "mpur",
    10: "mrules",
    11: "correct",
}

CAT2ERROR = {
    0: 'incorrect decision',
    1: 'incorrect subject',
    2: 'incorrect action',
    3: 'incorrect resource',
    4: 'incorrect condition',
    5: 'incorrect purpose',
    6: 'missing subject',
    7: 'missing resource',
    8: 'missing condition',
    9: 'missing purpose',
    # 10: 'missing rules'
}

AUG_LABELS = {
    'allow_deny': 0, 
    'incorrect_subject': 1, 
    'incorrect_action': 2, 
    'incorrect_resource': 3, 
    'incorrect_condition': 4, 
    'incorrect_purpose': 5, 
    'missing_subject': 6, 
    'missing_resource': 7, 
    'missing_condition': 8, 
    'missing_purpose': 9,
    'missing_rule': 10,
    'correct': 11
}
    
ERROR_MAP = {
    0:(Error.CHANGED_DECISION, ''), 
    1:(Error.INCORRECT_COMPONENT, 'subject'), 
    2:(Error.INCORRECT_COMPONENT, 'action'), 
    3:(Error.INCORRECT_COMPONENT, 'resource'), 
    4:(Error.INCORRECT_COMPONENT, 'condition'), 
    5:(Error.INCORRECT_COMPONENT, 'purpose'), 
    6:(Error.MISSING_COMPONENT, 'subject'), 
    7:(Error.MISSING_COMPONENT, 'resource'), 
    8:(Error.MISSING_COMPONENT, 'condition'), 
    9:(Error.MISSING_COMPONENT, 'purpose'),
    10:(Error.MISSING_RULES, '')
}


ACP_DEFN = """
Access Control Policy Definition
--------------------------------

Access Control Policy (ACP) is a python list containing python dictionaries.
Each python dictionary represents an Access Control Rule (ACR).
Each ACR (or python dictionary) contains five keys, namely, 'decision', 'subject', 'action', 'resource', 'purpose', and 'condition'.

'decision': The access decision of the ACR. It can only be either 'allow' used for an ACR that allows a subject to perform an action on a resource, or 'deny' otherwise.
'subject': The entity that performs the 'action' on the 'resource'. 
'resource': The entity which the 'subject' performs an 'action' on.
'purpose': The purpose of perfoming the 'action'.
'condition': The condition/constraint affect the 'action'.

It is important that each ACP can contain one or more ACRs and each ACR can contain only one subject, action, resource, purpose, or condition.
When generating the ACP, first you need to identify ACRs.
For example, in the sentence 'The doctor and the nurse can read records if the patient agrees.' contains two ACRs: 'The doctor can read records if the patient agrees' and 'The nurse can read records if the patient agrees'.
Then represent each identified ACR as a python dictionary.
For example, the ACR 'The doctor can read records if the patient agrees.' has the 'allow' access decision since the ACR allows the doctor to read records, 'subject' is the doctor, the resource is the 'record', and the 'condition' is 'the patient agrees', since the patient's agreement affect the action 'read'.
Here there is no 'purpose' mentioned in the ACR. Therefore the value for the key 'purpose' is 'none'.
Finally we have an ACR as, 
{'decision': 'allow', 'subject': 'doctor', 'action': 'read', 'resource': 'record', 'purpose': 'none', 'condition': 'patient agrees'}.
Similary, for the ACR 'The nurse can read records if the patient agrees', we can build the python dictionary as,
{'decision': 'allow', 'subject': 'nurse', 'action': 'read', 'resource': 'record', 'purpose': 'none', 'condition': 'patient agrees'}.
Finally the ACP can be created as a python list with built ACR dictionaries.

ACP: [{'decision': 'allow', 'subject': 'doctor', 'action': 'read', 'resource': 'record', 'purpose': 'none', 'condition': 'patient agrees'}, {'decision': 'allow', 'subject': 'nurse', 'action': 'read', 'resource': 'record', 'purpose': 'none', 'condition': 'patient agrees'}]
\n\n
"""

VERIFICATION_INST = ACP_DEFN + f"""You are an intelligent access control policy verifier that can decide whether or not an access control policy generated from a natural language access requirement according to the provided Access Control Policy Definition is correct.
    Given the nlacp after 'NLACP:' tag and the corresponding access control policy generated according to the above Access Control Policy Definition after the 'Policy:' tag, output 'correct' if the 'Policy' represents the 'NLACP' accurately.
    If not output the reason for inaccuratly representing the NLACP as one of the following 11 categories:\n
    
    1. 'allow_deny': The access 'decision' of one or more ACR (i.e., python dictionary in the 'Policy') is incorrect.
    2. 'missing_rule': One or more ACR (i.e., python dictionary in the 'Policy') is completely missing even though it should be there.
    3. 'missing_subject': The 'subject' of one or more ACR (i.e., python dictionary in the Policy) is missing as indicated by 'subject': 'none', even though it can be found in the 'NLACP'.
    4. 'missing_resource': The 'resource' of one or more ACR (i.e., python dictionary in the Policy) is missing as indicated by 'resource': 'none', even though it can be found in the 'NLACP'.
    5. 'missing_condition': The 'condition' of one or more ACR (i.e., python dictionary in the Policy) is missing as indicated by 'condition': 'none', even though it can be found in the 'NLACP'.
    6. 'missing_purpose': The 'purpose' of one or more ACR (i.e., python dictionary in the Policy) is missing as indicated by 'purpose': 'none', even though it can be found in the 'NLACP'.
    7. 'incorrect_subject': The 'subject' of one or more ACR (i.e., python dictionary in the Policy) is incorrect.
    8. 'incorrect_action': The 'action' of one or more ACR (i.e., python dictionary in the Policy) is incorrect.
    9. 'incorrect_resource': The 'resource' of one or more ACR (i.e., python dictionary in the Policy) is incorrect.
    10. 'incorrect_purpose': The 'purpose' of one or more ACR (i.e., python dictionary in the Policy) is incorrect.
    11. 'incorrect_condition': The 'condition' of one or more ACR (i.e., python dictionary in the Policy) is incorrect.
    """
    
INSTRUCTION_ENTS = f"{ACP_DEFN}\nGiven a natural language sentence (i.e., NLACP), generate an access control policy according to the above Access Control Policy Definition.\nIf a value for any key in any python dictionary is cannot be found in the NLACP, set the value to 'none'.\nTo identify subject, action, resource, purpose, and condition, use the entities provided as a dictionary, 'Available entities' as an aid.\nIf none of the provided Available entities match the entities of the NLACP or there is no 'Available entities' provided, use your judgment to select the most suitable entity within the NLACP\nDo not use values in a different list as values for the keys subject, action, resource, purpose, and condition of the dictioaries represent access control rules (i.e., Do not use values available for 'resource' as 'subject' in in the access control policy, if it is not listed as an available 'subject').\n"

INSTRUCTION_NO_ENTS = f"{ACP_DEFN}\nGiven a natural language sentence (i.e., NLACP), generate an access control policy according to the above Access Control Policy Definition.\nIf a value for any key in any python dictionary is cannot be found in the NLACP, set the value to 'none'.\n"

a,count = 0,0
failed_parse = []

basic_template = "{subject} is {decision} {action} {resource}"
basic_template_subject = "{subject} is {decision} {action}"
basic_template_resource = "{resource} is {decision} be {action}"

purpose_template = "{template} for the purpose of {purpose}"
condition_template = "{template} if {condition}"
sarcp_template = "{template} for the purpose of {purpose}, if {condition}"

allow_sents = ['allowed to', 'able to', 'shall', 'authorized to']
deny_sents = ['prohibited to', 'not able to', 'shall not', 'unauthorized to']


def get_error_instrution(nlacp, gen_t_1, error_class):
    
    error = ERROR_MAP[error_class]
    error_prompt = get_error_prompt(error)
    return ACP_DEFN + f"You generated \'{gen_t_1}\' for the sentence, \'{nlacp} based on the mentioned Access Control Policy Definition.\nHowever the follwoing error is found.\n\n1. {error_prompt}\n\nPlease address the error and output the corrected access control policy according to the mentioned definition.\nThink step-by-step to first provide the reasoning steps/thought process.\nThen after the \n\n### Corrected: \n\n provide the corrected policy without any other text. Then add \n\n####"


def get_error_prompt(error):

    category,component = error

    if category == Error.MISSING_COMPONENT:
        return f"According to the Access Control Policy Definition, the value assigned for the '{component}' in one or more access control rules are 'none' (indicating not available in the sentence), even though the value can be found\n"

    elif category == Error.INCORRECT_COMPONENT:
        return f"According to the Access Control Policy Definition, the value assigned for the '{component}' in one or more access control rules are incorrect\n"

    elif category == Error.CHANGED_DECISION:
        return f"According to the Access Control Policy Definition, the value assigned for the decision in one or more access control rules are incorrect\n"

    else:
        return f"According to the Access Control Policy Definition, one or more python dicionaries that represent access control rules related to actions are missing\n"


def get_verification_msgs(input, output):

    user = f"Verify the natural language access requirement infront of the 'Policy:' tag based on the natural language requirement written infront of the 'NLACP:' tag.\nProvide the output as one of ['correct', 'allow_deny', 'missing_rule', 'mssing_subject', 'mssing_resource', 'mssing_purpose', 'mssing_condition','incorrect_subject', 'incorrect_action', 'incorrect_resource', 'incorrect_purpose', 'incorrect_condition'] according to the given instructions.\n\nNLACP: {input}\nPolicy: {output}"

    return [
        {'role': 'system', 'content': VERIFICATION_INST},
        {'role': 'user', 'content': user}
    ]
    
def get_generation_msgs_ents(nlacp, ents):
    
    messages = [
        {"role": "system", "content": INSTRUCTION_ENTS},
        {"role": "user", "content": f"NLACP: {nlacp}\nAvailable entities: {ents}"},
    ]
    return messages

def get_generation_msgs(nlacp):
    messages = [
        {"role": "system", "content": INSTRUCTION_NO_ENTS},
        {"role": "user", "content": f"NLACP: {nlacp}"},
    ]
    return messages

def prepare_inputs_bart(s,l,tokenizer, device = 'cuda:0'):
    
    tokens = tokenizer(s,l,return_tensors='pt')
    
    return {k:v.to(device) for k,v in tokens.items()}

def convert_to_sent(sample):
    random.seed(0)
    error = 0
    sample = ast.literal_eval(str(sample))
    pol_sent = []
    for rule in  sample:

        if rule['decision'] == 'allow':
            rand = random.randint(0, len(allow_sents)-1)
            decision = allow_sents[rand]
        else:
            rand = random.randint(0, len(deny_sents)-1)
            decision = deny_sents[rand]
    
        subject = rule['subject']
        action = rule['action']
        resource = rule['resource']
        purpose = rule['purpose']
        condition = rule['condition']
    
        if subject != 'none' and resource != 'none':
            template = basic_template.format_map({'decision': decision, 'subject': subject, 'action': action, 'resource': resource})
        elif subject != "none":
            template = basic_template_subject.format_map({'decision': decision, 'subject': subject, 'action': action})
        elif resource != "none":
            template = basic_template_resource.format_map({'decision': decision, 'resource': resource, 'action': action})
    
        else:
            # print(rule)
            template = ''
            error = True
    
    
        if purpose != 'none' and condition != 'none':
    
            final_template = sarcp_template.format_map({'template': template, 'purpose': purpose, 'condition': condition})
        elif purpose != 'none':
            final_template = purpose_template.format_map({'template': template, 'purpose': purpose})
    
        elif condition != 'none':
            final_template = condition_template.format_map({'template': template, 'condition': condition})
        else:
            final_template = template

        pol_sent.append(final_template)
    return " and ".join(pol_sent).strip(), error

def remove_duplicates(policy):
    
    uniques = []
    
    for r in policy:
        if r not in uniques:
            uniques.append(r)
            
    return uniques

# def rerun_on_login():
#     if 'loggedin' not in st.session_state or st.session_state['loggedin'] == False:
#         st.session_state['loggedin'] = True
#         st.rerun()
#     else:
#         del st.session_state['loggedin']
        
def reset(args):
    st.rerun()
    # if 'loggedin' in st.session_state:
    #     del st.session_state['loggedin']
    

class ACPDataset(Dataset):

    def __init__(self, sentences, tokenizer, max_len = 256, device='cuda:0'):
        self.text = [tokenizer(str(s), 
                        padding='max_length', 
                        max_length = max_len, 
                        truncation=True, 
                        return_token_type_ids = False, 
                        return_tensors="pt") for s in sentences]
        # self.labels = torch.tensor(df['acp'].tolist())
        self.sentences = sentences
        self.device = device

    def __len__(self):
        # assert len(self.text) == len(self.labels)
        return len(self.text)

    def __getitem__(self, idx):
        output = {k: v.flatten().to(self.device) for k,v in self.text[idx].items()}
        output['sentence'] = self.sentences[idx]
        return output
    
class VerificationDataset(Dataset):
    
    def __init__(self, results: Results, tokenizer, max_len = 1024, device='cuda:0'):
        self.premise = results.generated_nlacps
        self.hypothesis = results.converted_policies
        self.policies = results.generated_policies
        
        self.device = device
        
        self.input = [tokenizer(p,h,
                                return_tensors='pt',
                                padding='max_length',
                                truncation = True,
                                max_length = max_len) for p,h in zip(self.premise, self.hypothesis)]
        
          
    def __len__(self):
        return len(self.input)
    
    def __getitem__(self, index):
        output = {k: v.flatten().to(self.device) for k,v in self.input[index].items()}
        output['sentence'] = self.premise[index]
        output['policy'] = str(self.policies[index])
        return output
    

class DataLoaders():
    
    def __init__(self, _id_tokenizer, _gen_tokenizer, _ver_tokenizer, _loc_tokenizer, device = 'cuda:0'):
        self.id_tokenizer = _id_tokenizer
        self.gen_tokenizer = _gen_tokenizer
        self.ver_tokenizer = _ver_tokenizer
        self.loc_tokenizer = _loc_tokenizer
        
        self.device = device
    
    def get_loader(self, results: Results, task: Task, max_len = 256, batch_size=8):
        
        if task == Task.NLACP_ID:
            dataset = ACPDataset(results.sentences, self.id_tokenizer, max_len=max_len, device=self.device)
            loader = DataLoader(dataset, batch_size=batch_size)
        elif task == Task.POLICY_VER:
            dataset = VerificationDataset(results, self.ver_tokenizer, max_len=max_len, device=self.device)
            loader = DataLoader(dataset, batch_size=batch_size)
            
        return loader
    
    
def store_value_pol_doc(key):
    st.session_state.reviewed = False
    st.session_state.new_doc = True
    st.session_state[key] = st.session_state["_"+key]
    
def store_value(key):
    st.session_state[key] = st.session_state["_"+key]
    
def load_value(key):
    if key not in st.session_state:
        st.session_state[key] = None
    st.session_state["_"+key] = st.session_state[key]
    
def on_click_generate(page_icon):
    st.session_state.is_generating = True
    st.session_state.new_doc = False
    change_page_icon(page_icon)
    
def change_page_icon(state, icon = ":material/task_alt:"):
    
    st.session_state[state] = icon
    
def toast_download_sucess():
    
    st.toast("Policies were downloaded successfully!", icon=":material/download_done:")

@st.cache_resource(show_spinner=False)
def save_wo_duplicate(policy, record_list):
    
    record_dict = {obj.policyId: obj for obj in record_list}
    record_dict[policy.policyId] = policy
    
    return [policy] + [v for k,v in record_dict.items() if k != policy.policyId]
    
def save(policy: JSONPolicyRecord, enforce_unique = False, index=None, with_context=True):
    
    ac_engine = AccessControlEngine()

    pdp_record = policy.to_json_record_pdp(with_context=with_context)
    
    if enforce_unique:
        st.session_state.corrected_policies = save_wo_duplicate(policy, st.session_state.corrected_policies)
        st.session_state.corrected_policies_pdp = save_wo_duplicate(pdp_record, st.session_state.corrected_policies_pdp)
        
    else:
        
        if index != None:
            st.session_state.corrected_policies.insert(index, policy)
            st.session_state.corrected_policies_pdp.insert(index, pdp_record)
        else:
            st.session_state.corrected_policies.append(policy)
            st.session_state.corrected_policies_pdp.append(pdp_record)
            
    ac_engine.create_policy_json(pdp_record)
    

    