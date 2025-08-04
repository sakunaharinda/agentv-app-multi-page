import streamlit as st
from ac_engine_service import AccessControlEngine
from utils import change_page_icon, save, get_random_colors
from models.ac_engine_dto import JSONPolicyRecord, JSONPolicyRecordPDP
from loading import load_policy
from ml_layer import align_policy
import ast
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode
import pandas as pd
from vectorstore import create_bm25_retriever
import bm25s
from feedback import success_publish_feedback, success_delete_feedback, success_refine_feedback

def delete_single(pdp_policy: JSONPolicyRecordPDP, ac_engine: AccessControlEngine):
    
    status = ac_engine.delete_policy_by_id(pdp_policy.policyId)
    if status == 200:
        # st.toast("Policy is deleted from the database successfully.", icon=":material/check:")
        success_delete_feedback()
        st.session_state.pdp_policies.remove(pdp_policy)
        pdp_policy.published = False
        pdp_policy.ready_to_publish = False
        ac_engine.create_policy_json(pdp_policy)

def publish_single(pdp_policy: JSONPolicyRecordPDP, ac_engine: AccessControlEngine):
    
    change_page_icon('correct_pol_icon')
            
    status = ac_engine.create_policy(pdp_policy.to_json_record())

    if status == 200:
        if pdp_policy not in st.session_state.pdp_policies:
            pdp_policy.published = True
            pdp_policy.ready_to_publish = True
            st.session_state.pdp_policies.insert(0, pdp_policy)
            # st.session_state.pdp_policies = list(set(st.session_state.pdp_policies))
            
            ac_engine.create_policy_json(pdp_policy)
            # st.toast(f"Policy {pdp_policy.policyId} is published successfully. Go to **Test Policies** page to test it.", icon=":material/check:")
            success_publish_feedback('single')
    
def get_updated_description(policy: JSONPolicyRecordPDP):
    
    if policy.published:
        
        new_description = policy.policyDescription + " :green-badge[:material/check: Published]"
    else:
        new_description = policy.policyDescription + " :orange-badge[:material/publish: Ready to Publish]"
        
    if not policy.with_context:
        
        new_description+= " :red-badge[:material/family_history: Outside context]"
        
    return "**" + new_description + "**"

    
def publish_all(ac_engine: AccessControlEngine, count: int, policies_to_pdp: list):
    
    change_page_icon('correct_pol_icon')
    
    if count == 0:
        # policies = st.session_state.corrected_policies
        policies = [k.to_json_record() for k in policies_to_pdp]
        status = ac_engine.create_multiple_policies(policies)
        
        if status == 200:
            # st.toast(f"All the policies are published successfully. Go to **Test Policies** page to test them.", icon=":material/check:")
            success_publish_feedback('multiple')
            for policy in st.session_state.corrected_policies_pdp:
                if policy in policies_to_pdp and policy.published == False:
                    policy.published = True
                    policy.ready_to_publish = True
                    st.session_state.pdp_policies.append(policy)
            
    else:
        
        policies = [k.to_json_record() for k in st.session_state.corrected_policies_pdp if k.ready_to_publish==True]
        status = ac_engine.create_multiple_policies(policies)
        
        if status == 200:
            # st.toast(f"All the selected policies are published successfully. Go to **Test Policies** page to test them.", icon=":material/check:")
            success_publish_feedback('multiple')
            for policy in st.session_state.corrected_policies_pdp:
                if not policy.published and policy.ready_to_publish:
                    policy.published = True
                    policy.ready_to_publish = True
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
    
    col.button("Publish", key=f"publish_{policy.policyId}", use_container_width=True, on_click=publish_single, args=(policy, ac_engine,), type='primary', help = "Publish the policy to AGentV's policy database.", disabled=policy.published, icon=":material/database_upload:")
    
    col_delete.button("Unpublish", use_container_width=True, key = f"remove_{policy.policyId}", type='primary', help = "Remove the published policy from AGentV's policy database.", disabled=not policy.published, icon=":material/delete:", on_click=delete_single, args=(policy, ac_engine,))
    
    
def get_updated_description_inc(inc_policy):
    if inc_policy['solved']:
        
        return "**" + inc_policy['nlacp'] + " :green-badge[:material/check: Submitted]" + "**"
    else:
        return "**" + inc_policy['nlacp'] + " :orange-badge[:material/reviews: Ready to Review]" + "**"

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


def highlight_rows(row_highlights, gb: GridOptionsBuilder):
    js_func = JsCode(f"""
        function(params) {{
            const map = {row_highlights};
            const color = map[params.node.rowIndex];
            if (color !== undefined) {{
                return {{
                    backgroundColor: color,
                    color: 'black'
                }};
            }}
        }}
    """)
    gb.configure_grid_options(getRowStyle=js_func)


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
        
def add_rule_ids(policy):
    p = []
    for i,rule in enumerate(policy):
        rule['rule'] = i+1
        p.append(rule)
    return p

def get_conflicting_rule_ids(df, conflicts):
    all_ids = []
    for pair in conflicts:
        ids = []
        for r in pair:
            df_row = df[(df['Decision'] == r['decision']) & (df['Subject'] == r['subject']) & (df['Action'] == r['action']) & (df['Resource'] == r['resource'])]
            if len(df_row) > 0:
                ids.append(df_row['rule'].item())
        if len(ids) > 1:
            all_ids.append(ids)
            
    colors = get_random_colors(len(all_ids))
    color_rule = {}
    for p,c in zip(all_ids, colors):
        for p_sub in p:
            color_rule[p_sub-1] = c
    return color_rule

def review_policy_aggrid(inc_policy, err_info, conflicts, hierarchy, models):
    
    highlights = []
    
    error_ids, error_type = err_info
    
    pol_id = inc_policy['id']
    
    # if isinstance(inc_policy['policy'], list):
    inc_policy['policy'] = add_rule_ids(inc_policy['policy'])
        
    df = load_policy(inc_policy['policy'])
    # df.insert(0, 'rule', [i+1 for i in range(len(df))])
    df = df[['rule'] + [col for col in df.columns if col != 'rule']]
    
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
    gb.configure_selection('multiple', use_checkbox=True)
    
    
    if error_ids != None:
        for row in error_ids:
            highlights.append((row, error_type.capitalize()))
        if not inc_policy['solved']:
            highlight_errors(highlights, gb)
    
    if len(conflicts)>0:
        color_rules = get_conflicting_rule_ids(df, conflicts)
        highlight_rows(color_rules, gb)
    
    grid_options = gb.build()
    grid_return = AgGrid(df, gridOptions=grid_options,
        width='100%',
        allow_unsafe_jscode=True, fit_columns_on_grid_load=True, editable=True,
        # pinned_top_row_data=[pinned_row]
        key=f'incorrect_policy_{pol_id}',
        )

    selected_rows = grid_return.get('selected_rows')
    
    
    # if selected_rows is not None and not selected_rows.empty:
    #     print(selected_rows.to_dict('records'))
        
    _,add_col,delete_col = st.columns([8,2,2])
    
    add_col.button("Add rule", key=f'add_rule_btn_{pol_id}', use_container_width=True, type='secondary', icon=":material/add:", on_click=add_new_rule, args=(inc_policy,))
    
    delete_col.button("Delete rule", key=f'delete_rule_btn_{pol_id}', use_container_width=True, type='secondary', icon=":material/delete:", on_click=delete_rule, args=(selected_rows,inc_policy,), disabled=selected_rows is None)
    
    st.button("Submit", key=f'submit_inc_btn_{pol_id}', use_container_width=True, type='primary', on_click=submit_corrected_policy, args=(inc_policy, grid_return['data'], hierarchy, models,), icon=":material/send:")
    
def delete_rule(selected_rows, inc_policy):
    st.session_state.deleted_rule = True
    df = pd.DataFrame(inc_policy['policy'])
    
    has_selections = not selected_rows.empty
    if has_selections:
        selected_rows = selected_rows.to_dict('records')
        ids_to_delete = []
        for row in selected_rows:
            if isinstance(row, dict) and 'rule' in row:
                ids_to_delete.append(row['rule'])
        if ids_to_delete:
            df = df[~df['rule'].isin(ids_to_delete)].reset_index(drop=True)
    
    df = df.drop('rule', axis='columns')
    inc_policy['policy'] = df.to_dict(orient='records')
        
    
def add_new_rule(inc_policy):
    st.session_state.added_rule = True
    new_rule = pd.DataFrame({
        "decision": ['allow'],
        "subject": ['none'],
        "action": ['none'],
        "resource": ['none'],
        "purpose": ['none'],
        "condition": ['none'],
    })
    
    df = pd.concat([pd.DataFrame(inc_policy['policy']), new_rule]).drop('rule', axis='columns')
    
    inc_policy['policy'] = df.to_dict(orient='records')
    

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
    
    ALL_SOLVED = True
    
    
    if st.session_state.deleted_rule:
        
        corrected_policy = inc_policy['policy']
        st.session_state.deleted_rule = False
    elif st.session_state.added_rule:
        corrected_policy = inc_policy['policy']
        st.session_state.added_rule = False
    else:
        edited_df = edited_df.drop('rule', axis='columns')
        edited_df.columns = edited_df.columns.str.lower()
        corrected_policy = [v for _, v in edited_df.reset_index(drop=True).to_dict("index").items()]
    
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
    
    inc_policy['policy'] = corrected_policy
    inc_policy['solved'] = True
    change_page_icon('incorrect_pol_icon')
    inc_policy['show'] = False
    
    if len(st.session_state.inc_policies)>0:
    
        for incorrect_pol_object in st.session_state.inc_policies:
            
            if incorrect_pol_object['solved'] == False:
                st.session_state.inc_policy_count +=1
                ALL_SOLVED = False
        if ALL_SOLVED:
            # st.toast("All the policies are refined successfully. Go to **Access Control Policies** page to review and publish.", icon=":material/check:")
            success_refine_feedback()
            
            st.session_state.inc_policy_count = 0
    
def filter_by_nlacp(nlacp, filtered_policies):
    retriever = create_bm25_retriever(filtered_policies)
    results, scores = retriever.retrieve(bm25s.tokenize(nlacp), k=len(filtered_policies))
    mask = scores > 0
    return results[mask].tolist()
    
    
def filter(original_list, filter_container):
    
    with filter_container.popover("Filter", icon = ":material/tune:", use_container_width=True):
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
            if len(by_nlacp.split(' ')) == 1:
                if by_nlacp[-1] == 's':
                    filtered1 = filter_by_nlacp(by_nlacp, filtered_policies)
                    filtered2 = filter_by_nlacp(by_nlacp[:-1], filtered_policies)
                    
                    for p in filtered2:
                        if p not in filtered1:
                            filtered1.append(p)
                    filtered_policies = filtered1
                else:
                    filtered1 = filter_by_nlacp(by_nlacp, filtered_policies)
                    filtered2 = filter_by_nlacp(by_nlacp+'s', filtered_policies)
                    
                    for p in filtered2:
                        if p not in filtered1:
                            filtered1.append(p)
                    filtered_policies = filtered1
            else:
                filtered_policies = filter_by_nlacp(by_nlacp, filtered_policies)
            
    return filtered_policies
    
    