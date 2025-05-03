import os
import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import LoginError
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


@st.cache_data(show_spinner=False)
def load_auth_config(auth_file = 'auth_config.yaml'):

    uri = os.environ['MONGODB_URI']

    client = MongoClient(uri, server_api=ServerApi('1'))
    agentv_db = client['agentv']
    users = agentv_db['user'].find()
    usernames = {}
    
    for u in users:
        usernames.update(u['user'])
    
    with open(f'.streamlit/{auth_file}') as file:
        config = yaml.load(file, Loader=SafeLoader)
        
    config['credentials'] = {}
    config['credentials']['usernames'] = usernames
    return config

def login():
    
    if 'authentication_status' in st.session_state:
        del st.session_state['authentication_status']

    config = load_auth_config('auth_config.yaml')
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    st.title(f"Welcome to AGentV")
    
    try:
        authenticator.login(location='main')
    except LoginError as e:
        st.error(e)
        
    if st.session_state["authentication_status"]:
        
        # authenticator.logout()
        
        st.session_state.authenticator = authenticator
        st.switch_page("pages/get_started.py")
        

    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
        return False
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')
        return False
    

login()