import streamlit as st
from init_ui import init
import torch
from dotenv import load_dotenv

torch.classes.__path__ = []
_ = load_dotenv()
init()

st.markdown(
        f"""
        <style>
            
            
            [data-testid="stSidebarNav"] ul li {{
                width: 100%;
                text-align: center;
            }}

            [data-testid="stSidebarNav"] ul li {{
                margin-bottom: 1px; /* Adjust the value as needed */
            }}
            
            
        </style>
        """,
        unsafe_allow_html=True,
    )

# standard_menu()
# start()

st.switch_page("pages/get_started.py")