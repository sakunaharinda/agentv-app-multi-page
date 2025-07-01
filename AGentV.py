import streamlit as st
from init_ui import init
import torch

torch.classes.__path__ = []

init()


st.switch_page("pages/get_started.py")