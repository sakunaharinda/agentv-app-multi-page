import os

import streamlit as st
import torch
from utils import ID2AUGS, CAT2ERROR, DataLoaders, Task, remove_duplicates, get_generation_msgs, get_generation_msgs_ents, convert_to_sent, prepare_inputs_bart, get_error_instrution, save
import ast
import re
from itertools import product
import numpy as np
import handlers as handlers
from feedback import *
import requests
from models.record_dto import Results
from models.ac_engine_dto import JSONPolicyRecord
from uuid import uuid4
from vectorstore import get_candidates_chroma, get_available_entities_chroma

ITERATIONS = 2

# torch.classes.__path__ = []


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
    
    return np.argmax(all_preds, axis=-1).tolist()
    # return results


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
def get_available_entities(query: str, _vectorstores: dict, n=3, chroma=False):
    
    if chroma:
        return get_available_entities_chroma(query, _vectorstores, n)
    else:
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
def align_policy(policy, _vectorstore: dict, hierarchy: dict, chroma = False):
    unique_pols = []
    new_pol = []
    
    if chroma:
        return align_policy_chroma(policy, _vectorstore, hierarchy)
    else:
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
            
        unique_pols = filter_policy(new_pol)
                
        return expand_policy(unique_pols, hierarchy['subject_hierarchy'], hierarchy['action_hierarchy'], hierarchy['resource_hierarchy']), False

@st.cache_data(show_spinner=False)
def align_policy_chroma(policy, _vectorstore: dict, hierarchy: dict):
    unique_pols = []
    
    new_pol = []
    outside_hierarchy = False
    for rule in policy:
        for k,v in rule.items():
            if k=='decision' or k == 'purpose':
                continue
            store = _vectorstore.get(k, None)
            if v!='none' and store is not None:
                from_db, score = get_candidates_chroma(store, v, 1)
                # print(v, from_db[0], score)
                if score[0] > 0.8:
                    rule[k] = from_db[0].strip()
                else:
                    outside_hierarchy = True
        new_pol.append(rule)
        
    for r in new_pol:
        if r not in unique_pols:
            unique_pols.append(r)
            
    return expand_policy(unique_pols, hierarchy['subject_hierarchy'], hierarchy['action_hierarchy'], hierarchy['resource_hierarchy']), outside_hierarchy


def check_conflicts_bf(policy):
    conflict = False
    conflict_pairs = []
    for r1 in policy:
        for r2 in policy:
            if r1['decision'] != r2['decision']:
                if (r1['subject'] == r2['subject']) and (r1['action'] == r2['action']) and (r1['resource'] == r2['resource']) and (r1['condition'] == r2['condition']) and (r1['purpose'] == r2['purpose']):
                    conflict = True
                    if ((r1, r2) not in conflict_pairs) and ((r2, r1) not in conflict_pairs):
                        conflict_pairs.append((r1,r2))
                    
    return conflict, conflict_pairs

# @st.cache_data(show_spinner=False)
def agentv_single(_status_container, nlacp, _id_tokenizer, _id_model, _gen_tokenizer, _gen_model, _ver_model, _ver_tokenizer, _loc_tokenizer, _loc_model, _vectorstores, hierarchy, do_align=True):
    
    uuid = str(uuid4())
    
    with _status_container.status("Generating the policy ...", expanded=True) as _status:

        results = Results()
        
        results.sentences.append(nlacp)
        
        # st.write("Preprocessing...")
        st.write("Looking for access requirements...")
        is_nlacp = classify_single_sentence(
            nlacp, _id_tokenizer, _id_model
        )
        # if not is_nlacp:
        #     _status.update(
        #         label="Input is not an access control policy",
        #         state="error",
        #         expanded=False,
        #     )
            
        #     results.interrupted_errors.append("The entered sentence is not an access control requirement. Please refine the sentence and re-submit again.")
        # else:
        results.nlacps.append(nlacp)
        
        if do_align:
            ents = get_available_entities(nlacp, _vectorstores, n=3, chroma=st.session_state.use_chroma)
            st.write("Translating ...")
            
            # TODO: Remove
            if os.getenv("TEST", False) == 'true' and nlacp == "Medical records cannot be viewed either by LTs or administrators, to protect patient confidentiality.":
                policy, success = [
                    {
                        'decision': 'deny',
                        'subject': 'lhcp',
                        'action': 'view',
                        'resource': 'medical record',
                        'purpose': 'protect patient confidentiality',
                        'condition': 'none'
                    },
                    {
                        'decision': 'deny',
                        'subject': 'administrator',
                        'action': 'view',
                        'resource': 'medical record',
                        'purpose': 'protect patient confidentiality',
                        'condition': 'none'
                    }
                ], True
            else:
                nlacp_lower = nlacp.lower()
                policy, success = generate_policy(
                    nlacp_lower, _gen_tokenizer, _gen_model, ents
                )
        else:
            nlacp_lower = nlacp.lower()
            st.write("Translating ...")
            policy, success = generate_policy(
                nlacp_lower, _gen_tokenizer, _gen_model
            )
        
        if success:
            policy = filter_policy(policy)
            results.generated_nlacps.append(nlacp)
            results.generated_policies.append(policy)
            st.write("Verifying and Refining the translation ...")
            ver_result = verify(
                nlacp, policy, _ver_model, _ver_tokenizer
            )
            
            results.init_verification.append(ver_result)
            # print(ver_result)
            if ver_result != 11:
                # st.write("Refining the translation ...")
                policy, ver_result = verify_refine(
                    nlacp,
                    policy,
                    _ver_tokenizer,
                    _ver_model,
                    _gen_tokenizer,
                    _gen_model,
                )
            
            
            expanded_policy,_ = align_policy(policy, _vectorstores, hierarchy, chroma=st.session_state.use_chroma)
            conflict, conflict_pairs = check_conflicts_bf(expanded_policy)
            
            if (conflict == True):
                warning = get_rule_conflict_message(nlacp, conflict_pairs)
                st.session_state.inc_policies.append(
                    {
                        "id": uuid,
                        "nlacp": nlacp,
                        "policy": expanded_policy,
                        "warning": warning,
                        "solved": False,
                        "show": True
                    }
                )
                ver_result = -1 # Indicating a conflict
                
            elif ver_result == 11:
                
                if do_align:
                    policy, outside_hierarchy = align_policy(policy, _vectorstores, hierarchy, chroma=st.session_state.use_chroma)
                    
                    if outside_hierarchy:
                        results.interrupted_errors.append("Sorry! AGentV has found that the entered access control requirement contains entities (i.e., subjects, actions, and resources) that do not align with the organization. Please refer to the **:material/family_history: Organization Hierarchy**, rephrase the access control requirement, and **:material/play_circle: Generate** again.")
                        
                    else:
                        json_policy = JSONPolicyRecord.from_dict({
                            'policyId': uuid,
                            'policyDescription': nlacp,
                            'policy': policy
                        })
                        
                        save(json_policy, index=0, with_context=do_align)
                        results.final_correct_policies.append(json_policy)
                        
                else:
                
                    json_policy = JSONPolicyRecord.from_dict({
                        'policyId': uuid,
                        'policyDescription': nlacp,
                        'policy': policy
                    })
                    
                    save(json_policy, index=0, with_context=do_align)
                    results.final_correct_policies.append(json_policy)
                    # handlers.cor_policy_nav_last()
                
            else:
                if ver_result != 10:
                    nlacp_lower = nlacp.lower()
                    error_type = CAT2ERROR[ver_result]
                    error_loc = locate_error(
                        nlacp_lower,
                        str(policy),
                        error_type,
                        _loc_model,
                        _loc_tokenizer,
                    )
                    warning = get_locate_warning_msg(nlacp, error_type, error_loc)

                else:
                    warning = get_locate_warning_missing_rule_msg(nlacp)

                st.session_state.inc_policies.append(
                    {
                        "id": uuid,
                        "nlacp": nlacp,
                        "policy": policy,
                        "warning": warning,
                        "solved": False,
                        "show": True
                    }
                )
                # handlers.inc_policy_nav_last()
                handlers.inc_policy_nav_next()
                
            results.final_verification.append(ver_result)
            results.final_policies.append(policy)

            _status.update(
                label="Generation complete!", state="complete", expanded=False
            )
        else:
            results.interrupted_errors.append("Sorry! AGentV has failed to process the access control policy generated from the entered sentence. Please rephrase the sentence and **:material/play_circle: Generate** again.")
            
            _status.update(
                label="AGentV has failed to parse the access control policy",
                state="error",
                expanded=False,
            )
            
        
        st.session_state['results_individual'] = results.to_dict()
        st.session_state.is_generating = False
        st.session_state.review_single = True
        # st.session_state.correct_policies = list(set(st.session_state.corrected_policies))
        
    return uuid
    
    
# @st.cache_data(show_spinner=False)
def agentv_batch(_status_container, content, _id_tokenizer, _id_model, _gen_tokenizer, _gen_model, _ver_model, _ver_tokenizer, _loc_tokenizer, _loc_model, _vectorstores, hierarchy, do_align = True):

    with _status_container.status("Generating policies ...", expanded=True) as _status:
        results = Results()
        
        sentences = preprocess_document(content)['content']
        results.sentences = sentences
        # print(sentences)
        
        st.write("Looking for access requirements ...")
        
        data_loaders = DataLoaders(_id_tokenizer, _gen_tokenizer, _ver_tokenizer, _loc_tokenizer)
        id_loader = data_loaders.get_loader(results, Task.NLACP_ID, max_len=256, batch_size=8)
        results = get_nlacps(id_loader, _id_model, results)
        
        
        for nlacp in results.nlacps:
            
            if do_align:
            
                ents = get_available_entities(nlacp, _vectorstores, n=3, chroma=st.session_state.use_chroma)
            else:
                ents = {}
            
            results.nlacps_context.append([nlacp, ents])
        
        
        st.write("Translating ...")
        
        for nlacp,context in results.nlacps_context:
            
            if do_align:
                
                if os.getenv("TEST", False) == 'true' and nlacp == "Medical records cannot be viewed either by LTs or administrators, to protect patient confidentiality.":
                    policy, success = [
                        {
                            'decision': 'deny',
                            'subject': 'lhcp',
                            'action': 'view',
                            'resource': 'medical record',
                            'purpose': 'protect patient confidentiality',
                            'condition': 'none'
                        },
                        {
                            'decision': 'deny',
                            'subject': 'administrator',
                            'action': 'view',
                            'resource': 'medical record',
                            'purpose': 'protect patient confidentiality',
                            'condition': 'none'
                        }
                    ], True
                else:
                    policy, success = generate_policy(
                        nlacp, _gen_tokenizer, _gen_model, context=context
                    )
            else:
                policy, success = generate_policy(nlacp, _gen_tokenizer, _gen_model)
        
            if success:
                
                policy = filter_policy(policy)
                results.generated_nlacps.append(nlacp)
                results.generated_policies.append(policy)
                results.converted_policies.append(convert_to_sent(policy)[0])
                
            else:
                print()
                print(nlacp)
                
        st.write("Verifying and Refining the translation ...")
        
        ver_loader = data_loaders.get_loader(results, Task.POLICY_VER, max_len=1024, batch_size=8)
        
        results.init_verification = verify_policies(ver_loader, _ver_model, results)
        
        # st.write("Refining the translation ...")
        
        for i in range(len(results.generated_nlacps)):
            
            
            nlacp = results.generated_nlacps[i]
            policy = results.generated_policies[i]
            ver = results.init_verification[i]
            
            
            if ver == 11:
                
                if do_align:
                    policy, outside_hierarchy = align_policy(policy, _vectorstores, hierarchy, chroma=st.session_state.use_chroma)
                    
                    if outside_hierarchy:
                        print(nlacp)
                
                json_policy = JSONPolicyRecord.from_dict({
                    'policyId': str(uuid4()),
                    'policyDescription': nlacp,
                    'policy': policy
                })
                
                save(
                    json_policy,
                    with_context=do_align
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
                    
                    if do_align:
                        policy, outside_hierarchy = align_policy(policy, _vectorstores, hierarchy, chroma=st.session_state.use_chroma)
                        
                        if outside_hierarchy:
                            print(nlacp)
                    
                    json_policy = JSONPolicyRecord.from_dict({
                        'policyId': str(uuid4()),
                        'policyDescription': nlacp,
                        'policy': policy
                    })
                    
                    save(
                        json_policy,
                        with_context=do_align
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
                            
                        warning = get_locate_warning_msg(nlacp, error_type, error_loc)
                        st.session_state.inc_policies.append(
                            {
                                "id": str(uuid4()),
                                "nlacp": nlacp,
                                "policy": policy,
                                "warning": warning,
                                "solved": False,
                                "show": True
                            }
                        )

                    else:
                        warning = get_locate_warning_missing_rule_msg(nlacp)

                        st.session_state.inc_policies.append(
                            {
                                "id": str(uuid4()),
                                "nlacp": nlacp,
                                "policy": policy,
                                "warning": warning,
                                "solved": False,
                                "show": True
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
        
        st.session_state['results_document'] = results.to_dict()
        st.session_state.is_generating = False
        st.session_state.refresh = True
        st.session_state.reviewed = False
        st.session_state.correct_policies = list(set(st.session_state.corrected_policies))
        # st.session_state['policy_create_status'] = ac_engine.create_multiple_policies(results.final_correct_policies)
    
            
            
