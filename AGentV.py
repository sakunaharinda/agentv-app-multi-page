
import streamlit as st

from init_ui import init
import torch

torch.classes.__path__ = []

st.set_page_config(layout="wide")

selected_color = "#4CAF50"

st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"]::before {{
                content: "AGentV";
                margin-top: 20px;
                font-size: 30px;
                justify-content: center;
                display: flex;
                top: 10px;
                font-weight: bold;
            }}
            [data-testid="stSidebarNav"] ul {{
                padding-top: 100px;
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
                margin-bottom: 10px; /* Adjust the value as needed */
            }}
            
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    
init()

starting_page = st.Page("sections/get_started.py", title=st.session_state.start_title, icon=st.session_state.start_icon, default=True)
generate_doc = st.Page("sections/generation/generate_document.py", title=st.session_state.generate_doc_title, icon="")
generate_single = st.Page("sections/generation/generate_individual.py", title=st.session_state.generate_single_title, icon="")
correct_pol_page = st.Page("sections/correct_policies.py", title=st.session_state.cor_policies_title, icon="")
incorrect_pol_page = st.Page("sections/incorrect_policies.py", title=st.session_state.inc_policies_title, icon="")


pg = st.navigation(
    
    {
        "": [starting_page],
        "Generate": [generate_doc, generate_single],
        "Review": [correct_pol_page, incorrect_pol_page]
    }
    
)


pg.run()