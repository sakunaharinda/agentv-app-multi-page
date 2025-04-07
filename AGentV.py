
import streamlit as st

from init_ui import init
import torch
from hierarchy_visualizer import visualize_hierarchy_dialog

torch.classes.__path__ = []
print("rerun")

st.set_page_config(layout="wide")

selected_color = "#4CAF50"

st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"]::before {{
                content: "AGentV";
                margin-top: 10px;
                font-size: 30px;
                justify-content: center;
                display: flex;
                top: 10px;
                font-weight: bold;
            }}
            [data-testid="stSidebarNav"] ul {{
                padding-top: 20px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100%;
            }}
            [data-testid="stSidebarNav"] ul li {{
                width: 100%;
                text-align: center;
            }}

            
            [data-testid="stSidebarNav"] ul li {{
                margin-bottom: 2px; /* Adjust the value as needed */
            }}
            
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    
init()


starting_page = st.Page("sections/get_started.py", title=st.session_state.start_title, icon=st.session_state.start_icon, default=True)

generate_doc = st.Page("sections/generation/generate_document.py", title=st.session_state.generate_doc_title, icon=st.session_state.gen_doc_icon)
generate_single = st.Page("sections/generation/generate_individual.py", title=st.session_state.generate_single_title, icon=st.session_state.gen_sent_icon)
write_xacml = st.Page("sections/generation/write_policy.py", title=st.session_state.write_xacml_title, icon=st.session_state.write_xacml_icon)

correct_pol_page = st.Page("sections/review/correct_policies.py", title=st.session_state.cor_policies_title, icon=st.session_state.correct_pol_icon)
incorrect_pol_page = st.Page("sections/review/incorrect_policies.py", title=st.session_state.inc_policies_title, icon=st.session_state.incorrect_pol_icon)

policy_viz_page = st.Page("sections/testing/policy_visualization.py", title=st.session_state.policy_viz_title, icon=st.session_state.viz_icon)
policy_test_page = st.Page("sections/testing/test_policies.py", title=st.session_state.policy_test_title, icon=st.session_state.test_icon)

policy_export_page = st.Page("sections/export/policy_export.py", title=st.session_state.policy_export_title, icon=st.session_state.save_icon)

if st.session_state.started:
    
    pages = {
        "": [starting_page],
        "Policy Generation": [generate_doc, generate_single, write_xacml],
        "Policy Review": [incorrect_pol_page, correct_pol_page],
        "Policy Testing": [policy_viz_page, policy_test_page],
        "Policy Exporting": [policy_export_page]
    }
    
    h_btn = st.sidebar.button("Organization Hierarchy", use_container_width=True, key='org_hierarchy', type='primary', disabled=(not st.session_state.hierarchies))
    if h_btn:
        visualize_hierarchy_dialog()
    
else:
    
    pages = {
        "": [starting_page]
    }

pg = st.navigation(pages)


pg.run()