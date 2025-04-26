from loading import load_auth_config
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)


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