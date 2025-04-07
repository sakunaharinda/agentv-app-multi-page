import streamlit as st
from streamlit_float import *

# Float feature initialization
float_init()

# Create footer container and add content
footer_container = st.container()
with footer_container:
    st.markdown("Copyright &copy; 2023 Your Name - All Rights Reserved.")

# Float the footer container and provide CSS to target it with
footer_container.float("bottom: 10px;")