import streamlit as st
from ac_engine_service import AccessControlEngine
from utils import change_page_icon, save
from models.ac_engine_dto import JSONPolicyRecord, JSONPolicyRecordPDP
from loading import load_policy
from ml_layer import align_policy
import ast
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pandas as pd

def publish_single(pdp_policy: JSONPolicyRecordPDP, ac_engine: AccessControlEngine):
    
    change_page_icon('correct_pol_icon')
            
    status = ac_engine.create_policy(pdp_policy.to_json_record())

    if status == 200:
        if pdp_policy not in st.session_state.pdp_policies:
            st.session_state.pdp_policies.append(pdp_policy)
            # st.session_state.pdp_policies = list(set(st.session_state.pdp_policies))
            set_published(pdp_policy)
    
def get_updated_description(policy: JSONPolicyRecordPDP):
    
    if policy.published:
        
        return policy.policyDescription + " :green-badge[:material/check: Published]"
    else:
        return policy.policyDescription + " :orange-badge[:material/publish: Ready to Publish]"
    
def set_published(policy: JSONPolicyRecordPDP):
        
    policy.published = True
        
    return policy
    
    
def publish_all(ac_engine: AccessControlEngine, count: int):
    
    change_page_icon('correct_pol_icon')
    
    if count == 0 or count == len(st.session_state.corrected_policies_pdp):
        policies = st.session_state.corrected_policies
        status = ac_engine.create_multiple_policies(policies)
        
        if status == 200:
            for policy in st.session_state.corrected_policies_pdp:
                if policy.published == False:
                    policy.published = True
                    st.session_state.pdp_policies.append(policy)
            # st.session_state.corrected_policies_pdp = list(map(set_published, st.session_state.corrected_policies_pdp))
            
            # st.session_state.pdp_policies.extend(st.session_state.corrected_policies_pdp)
            # st.session_state.pdp_policies = list(set(st.session_state.pdp_policies))
            
    else:
        
        policies = [k.to_json_record() for k in st.session_state.corrected_policies_pdp if k.ready_to_publish==True]
        status = ac_engine.create_multiple_policies(policies)
        
        if status == 200:
            for policy in st.session_state.corrected_policies_pdp:
                if not policy.published and policy.ready_to_publish:
                    policy.published = True
                    st.session_state.pdp_policies.append(policy)
                    
        
        

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
        subject = df.iloc[i]['Subject']
        action = df.iloc[i]['Action']
        resource = df.iloc[i]['Resource']
        
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


def highlight_errors(highlights, gb: GridOptionsBuilder):
    for highlight in highlights:
        row_index, column_field = highlight
        cell_style_jscode = JsCode(f"""
        function(params) {{
            if (params.node.rowIndex === {row_index}) {{
                return {{
                    'backgroundColor': '#FAE7E9',
                    'color': 'black'
                }}
            }}
            return null;
        }}
        """)
        gb.configure_column(column_field, cellStyle=cell_style_jscode)

def review_policy_aggrid(inc_policy, err_info, hierarchy, models):
    # TODO: Cannot add new rows as of now
    
    highlights = []
    
    error_ids, error_type = err_info
    
    pol_id = inc_policy['id']
    df = load_policy(inc_policy['policy'])
    df.insert(0, 'rule', [i+1 for i in range(len(df))])
    
    subjects, actions, resources = update_options(df, get_options(hierarchy['subject_hierarchy']), get_options(hierarchy['action_hierarchy']), get_options(hierarchy['resource_hierarchy']))
    
    gb = GridOptionsBuilder.from_dataframe(df)
    
    if error_ids != None:
        for row in error_ids:
            highlights.append((row, error_type.capitalize()))
        if not inc_policy['solved']:
            highlight_errors(highlights, gb)
        
    gb.configure_column('rule', header_name="Rule ID", editable=True)
    gb.configure_column('Decision', editable=True, cellEditor='agSelectCellEditor',
        cellEditorParams={'values': ['allow', 'deny']})
    gb.configure_column('Subject', editable=True, cellEditor='agSelectCellEditor',
        cellEditorParams={'values': subjects})
    gb.configure_column('Action', editable=True, cellEditor='agSelectCellEditor',
        cellEditorParams={'values': actions})
    gb.configure_column('Resource', editable=True, cellEditor='agSelectCellEditor',
        cellEditorParams={'values': resources})
    gb.configure_column('Condition', editable=True)
    gb.configure_column('Purpose', editable=True)
    gb.configure_grid_options(domLayout='autoHeight')
    grid_options = gb.build()
    grid_return = AgGrid(df, gridOptions=grid_options,
        width='100%',
        allow_unsafe_jscode=True, fit_columns_on_grid_load=True, editable=True,
        # pinned_top_row_data=[pinned_row]
        key=f'incorrect_policy_{pol_id}'
        )
    st.button("Submit", key=f'submit_inc_btn_{pol_id}', use_container_width=True, type='primary', on_click=submit_corrected_policy, args=(inc_policy, grid_return['data'], hierarchy, models,), icon=":material/send:")

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
            "Decision": st.column_config.SelectboxColumn(
                "Decision",
                help="The access control rule decision",
                width="small",
                options=[
                    "allow",
                    "deny",
                ],
                required=True,
            ),
            "Subject": st.column_config.SelectboxColumn(
                "Subject",
                help="The subject of the access control rule",
                width="small",
                options=subjects,
                required=True
            ),
            "Action": st.column_config.SelectboxColumn(
                "Action",
                help="The action of the access control rule",
                width="small",
                options=actions,
                required=True
            ),
            "Resource": st.column_config.SelectboxColumn(
                "Resource",
                help="The resource of the access control rule",
                width="small",
                options=resources,
                required=True
            ),
        },
    )
    
    st.button("Submit", key=f'submit_inc_btn_{pol_id}', use_container_width=True, type='primary', on_click=submit_corrected_policy, args=(inc_policy, edited_df, hierarchy, models,), icon=":material/send:")
        
    
def submit_corrected_policy(inc_policy, edited_df: pd.DataFrame, hierarchy, models):
    
    edited_df = edited_df.drop('rule', axis='columns')
    edited_df.columns = edited_df.columns.str.lower()
    corrected_policy = [v for _, v in edited_df.to_dict("index").items()]
    policy, outside_hierarchy = align_policy(corrected_policy, models.vectorestores, hierarchy, chroma=st.session_state.use_chroma)
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
    inc_policy['show'] = False
    
def make_ready(object):
    object.ready_to_publish = True
    # else:
    #     st.session_state.select_count = max(0, st.session_state.select_count-1)
    