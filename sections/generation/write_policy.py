import streamlit as st
from code_editor import code_editor
import xml.etree.ElementTree as ET
from ac_engine_service import AccessControlEngine
from models.ac_engine_dto import XACMLPolicyRecord
from utils import change_page_icon
from sections.generation.generation_utils import write_feedback
from models.pages import PAGE

@st.fragment
def write_xacml(ac_engine: AccessControlEngine):
    
    st.session_state.current_page = PAGE.WRITE_XACML
    
    st.markdown("""
        <style>
            /* Target the container with the specific key */
            [data-testid="stVerticalBlock"] .st-key-xacml_container {
                position: fixed !important;
                bottom: 10px !important;
            }
            
            /* Add padding at the bottom of the page to prevent content from being hidden */
            section.main {
                padding-bottom: 100px !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.title("Write in XACML")
    
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
    
    
    code_editor_response = code_editor(
        code=f"""<Policy xmlns="urn:oasis:names:tc:xacml:3.0:core:schema:wd-17" PolicyId="{st.session_state.xacml_uuid}" RuleCombiningAlgId="urn:oasis:names:tc:xacml:1.0:rule-combining-algorithm:first-applicable" Version="1.0">
    <Description>Add a relevant description here</Description>
    <Target/>
    <Rule RuleId="rule1" Effect="Permit">
        <Description>Rule1</Description>
        <Target/>
    </Rule>
</Policy>""",
        lang="xml",
        height="465px",
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
    
    xacml_container = st.container(key='xacml_container')
    with xacml_container:
        feedback_container = st.container(border=False, height=55)
        feedback_container.warning("Policies manually created with XACML will not be appeared in the **Policy Visualization**, but can be tested in the **Policy Testing** stage.", icon=":material/warning:")
        
        submit = st.button(
                "Publish Policy to Database",
                type="primary",
                use_container_width=True,
                key="publish_cur",
                disabled=code_editor_response["text"] == "",
            )
    
    if submit:
        change_page_icon("write_xacml_icon")
        policy_xml = code_editor_response["text"]
        try:
            policy_root = ET.fromstring(policy_xml)
            policy_id = policy_root.get('PolicyId')
            status = ac_engine.create_policy_xacml(
                XACMLPolicyRecord(
                    id=policy_id,
                    policy=policy_xml
                )
            )
            write_feedback(status)
        except Exception as e:
            print(e)
            feedback_container.error(body=str(e), icon=':material/dangerous:')
    

ac_engine = AccessControlEngine()
write_xacml(ac_engine)