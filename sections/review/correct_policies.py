import streamlit as st
from handlers import *
from loading import *

@st.fragment
def show_correct_policies():
    
    st.title("Correct Policies")
    
    corr_policy = st.text_input(
        label="Correctly generated policy",
        value=get_cor_nlacp(),
        disabled=True,
        help="Natural Language Access Control Policies corresponding to correct access control policies.",
    )
    _, pclc, nclc, _ = st.columns([5, 2, 2, 5])
    prev_button_correct = pclc.button(
        label="Previous",
        key="cor_prev",
        on_click=cor_policy_nav_prev,
        disabled=st.session_state.cor_count <= 0,
        use_container_width=True,
    )
    next_button_correct = nclc.button(
        label="Next",
        key="cor_next",
        on_click=cor_policy_nav_next,
        disabled=st.session_state.cor_count
        == len(st.session_state.corrected_policies) - 1,
        use_container_width=True,
    )

    cdf = load_policy(get_cor_policy())

    with st.container(border=False, height=350):
        if len(st.session_state.corrected_policies)>0:
            corr_df = st.dataframe(cdf, use_container_width=True, key="correct_policies")


    with st.container(border=False, height=100):
        out_col1, out_col2, out_col3 = st.columns([1, 1, 1])
        # json_btn = viz_col1.button('Export as JSON', use_container_width=True, key='json_btn')
        out_col3.download_button(
            label="Export as JSON",
            file_name="policies.json",
            mime="application/json",
            data=load_json_output(st.session_state.corrected_policies),
            use_container_width=True,
            disabled=len(st.session_state.corrected_policies) < 1,
        )
        try_single = out_col2.button(
            "Test Policy",
            type="secondary",
            use_container_width=True,
            key="try_single",
            disabled=len(st.session_state.corrected_policies) < 1,
        )
        
        try_overall = out_col1.button(
            "Test System",
            type="primary",
            use_container_width=True,
            key="try_overall",
            disabled=len(st.session_state.corrected_policies) < 1,
        )
        

show_correct_policies()