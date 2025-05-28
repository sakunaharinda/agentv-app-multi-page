import streamlit as st
from ac_engine_service import AccessControlEngine
from utils import change_page_icon, save
from models.ac_engine_dto import JSONPolicyRecord, JSONPolicyRecordPDP
from loading import load_policy
from ml_layer import align_policy
import ast
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pandas as pd
from vectorstore import create_bm25_retriever
import bm25s

def delete_single(pdp_policy: JSONPolicyRecordPDP, ac_engine: AccessControlEngine):
    
    status = ac_engine.delete_policy_by_id(pdp_policy.policyId)
    if status == 200:
        st.toast("Policy is deleted from the database successfully.", icon=":material/check:")
        st.session_state.pdp_policies.remove(pdp_policy)
        pdp_policy.published = False
        ac_engine.create_policy_json(pdp_policy)

def publish_single(pdp_policy: JSONPolicyRecordPDP, ac_engine: AccessControlEngine):
    
    change_page_icon('correct_pol_icon')
            
    status = ac_engine.create_policy(pdp_policy.to_json_record())

    if status == 200:
        if pdp_policy not in st.session_state.pdp_policies:
            pdp_policy.published = True
            st.session_state.pdp_policies.append(pdp_policy)
            # st.session_state.pdp_policies = list(set(st.session_state.pdp_policies))
            
            ac_engine.create_policy_json(pdp_policy)
            st.toast(f"Policy {pdp_policy.policyId} is published successfully. Go to **Test Policies** page to test it.", icon=":material/check:")
    
def get_updated_description(policy: JSONPolicyRecordPDP):
    
    if policy.published:
        
        new_description = policy.policyDescription + " :green-badge[:material/check: Published]"
    else:
        new_description = policy.policyDescription + " :orange-badge[:material/publish: Ready to Publish]"
        
    if not policy.with_context:
        
        new_description+= " :red-badge[:material/family_history: Outside context]"
        
    return new_description

    
def publish_all(ac_engine: AccessControlEngine, count: int):
    
    change_page_icon('correct_pol_icon')
    
    if count == 0 or count == len(st.session_state.corrected_policies_pdp):
        policies = st.session_state.corrected_policies
        status = ac_engine.create_multiple_policies(policies)
        
        if status == 200:
            st.toast(f"All the policies are published successfully. Go to **Test Policies** page to test them.", icon=":material/check:")
            for policy in st.session_state.corrected_policies_pdp:
                if policy.published == False:
                    policy.published = True
                    st.session_state.pdp_policies.append(policy)
            
    else:
        
        policies = [k.to_json_record() for k in st.session_state.corrected_policies_pdp if k.ready_to_publish==True]
        status = ac_engine.create_multiple_policies(policies)
        
        if status == 200:
            st.toast(f"All the selected policies are published successfully. Go to **Test Policies** page to test them.", icon=":material/check:")
            for policy in st.session_state.corrected_policies_pdp:
                if not policy.published and policy.ready_to_publish:
                    policy.published = True
                    st.session_state.pdp_policies.append(policy)
                    
    ac_engine.create_multiple_policies_json(st.session_state.pdp_policies)

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
        
def publish_delete_policy(policy: JSONPolicyRecordPDP, ac_engine, col, col_delete):
    
    col.button("Publish", key=f"publish_{policy.policyId}", use_container_width=True, on_click=publish_single, args=(policy, ac_engine,), type='primary', help = "Publish the policy to the policy database", disabled=policy.published, icon=":material/database_upload:")
    
    col_delete.button("Unpublish", use_container_width=True, key = f"remove_{policy.policyId}", type='primary', help = "Remove the published policy from the policy database", disabled=not policy.published, icon=":material/delete:", on_click=delete_single, args=(policy, ac_engine,))
    
    
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
    
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column('rule', header_name="Rule ID", editable=True)
    gb.configure_column('Decision', editable=True, cellEditor='agSelectCellEditor',
        cellEditorParams={'values': ['allow', 'deny']})
    
    if hierarchy != None and not st.session_state.no_hierarchy:
    
        subjects, actions, resources = update_options(df, get_options(hierarchy['subject_hierarchy']), get_options(hierarchy['action_hierarchy']), get_options(hierarchy['resource_hierarchy']))

        gb.configure_column('Subject', editable=True, cellEditor='agSelectCellEditor',
            cellEditorParams={'values': subjects})
        gb.configure_column('Action', editable=True, cellEditor='agSelectCellEditor',
            cellEditorParams={'values': actions})
        gb.configure_column('Resource', editable=True, cellEditor='agSelectCellEditor',
            cellEditorParams={'values': resources})
    else:
        gb.configure_column('Subject', editable=True)
        gb.configure_column('Action', editable=True)
        gb.configure_column('Resource', editable=True)
        
    
    
    gb.configure_column('Condition', editable=True)
    gb.configure_column('Purpose', editable=True)
    gb.configure_grid_options(domLayout='autoHeight')
    
    
    if error_ids != None:
        for row in error_ids:
            highlights.append((row, error_type.capitalize()))
        if not inc_policy['solved']:
            highlight_errors(highlights, gb)
    
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
    
    if st.session_state.do_align:
        policy, outside_hierarchy = align_policy(corrected_policy, models.vectorestores, hierarchy, chroma=st.session_state.use_chroma)
    else:
        policy = corrected_policy
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
    
    # st.session_state.models.vectorestores['nlacps'].add(documents=[json_policy.policyDescription], ids=[json_policy.policyId])
    
    inc_policy['policy'] = ast.literal_eval(edited_df.to_json(orient='records'))
    inc_policy['solved'] = True
    change_page_icon('incorrect_pol_icon')
    inc_policy['show'] = False
    
def filter_by_nlacp(nlacp, filtered_policies):
    retriever = create_bm25_retriever(filtered_policies)
    results, scores = retriever.retrieve(bm25s.tokenize(nlacp), k=len(filtered_policies))
    mask = scores > 0
    return results[mask].tolist()
    
    
def filter(original_list, filter_container):
    
    with filter_container.expander("Filter", icon = ":material/tune:"):
        by_id = st.multiselect(
            "By Policy Id", [policy.policyId for policy in original_list], default=[], placeholder="Select a policy ID", key="correct_filter_id", disabled=len(original_list)==0
        )
        
        by_nlacp = st.text_input(
            label="By Text",
            placeholder="Enter a part or the complete access requirement",
            key="correct_filter_nlacp",
            disabled=len(original_list)==0
        )
        
        if by_id != []:
            
            filtered_policies = [policy for policy in original_list if policy.policyId in by_id]
                
            
        else:
            filtered_policies = original_list
            
        if by_nlacp:
            filtered_policies = filter_by_nlacp(by_nlacp, filtered_policies)
            
    return filtered_policies
    
    