import streamlit as st
from ac_engine_service import AccessControlEngine
from utils import change_page_icon, save
from models.ac_engine_dto import JSONPolicyRecord, JSONPolicyRecordPDP
from loading import load_policy
from ml_layer import align_policy
import ast

def publish_single(pdp_policy: JSONPolicyRecordPDP, ac_engine: AccessControlEngine):
    
    change_page_icon('correct_pol_icon')
            
    status = ac_engine.create_policy(pdp_policy.to_json_record())

    if status == 200:
        st.session_state.pdp_policies.append(pdp_policy)
        st.session_state.pdp_policies = list(set(st.session_state.pdp_policies))
        set_published(pdp_policy)
    
def get_updated_description(policy: JSONPolicyRecordPDP):
    
    if policy.published:
        
        return policy.policyDescription + " :green-badge[:material/check: Published]"
    else:
        return policy.policyDescription + " :orange-badge[:material/publish: Ready to Publish]"
    
def set_published(policy: JSONPolicyRecordPDP):
        
    policy.published = True
        
    return policy
    
    
def publish_all(ac_engine: AccessControlEngine):
    
    change_page_icon('correct_pol_icon')
    
    policies = st.session_state.corrected_policies
    status = ac_engine.create_multiple_policies(policies)
    
    if status == 200:
        st.session_state.corrected_policies_pdp = list(map(set_published, st.session_state.corrected_policies_pdp))
        
        st.session_state.pdp_policies.extend(st.session_state.corrected_policies_pdp)
        st.session_state.pdp_policies = list(set(st.session_state.pdp_policies))
        
        st.switch_page("pages/test_policies.py")
        
        

@st.dialog(title="Publish to Policy Database")
def policy_db_feedback(status_code, single = False):
    
    if status_code == 200:
        if single:
            st.success("The policy is published to the policy database successfully!", icon=':material/check_circle:')
        else:
            st.success("All the policies are published to the policy database successfully!", icon=':material/check_circle:')
        
    else:
        if single:
            st.error(f"An error occured with the HTTP status code {status_code} while trying to publish the policy to the policy database.", icon=':material/dangerous:')
        else:
            st.error(f"An error occured with the HTTP status code {status_code} while trying to publish the policies to the policy database.", icon=':material/dangerous:')
        
    ok = st.button("OK", key='ok_publish', use_container_width=True, type='primary')
    
    if ok and not single:
        st.switch_page("pages/test_policies.py")
    elif ok:
        st.rerun()
        
        
def publish_policy(policy: JSONPolicyRecordPDP, ac_engine, col):
    
    # _,_,col = st.columns([1,1,1])
    
    col.button("Publish", key=f"publish_{policy.policyId}", use_container_width=True, on_click=publish_single, args=(policy, ac_engine,), type='primary', help = "Publish the policy to the policy database", disabled=policy.published, icon=":material/database_upload:")
    
    
def get_updated_description_inc(inc_policy):
    if inc_policy['solved']:
        
        return inc_policy['nlacp'] + " :green-badge[:material/check: Submitted]"
    else:
        return inc_policy['nlacp'] + " :orange-badge[:material/reviews: Ready to Review]"

@st.cache_data(show_spinner=False)
def update_options(df, subjects, actions, resources):
    
    for i in range(len(df)):
        subject = df.iloc[i]['subject']
        action = df.iloc[i]['action']
        resource = df.iloc[i]['resource']
        
        if subject not in subjects:
            subjects.append(subject)
        if action not in actions:
            actions.append(action)
        if resource not in resources:
            resources.append(resource)
            
    return subjects, actions, resources

@st.cache_data(show_spinner=False)
def get_options(h: dict):
    values = []
    for k, v in h.items():
        values.append(k)
        values.extend(v)
        
    return sorted(list(set(values)))

def review_policy(inc_policy, hierarchy, models):
    
    pol_id = inc_policy['id']
    df = load_policy(inc_policy['policy'])
    df.insert(0, 'rule', [i+1 for i in range(len(df))])
    
    subjects, actions, resources = update_options(df, get_options(hierarchy['subject_hierarchy']), get_options(hierarchy['action_hierarchy']), get_options(hierarchy['resource_hierarchy']))
    
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key="corrected_policy",
        column_config={
            "decision": st.column_config.SelectboxColumn(
                "decision",
                help="The access control rule decision",
                width="small",
                options=[
                    "allow",
                    "deny",
                ],
                required=True,
            ),
            "subject": st.column_config.SelectboxColumn(
                "subject",
                help="The subject of the access control rule",
                width="small",
                options=subjects,
                required=True
            ),
            "action": st.column_config.SelectboxColumn(
                "action",
                help="The action of the access control rule",
                width="small",
                options=actions,
                required=True
            ),
            "resource": st.column_config.SelectboxColumn(
                "resource",
                help="The resource of the access control rule",
                width="small",
                options=resources,
                required=True
            ),
        },
    )
    
    st.button("Submit", key=f'submit_inc_btn_{pol_id}', use_container_width=True, type='primary', on_click=submit_corrected_policy, args=(inc_policy, edited_df, hierarchy, models,), icon=":material/send:")
        
    
def submit_corrected_policy(inc_policy, edited_df, hierarchy, models):
    
    edited_df = edited_df.drop('rule', axis='columns')
    corrected_policy = [v for _, v in edited_df.to_dict("index").items()]
    policy = align_policy(corrected_policy, models.vectorestores, hierarchy)
    json_policy = JSONPolicyRecord.from_dict({
        'policyId': inc_policy['id'],
        'policyDescription': inc_policy['nlacp'],
        'policy': policy
        }
    )
    
    save(
        json_policy,
        enforce_unique=True
    )
    
    inc_policy['policy'] = ast.literal_eval(edited_df.to_json(orient='records'))
    inc_policy['solved'] = True
    change_page_icon('incorrect_pol_icon')