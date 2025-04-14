import pandas as pd
from typing import List
import streamlit as st
import numpy as np
from models.ac_engine_dto import JSONPolicyRecord
from utils import change_page_icon
from models.pages import PAGE
from menus import standard_menu

@st.cache_data(show_spinner = False)
def create_access_matrix(correct_policies: List[JSONPolicyRecord]):
    
    st.session_state.current_page = PAGE.VIZ_POLICY
    
    data = []
    
    if len(correct_policies) > 0:
    
        for nlacp_pol in correct_policies:
            
            policy_record = nlacp_pol.to_dict()
            
            nlacp = nlacp_pol.policyDescription
            policy = policy_record['policy']
            
            data.extend(policy)
            
        df = pd.DataFrame(data).drop_duplicates()

        # Get unique subjects and resources
        subjects = sorted(df['subject'].unique())
        resources = sorted(df['resource'].unique())

        # Create an empty access matrix
        access_matrix = pd.DataFrame(index=subjects, columns=resources)

        # Populate the access matrix
        for _, row in df.iterrows():
            decision, subject, action, resource = row['decision'], row['subject'], row['action'], row['resource']
            
            if decision == 'allow':
                entry = f"✅ {action}"
            else:
                entry = f"🚫 {action}"
            
            # If cell is empty, initialize with a list; otherwise, append new entry
            
            is_cell_empty = pd.isna(access_matrix.at[subject, resource])
            
            if (type(is_cell_empty) == np.ndarray):
                is_cell_empty = is_cell_empty.all()
            
            if is_cell_empty:
                access_matrix.at[subject, resource] = [entry]
            else:
                if entry not in access_matrix.at[subject, resource]:
                    access_matrix.at[subject, resource].append(entry)

        # Convert lists to readable string format
        access_matrix = access_matrix.applymap(lambda x: '\n'.join(x) if isinstance(x, list) else '')
        
        access_matrix.to_csv("logs/access_matrix.csv")
        
        return access_matrix
        

standard_menu()
_, viz_col, _ = st.columns([1,1,1])
        

st.title("Policy Visualization")
change_page_icon('viz_icon')
if len(st.session_state.corrected_policies)>0:
    with st.container(height=400, border=False):

        st.dataframe(create_access_matrix(st.session_state.corrected_policies), use_container_width=True, key="access_matrix")
        
    _,leg_col1,leg_col2,_ = st.columns([4,2,2,4])

    leg_col1.markdown("#### ✅ :green[Allowed]")
    leg_col2.markdown("#### 🚫 :red[Denied]")