
import streamlit as st

from st_pages import add_page_title, get_nav_from_toml

st.set_page_config(layout="wide")

st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"]::before {
                content: "AGentV";
                margin-top: 20px;
                font-size: 30px;
                justify-content: center;
                display: flex;
                top: 10px;
                font-weight: bold;
            }
            [data-testid="stSidebarNav"] ul {
                padding-top: 100px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100%;
            }
            [data-testid="stSidebarNav"] ul li {
                margin-bottom: 10px; /* Adjust the value as needed */
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

starting_page = st.Page("get_started.py", title="Getting Started", icon="")
inputs_page = st.Page("inputs.py", title="Provide Inputs", icon="")
correct_pol_page = st.Page("correct_policies.py", title="Correct Policies", icon="")
incorrect_pol_page = st.Page("incorrect_policies.py", title="Incorrect Policies", icon="")


pg = st.navigation(
    
    [starting_page, inputs_page, correct_pol_page, incorrect_pol_page]
    
)


pg.run()