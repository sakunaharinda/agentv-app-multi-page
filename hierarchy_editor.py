import streamlit as st
from code_editor import code_editor
import yaml

# @st.dialog(title="Edit the Hierarchy.", width='large')
def edit_hierarchy(entity_hierarchy):
    
    css_string = '''
        background-color: #bee1e5;

        body > #root .ace-streamlit-dark~& {
        background-color: #262830;
        }

        .ace-streamlit-dark~& span {
        color: #fff;
        opacity: 0.6;
        }

        span {
        color: #000;
        opacity: 0.5;
        }

        .code_editor-info.message {
        width: inherit;
        margin-right: 75px;
        order: 2;
        text-align: center;
        opacity: 0;
        transition: opacity 0.7s ease-out;
        }

        .code_editor-info.message.show {
        opacity: 0.6;
        }

        .ace-streamlit-dark~& .code_editor-info.message.show {
        opacity: 0.5;
        }
        '''
    
    init_code = yaml.dump(entity_hierarchy, default_flow_style=False)
    
    code_editor_response = code_editor(
        code=init_code,
        lang="yaml",
        focus=False,
        allow_reset=True,
        options={"showLineNumbers": True},
        buttons=[
            {
                "name": "Save",
                "feather": "Save",
                "hasText": True,
                "commands": ["save-state", ["response", "saved"]],
                "response": "saved",
                "alwaysOn": True,
                "style": {"bottom": "0.46rem", "right": "0.4rem"}
            }
        ],
    )
    
    print(code_editor_response)
    
#     xacml_container = st.container(key='xacml_container')
#     with xacml_container:
#         feedback_container = st.container(border=False, height=55)
#         feedback_container.warning("Policies manually created with XACML will not be appeared in the **Policy Visualization**, but can be tested in the **Policy Testing** stage.", icon=":material/warning:")
        
#         submit = st.button(
#                 "Publish",
#                 type="primary",
#                 use_container_width=True,
#                 key="publish_cur",
#                 disabled=code_editor_response["text"] == "",
#                 help="Publish the written XACML policy to the policy database",
#                 icon=":material/database_upload:"
#             )
    
#     if submit:
#         change_page_icon("write_xacml_icon")
#         policy_xml = code_editor_response["text"]
#         try:
#             policy_root = ET.fromstring(policy_xml)
#             policy_id = policy_root.get('PolicyId')
#             status = ac_engine.create_policy_xacml(
#                 XACMLPolicyRecord(
#                     id=policy_id,
#                     policy=policy_xml
#                 )
#             )
#             write_feedback(status)
#         except Exception as e:
#             print(e)
#             feedback_container.error(body=str(e), icon=':material/dangerous:')
    
# standard_menu()

# ac_engine = AccessControlEngine()
# write_xacml(ac_engine)