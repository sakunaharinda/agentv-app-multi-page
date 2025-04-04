import os

import streamlit as st
import torch
from utils import *
import ast
import re
from itertools import product
import numpy as np
import handlers as handlers
from feedback import *
from dotenv import load_dotenv
import requests
from models.record_dto import Results, Hierarchy
from models.ac_engine_dto import JSONPolicyRecord
from uuid import uuid4
from ac_engine_service import AccessControlEngine

_ = load_dotenv('../.env')

ITERATIONS = 2

torch.classes.__path__ = []


@st.cache_data(show_spinner=False)
def preprocess_document(content):
    
    file = {
        "content": content
    }
    resp = requests.post(url=os.environ['PREPROCESSING_SERVER_IP'], json=file) 
    return resp.json()


@st.cache_data(show_spinner=False)
def classify_single_sentence(nlacp, _tokenizer, _model):

    input = nlacp.replace("\u2019s", "")
    tokens = _tokenizer(input, return_token_type_ids=False, return_tensors="pt").to(
        "cuda:0"
    )

    out = _model(**tokens)
    res = torch.argmax(out.logits, dim=1)
    return res.item()


@st.cache_data(show_spinner=False)
def get_nlacps(_loader, _model, results: Results):
    
    sentences = []
    all_preds = None

    for b in _loader:
        sentences.extend(b.pop('sentence'))
        out = _model(**b)
        logits = out.logits.cpu().detach().numpy()
        all_preds = logits if all_preds is None else np.concatenate((all_preds, logits))
    preds = np.argmax(all_preds, axis=-1)
    for s,r in zip(sentences, preds):
        if r:
            results.nlacps.append(s)
    return results


@st.cache_data(show_spinner=False)
def verify_policies(_loader, _model, results: Results):
    
    sentences,policies = [], []
    all_preds = None

    for b in _loader:
        sentences.extend(b.pop('sentence'))
        policies.extend(b.pop('policy'))
        out = _model(**b)
        logits = out.logits.cpu().detach().numpy()
        all_preds = logits if all_preds is None else np.concatenate((all_preds, logits))
    assert sentences == results.generated_nlacps,'Mismatch between verifier sentence ordering and the original ordering'
    assert policies == list(map(str,results.generated_policies)),'Mismatch between verifier policy ordering and the original ordering'
    
    results.init_verification = np.argmax(all_preds, axis=-1).tolist()
    return results


@st.cache_data(show_spinner=False)
def generate_policy(nlacp, _gen_tokenizer, _gen_model, context=None):
    sucess = False
    terminators = [
        60,  # ]
        933,  # ]\n
        14711,
        22414,  # \n\n\n\n
        _gen_tokenizer.eos_token_id,
        _gen_tokenizer.convert_tokens_to_ids("<|eot_id|>"),
    ]

    if context is not None:
        messages = get_generation_msgs_ents(nlacp, context)
    else:
        messages = get_generation_msgs(nlacp)

    input_ids = _gen_tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt"
    ).to(_gen_model.device)

    outputs = _gen_model.generate(
        input_ids,
        max_new_tokens=1024,
        eos_token_id=terminators,
        pad_token_id=_gen_tokenizer.eos_token_id,
        do_sample=False,
        temperature=0.0
    )

    response = outputs[0][input_ids.shape[-1] :]
    resp = _gen_tokenizer.decode(response, skip_special_tokens=True).strip()
    try:
        pattern = r"\[.*?\]"
        str_policy = re.findall(pattern, resp)[0]
        p = ast.literal_eval(str_policy)
        sucess = True
    except:
        print("Failed to parse")
        p = [{'decision': 'deny', 'subject': 'none', 'action': 'none', 'resource': 'none', 'purpose': 'none', 'condition': 'none'}]

    return p, sucess


@st.cache_data(show_spinner=False)
def verify(nlacp, pred_pol, _ver_model, _ver_tokenizer):
    pp, _ = convert_to_sent(str(pred_pol))

    ver_inp = prepare_inputs_bart(nlacp, pp, _ver_tokenizer, "cuda:0")
    pred = _ver_model(**ver_inp).logits

    probs = torch.softmax(pred, dim=1)
    pred_class = probs.argmax(axis=-1).item()

    return pred_class


@st.cache_data(show_spinner=False)
def get_refined_policy(instruction, _model, _tokenizer):
    terminators_errors = [
        _tokenizer.eos_token_id,
        _tokenizer.convert_tokens_to_ids("<|eot_id|>"),
    ]

    error_messages = [
        {"role": "system", "content": ""},
        {"role": "user", "content": instruction},
    ]

    input_ids = _tokenizer.apply_chat_template(
        error_messages, add_generation_prompt=True, return_tensors="pt"
    ).to(_model.device)

    outputs = _model.generate(
        input_ids,
        max_new_tokens=1024,
        eos_token_id=terminators_errors,
        pad_token_id=_tokenizer.eos_token_id,
        do_sample=False,
    )

    response = outputs[0][input_ids.shape[-1] :]
    resp = _tokenizer.decode(response, skip_special_tokens=True).strip()

    if "### Corrected" in resp:

        resp = resp.split("### Corrected")[1]
    else:

        resp = resp.split("final refined policy")[1]

    pattern = r"\[.*?\]"
    sanitized = re.findall(pattern, resp)

    return sanitized[0]

def get_candidates(_store, sentence,k=5):
    l = []
    
    if _store is not None:
        docs = _store.similarity_search(sentence,k=k)
        for d in docs:
            l.append(d.page_content)
        
    return l

@st.cache_data(show_spinner=False)
def get_available_entities(query: str, _vectorstores: dict, n=3):
    
    entities = {'subject': [], 'action': [], 'resource': [], 'purpose': [], 'condition': []}
    for key in entities:
        entities[key] = get_candidates(_vectorstores.get(key, None), query, k=n)

    return entities

@st.cache_data(show_spinner=False)
def verify_refine(
    nlacp,
    init_generation,
    _ver_tokenizer,
    _ver_model,
    _gen_tokenizer,
    _gen_model,
    iterations=ITERATIONS,
):

    tries = 0
    init_ver = verify(nlacp, init_generation, _ver_model, _ver_tokenizer)

    final_generation, final_verification = init_generation, init_ver

    if "ver_int_results" not in st.session_state:
        st.session_state["ver_int_results"] = []

    st.session_state.ver_int_results.append(
        {
            "nlacp": nlacp,
            "iterations": [
                {
                    "iteration": tries,
                    "pred": init_generation,
                    "verification": ID2AUGS[init_ver],
                }
            ],
        }
    )

    idx = len(st.session_state.ver_int_results) - 1

    while final_verification != 11 and tries < iterations:

        try:
            tries += 1

            error_instruction = get_error_instrution(
                nlacp, final_generation, final_verification
            )
            final_generation = get_refined_policy(
                error_instruction, _gen_model, _gen_tokenizer
            )
            final_generation = ast.literal_eval(str(final_generation))
            assert len(final_generation) > 0, f"Re-generation failed for: \n{nlacp}\n"
            final_generation = remove_duplicates(final_generation)
            final_verification = verify(
                nlacp, final_generation, _ver_model, _ver_tokenizer
            )

            st.session_state.ver_int_results[idx]["iterations"].append(
                {
                    "iteration": tries,
                    "pred": final_generation,
                    "verification": ID2AUGS[final_verification],
                }
            )

        except:
            print("Failed")
            break

    return final_generation, final_verification

@st.cache_data(show_spinner=False)
def extract_inc_rules(s):
    return re.findall(r'\{.*?\}', s)

@st.cache_data(show_spinner=False)
def locate_error(nlacp, policy, label, _model, _tokenizer):
    
    pol_label = f"NLACP: {nlacp}\nError: {label}"
    
    tokens = _tokenizer(
        pol_label,
        policy,
        max_length=512,
        truncation="only_second",
        return_tensors='pt',
        padding="max_length",
    )
    
    policy_tokens = _tokenizer(policy)['input_ids']

    inputs = {k:v.to('cuda:0') for k,v in tokens.items()}

    out = _model(**inputs)
    
    start_logits = out['start_logits']
    end_logits = out['end_logits']

    start_predictions = np.argmax(start_logits.cpu().detach().numpy(), axis=1).item()
    end_predictions = np.argmax(end_logits.cpu().detach().numpy(), axis=1).item()
    
    try:
        
        extracted_str = ''.join(_tokenizer.convert_ids_to_tokens(tokens['input_ids'][0])[start_predictions:end_predictions+1])
        
        inc_rules_str = extract_inc_rules(extracted_str)
        
        inc_rules = [ast.literal_eval(rule) for rule in inc_rules_str]
    
        input_policy = ast.literal_eval(''.join(_tokenizer.convert_ids_to_tokens(policy_tokens, skip_special_tokens=True)))
        return [input_policy.index(inc_rule) for inc_rule in inc_rules]
    
    except:
        print(nlacp)
        print(_tokenizer.convert_ids_to_tokens(tokens['input_ids'][0])[start_predictions:end_predictions+1])
        return [1]

@st.cache_data(show_spinner=False)
def get_children(hierarchy, entity):
    return hierarchy.get(entity, [entity])

@st.cache_data(show_spinner=False)
def expand_policy(policy, subject_h, action_h, resource_h):
    
    expanded_policy = []
    
    for rule in policy:
        subjects =  get_children(subject_h, rule['subject'])
        actions = get_children(action_h, rule['action'])
        resources = get_children(resource_h, rule['resource'])
        purpose = rule['purpose']
        condition = rule['condition']
        
        for subject, action, resource in product(subjects, actions, resources):
            expanded_policy.append({
                "decision": rule["decision"],
                "subject": subject,
                "action": action,
                "resource": resource,
                "purpose": purpose,
                "condition": condition
            })
    
    return expanded_policy

@st.cache_data
def filter_policy(policy):
    uniques = []
    for rule in policy:
        if rule not in uniques:
            uniques.append(rule)
    return uniques

@st.cache_data(show_spinner=False)
def align_policy(policy, _vectorstore: dict, _hierarchy: Hierarchy):
    unique_pols = []
    
    new_pol = []
    for rule in policy:
        for k,v in rule.items():
            if k=='decision' or k == 'purpose':
                continue
            store = _vectorstore.get(k, None)
            if v!='none' and store is not None:
                from_db = store.similarity_search(v,k=1)[0].page_content
            else:
                from_db = v
            rule[k] = from_db.strip()
        new_pol.append(rule)
        
    for r in new_pol:
        if r not in unique_pols:
            unique_pols.append(r)
            
    return expand_policy(unique_pols, _hierarchy.subject_hierarchy, _hierarchy.action_hierarchy, _hierarchy.resource_hierarchy)

# @st.cache_data(show_spinner=False)
def agentv_single(_ac_engine: AccessControlEngine, _status_container, nlacp, _id_tokenizer, _id_model, _gen_tokenizer, _gen_model, _ver_model, _ver_tokenizer, _loc_tokenizer, _loc_model, _vectorstores, _hierarchy: Hierarchy, do_align=True):
    
    with _status_container.status("Generating policies ...", expanded=True) as _status:

        results = Results()
        
        results.sentences.append(nlacp)
        
        # st.write("Preprocessing...")
        st.write("Looking for access requirements...")
        is_nlacp = classify_single_sentence(
            nlacp, _id_tokenizer, _id_model
        )
        if not is_nlacp:
            _status.update(
                label="Input is not an access control policy",
                state="error",
                expanded=False,
            )
        else:
            results.nlacps.append(nlacp)
            
            if do_align:
                st.write("Retrieving context ...")
                ents = get_available_entities(nlacp, _vectorstores, n=3)
                
                st.write("Translating ...")
                policy, success = generate_policy(
                    nlacp, _gen_tokenizer, _gen_model, ents
                )
            else:
                st.write("Translating ...")
                policy, success = generate_policy(
                    nlacp, _gen_tokenizer, _gen_model
                )
            
            if success:
                policy = filter_policy(policy)
                results.generated_nlacps.append(nlacp)
                results.generated_policies.append(policy)
                st.write("Verifying the translation ...")
                ver_result = verify(
                    nlacp, policy, _ver_model, _ver_tokenizer
                )
                
                results.init_verification.append(ver_result)
                # print(ver_result)
                if ver_result != 11:
                    st.write("Refining the translation ...")
                    policy, ver_result = verify_refine(
                        nlacp,
                        policy,
                        _ver_tokenizer,
                        _ver_model,
                        _gen_tokenizer,
                        _gen_model,
                    )
                results.final_verification.append(ver_result)
                results.final_policies.append(policy)
                
                if ver_result == 11:
                    
                    if do_align:
                        policy = align_policy(policy, _vectorstores, _hierarchy)
                    
                    json_policy = JSONPolicyRecord.from_dict({
                        'policyId': str(uuid4()),
                        'policyDescription': nlacp,
                        'policy': policy
                    })
                    
                    st.session_state.corrected_policies.append(
                        json_policy
                    )
                    results.final_correct_policies.append(json_policy)
                    st.session_state['policy_create_status'] = _ac_engine.create_policy(json_policy)
                    handlers.cor_policy_nav_last()
                else:
                    if ver_result != 10:
                        error_type = CAT2ERROR[ver_result]
                        error_loc = locate_error(
                            nlacp,
                            str(policy),
                            error_type,
                            _loc_model,
                            _loc_tokenizer,
                        )
                        warning = get_locate_warning_msg(error_type, error_loc)

                    else:
                        warning = get_locate_warning_missing_rule_msg()

                    st.session_state.inc_policies.append(
                        {
                            "nlacp": nlacp,
                            "policy": policy,
                            "warning": warning,
                            "solved": False
                        }
                    )
                    # handlers.inc_policy_nav_last()
                    handlers.inc_policy_nav_next()

            _status.update(
                label="Generation complete!", state="complete", expanded=False
            )
        st.session_state['results'] = results.to_dict()
        st.session_state.is_generating = False
    
    
# @st.cache_data(show_spinner=False)
def agentv_batch(ac_engine: AccessControlEngine, _status_container, content, _id_tokenizer, _id_model, _gen_tokenizer, _gen_model, _ver_model, _ver_tokenizer, _loc_tokenizer, _loc_model, _vectorstores, _hierarchy: Hierarchy):
    
    with _status_container.status("Generating policies ...", expanded=True) as _status:
        results = Results()
        
        st.write("Preprocessing ...")
        
        sentences = preprocess_document(content)['content']
        results.sentences = sentences
        # print(sentences)
        
        st.write("Looking for access requirements ...")
        
        data_loaders = DataLoaders(_id_tokenizer, _gen_tokenizer, _ver_tokenizer, _loc_tokenizer)
        id_loader = data_loaders.get_loader(results, Task.NLACP_ID, max_len=256, batch_size=8)
        results = get_nlacps(id_loader, _id_model, results)
        
        st.write("Retrieving context ...")
        
        for nlacp in results.nlacps:
            
            ents = get_available_entities(nlacp, _vectorstores, n=3)
            
            results.nlacps_context.append([nlacp, ents])
        
        
        st.write("Translating ...")
        
        for nlacp,context in results.nlacps_context:
        
            policy, success = generate_policy(
                nlacp, _gen_tokenizer, _gen_model, context=context
            )
        
            if success:
                
                policy = filter_policy(policy)
                results.generated_nlacps.append(nlacp)
                results.generated_policies.append(policy)
                results.converted_policies.append(convert_to_sent(policy)[0])
                
        st.write("Verifying the translation ...")
        
        ver_loader = data_loaders.get_loader(results, Task.POLICY_VER, max_len=1024, batch_size=8)
        
        results = verify_policies(ver_loader, _ver_model, results)
        
        st.write("Refining the translation ...")
        
        for i in range(len(results.generated_nlacps)):
            
            
            nlacp = results.generated_nlacps[i]
            policy = results.generated_policies[i]
            ver = results.init_verification[i]
            
            
            if ver == 11:
                
                policy = align_policy(policy, _vectorstores, _hierarchy)
                
                json_policy = JSONPolicyRecord.from_dict({
                    'policyId': str(uuid4()),
                    'policyDescription': nlacp,
                    'policy': policy
                })
                
                st.session_state.corrected_policies.append(
                    json_policy
                )
                
                results.final_correct_policies.append(json_policy)
            
            else:
                
                policy, ver = verify_refine(
                    nlacp,
                    policy,
                    _ver_tokenizer,
                    _ver_model,
                    _gen_tokenizer,
                    _gen_model,
                )
                
                if ver == 11:
                    
                    policy = align_policy(policy, _vectorstores, _hierarchy)
                    
                    json_policy = JSONPolicyRecord.from_dict({
                        'policyId': str(uuid4()),
                        'policyDescription': nlacp,
                        'policy': policy
                    })
                    
                    st.session_state.corrected_policies.append(
                        json_policy
                    )
                    
                    results.final_correct_policies.append(json_policy)
                    # handlers.cor_policy_nav_next()
                else:
                    if ver != 10:
                        error_type = CAT2ERROR[ver]
                        error_loc = locate_error(
                            nlacp,
                            str(policy),
                            error_type,
                            _loc_model,
                            _loc_tokenizer,
                        )
                            
                        warning = get_locate_warning_msg(error_type, error_loc)
                        st.session_state.inc_policies.append(
                            {
                                "nlacp": nlacp,
                                "policy": policy,
                                "warning": warning,
                                "solved": False
                            }
                        )

                    else:
                        warning = get_locate_warning_missing_rule_msg()

                        st.session_state.inc_policies.append(
                            {
                                "nlacp": nlacp,
                                "policy": policy,
                                "warning": warning,
                                "solved": False
                            }
                        )
                    
                
            results.final_policies.append(policy)
            results.final_verification.append(ver)
            
        
        if len(st.session_state.corrected_policies) >= 1:
            handlers.cor_policy_nav_next()
        if len(st.session_state.inc_policies) >= 1:
            handlers.inc_policy_nav_next()
            
        _status.update(
                label="Generation complete!", state="complete", expanded=False
            )
        
        st.session_state['results'] = results.to_dict()
        st.session_state.is_generating = False
        st.session_state['policy_create_status'] = ac_engine.create_multiple_policies(results.final_correct_policies)
    
            
            
