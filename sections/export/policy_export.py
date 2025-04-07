import os
import streamlit as st
from streamlit_float import *
from loading import load_json_output
from ac_engine_service import AccessControlEngine
from zipfile import ZipFile, ZIP_DEFLATED
import pathlib
from utils import change_page_icon

def save_policies(ac_engine: AccessControlEngine, save_path = 'downloads'):
    
    float_init()
    
    def download_xacml():
        create_status = ac_engine.create_multiple_policies(st.session_state.corrected_policies)
        if create_status != 200:
            
            st.error(f"An error occured with the HTTP status code {create_status} while trying to publish the policies to the policy database.", icon='🚨')
            
        else:
            
            get_status, xacml_policies = ac_engine.get_all_policies()
            
            if get_status == 200:
                
                for i, xacml_policy in enumerate(xacml_policies):
                    id = xacml_policy.id
                    policy = xacml_policy.policy
                    
                    if not os.path.exists(save_path + "/raw"):
                        os.makedirs(save_path + "/raw")
                        
                        print(f"{save_path} folder is created!")
                        
                    with open(f'{save_path}/raw/{id}.xml', 'w') as f:
                        f.write(policy)
                        
                folder_to_zip = pathlib.Path(save_path + "/raw")
                with ZipFile(f'{save_path}/xacml.zip', 'w', ZIP_DEFLATED) as zip:
                    for file in folder_to_zip.iterdir():
                        zip.write(file, arcname=file.name)
        
    download_xacml()
    st.markdown(
        f"""
        <style>
            .st-key-save_json button,
            .st-key-save_xacml button {{
                height: 100px;
                font-size: 100px !important;
                border-radius: 2rem;
                box-shadow: rgba(0, 0, 0, 0.16) 0px 4px 16px;
            }}
            
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.title("Save Policies")
    
    btn_container = st.container()
    
    with btn_container:
        
        _,col1, col2,_ = st.columns([0.15, 1,1, 0.15])
        save_json = col1.download_button(
                label="Export as JSON",
                file_name="policies.json",
                mime="application/json",
                data=load_json_output(st.session_state.corrected_policies),
                use_container_width=True,
                disabled=len(st.session_state.corrected_policies) < 1,
                icon=':material/data_object:',
                key='save_json',
                on_click=change_page_icon,
                args=('save_icon',)
            )
        
        with open(f'{save_path}/xacml.zip', 'rb') as f:
            save_xacml = col2.download_button(
                label=f"Save as XACML", 
                key='save_xacml', 
                type='secondary', 
                icon=":material/code:", 
                use_container_width=True, 
                disabled= (len(st.session_state.corrected_policies) == 0),
                file_name="xacml.zip",
                data=f,
                on_click=change_page_icon,
                args=('save_icon',)
                )
            
    
    
    btn_container.float("top: 50%;")
    

ac_engine = AccessControlEngine()
save_policies(ac_engine)
    