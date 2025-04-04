import streamlit as st

def success(message, icon = "✅"):
    
    st.success(body = message, icon= icon)
    

def warning(message, icon = "⚠️"):
    
    st.warning(body = message, icon= icon)
    
def error(message, icon = "🚨"):
    
    st.error(body = message, icon= icon)