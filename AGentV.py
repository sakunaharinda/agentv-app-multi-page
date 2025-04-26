import streamlit as st
from init_ui import init
import torch
from dotenv import load_dotenv

torch.classes.__path__ = []
# _ = load_dotenv()
init()


st.switch_page("pages/login.py")