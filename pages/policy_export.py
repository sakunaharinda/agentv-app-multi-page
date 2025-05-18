import os
import streamlit as st
from streamlit_float import *
from loading import load_json_output
from ac_engine_service import AccessControlEngine
from zipfile import ZipFile, ZIP_DEFLATED
import pathlib
from utils import change_page_icon, toast_download_sucess
from models.pages import PAGE
from menus import standard_menu
import io

@st.cache_data
def add_to_zip_buffer(xacml_policies):
    
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w", ZIP_DEFLATED) as zip_file:
        for xacml_policy in xacml_policies:
            
            id = xacml_policy.id
            policy = xacml_policy.policy
            
            filename = f"{id}.xml"
            zip_file.writestr(filename, policy)
    zip_buffer.seek(0)
    
    return zip_buffer

@st.dialog("Download Policies")
def policy_select(options, mode, xacml_policies=None):

    selected_policies = st.multiselect("Select the policy/policies you want to download.", options=options, placeholder="Select the policy/policies by the Policy ID", key="select_save_pols")
    
    if "All" in selected_policies:
        selected_policies = [policy.policyId for policy in st.session_state.pdp_policies]
        
    with st.expander(label="Cannot find the policy you are looking for?"):
        
        st.write("This is because the policy you are looking for is not published to the policy database.")
        st.info("Please go to the **Access Control Policies** page, :material/database_upload: Publish the policy you need to download and come back.")
    
    if mode == 'json':
        
        pol_to_download = [policy.to_json_record() for policy in st.session_state.pdp_policies if policy.policyId in selected_policies]
        
        save_json = st.download_button(
                label="Download as JSON",
                file_name="policies.json",
                mime="application/json",
                data=load_json_output(pol_to_download),
                use_container_width=True,
                disabled=len(selected_policies) < 1,
                icon=':material/data_object:',
                key='save_as_json',
                on_click=change_page_icon,
                args=('save_icon',)
            )
        
    elif mode == 'xacml':
        
        pol_to_download = [xacml_policy for xacml_policy in xacml_policies if xacml_policy.id in selected_policies]
        
        buffer = add_to_zip_buffer(pol_to_download)
        
        save_xacml = st.download_button(
                label=f"Download as XACML", 
                key='save_as_xacml', 
                type='secondary', 
                icon=":material/code:", 
                use_container_width=True, 
                disabled= (len(pol_to_download) == 0),
                file_name="xacml.zip",
                data=buffer,
                on_click=change_page_icon,
                args=('save_icon',),
                mime='application/zip'
                )
        
            
def download_xacml(ac_engine, save_path, policy_ids=None):
        # create_status = ac_engine.create_multiple_policies(st.session_state.corrected_policies)
        # if create_status != 200:
            
        #     st.error(f"An error occured with the HTTP status code {create_status} while trying to publish the policies to the policy database.", icon='🚨')
            
        # else:
            
        get_status, xacml_policies = ac_engine.get_all_policies()
        
        if get_status == 200:
            
            if not os.path.exists(save_path + "/raw"):
                os.makedirs(save_path + "/raw")
                
                print(f"{save_path} folder is created!")
            
            for i, xacml_policy in enumerate(xacml_policies):
                id = xacml_policy.id
                policy = xacml_policy.policy
                
                if policy_ids!=None and id in policy_ids:
                    with open(f'{save_path}/raw/{id}.xml', 'w') as f:
                        f.write(policy)
                elif policy_ids==None:
                    with open(f'{save_path}/raw/{id}.xml', 'w') as f:
                        f.write(policy)
                    
            folder_to_zip = pathlib.Path(save_path + "/raw")
            with ZipFile(f'{save_path}/xacml.zip', 'w', ZIP_DEFLATED) as zip:
                for file in folder_to_zip.iterdir():
                    zip.write(file, arcname=file.name)
     
        

def save_policies(ac_engine: AccessControlEngine, save_path = 'downloads'):
    
    st.session_state.current_page = PAGE.SAVE_PAGE
    
    float_init()
    
    
    options = [policy.policyId for policy in st.session_state.pdp_policies]
    get_status, xacml_policies = ac_engine.get_all_policies()
    
    options = ['All'] + options
    
    
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
    
    st.title("Download Policies")
    
    btn_container = st.container()
    
    with btn_container:
        
        _,col1, col2,_ = st.columns([0.15, 1,1, 0.15])
        save_json = col1.button(
                label="Save as JSON",
                type='secondary',
                use_container_width=True,
                disabled=len(st.session_state.pdp_policies) == 0,
                icon=':material/data_object:',
                key='save_json',
                on_click=change_page_icon,
                args=('save_icon',)
            )
        
        save_xacml = col2.button(
            label=f"Save as XACML", 
            key='save_xacml', 
            type='secondary', 
            icon=":material/code:", 
            use_container_width=True, 
            disabled= (len(st.session_state.pdp_policies) == 0),
            on_click=change_page_icon,
            args=('save_icon',)
            )
        
        if save_json:
            
            policy_select(options, 'json')
        
        elif save_xacml:
            
            policy_select(options, 'xacml', xacml_policies)
            
    
    btn_container.float("top: 50%;")
    
standard_menu()
ac_engine = AccessControlEngine()

save_policies(ac_engine)
    