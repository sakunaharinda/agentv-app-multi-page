import streamlit as st
from typing import List, Literal

LOTTIE_STATUS = """
    <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
    <div style="width: 100%; display: flex; justify-content: center; left: 50% !important;">
        <lottie-player 
            src="{src}"  
            background="transparent"  
            speed="2"  
            style="width: 150; margin: 0 auto;"  
            autoplay>
        </lottie-player>
    </div>
    """

def success(message, icon = ":material/check_circle:"):
    
    st.success(body = message, icon= icon)
    

def warning(message, icon = ":material/warning:"):
    
    st.warning(body = message, icon= icon)
    
def error(message, icon = ":material/dangerous:"):
    
    st.error(body = message, icon= icon)
    

def get_rule_id_str(error_rules):
    result = ""
    for i in range(len(error_rules)):
        if len(error_rules) > 1 and i == len(error_rules)-1:
            result += f", and {error_rules[i]+1}"
        else:
            result += f", {error_rules[i]+1}"
            
    return result[2:]
        

def get_locate_warning_msg(error_type, error_rules: List):
    
    msg = f"#### :material/dangerous: Error in Access Control Policy\nRule {get_rule_id_str(error_rules)} contain{'s a/an' if len(error_rules)==1 else ''} {error_type}{'s' if len(error_rules)>1 else ''} which may restrict or permit unintended access.\nTo correct this:\n1. **Locate Error**: In the table below, go to the row {get_rule_id_str(error_rules)} corresponding to the rule {get_rule_id_str(error_rules)}.\n2. **Edit the {error_type.split(' ')[-1]}**: Double-click the cell highlighted in red under the '{error_type.split(' ')[-1]}' column in this row. A dropdown menu will appear; select the appropriate {error_type.split(' ')[-1]} from the list.\n3. **Submit the Policy**: Click the **'Submit'** button to save the corrected policy."
    
    
    return msg, [error_rules, error_type.split(' ')[-1]]

def get_locate_warning_missing_rule_msg():
    
    msg = f"#### :material/dangerous: Error: Missing Access Control Rules\nIt appears that one or more access control rules are absent from the current policy, which may lead to unintended access permissions.\nTo correct this:\n1. **Add a New Rule**: Click :material/add: Add rule to add an empty row to the table below.\n2. **Enter Rule Details**: Input the necessary policy components, such as decision, subject, action, resource, purpose, and condition, ensuring each field accurately reflects the intended access control requirement.\n3. **Submit the Policy**: Click the **'Submit'** button to save the corrected policy."
    

    return msg, [None, None]


def get_unrelated_warning():
    
    msg = f"#### :material/dangerous: Error: Unrelated Access Control Rule\nIt appears that one or more access control rules are not aligining with the organization hierarchy you uploaded.\nTo correct this:\n1. **Go to 'Generate from a Sentence'**: Go back to the 'Generate from Sentence' page.\n2. **Re-write the access control policy**: Re-write the access control requirement ensuring that it aligns with the subjects, actions, and resources of the organization\n3. **Re-generate**: Re-generate the access control policy by clicking the **Generate** button"
    
    return msg, [None, None]

@st.dialog(" ")
def success_publish_feedback(mode: Literal['single', 'multiple']='single'):
    lottie = LOTTIE_STATUS.format_map({"src": "https://lottie.host/7c49e648-7d7c-4da5-91df-1c15d62b7b46/10eseZvsTb.json"})
    _,col1,_ = st.columns([1,1,1])
    with col1:
        st.components.v1.html(lottie, width=200, height=120)
    
    if mode=='single':
        _,c1,_ = st.columns([1,6,1]) 
        
        with c1:
            st.write("# Policy Published Successfully!")
    elif mode=='multiple':
        _,c1,_ = st.columns([1,7,1]) 
        
        with c1:
            st.write("# Policies Published Successfully!")
            
@st.dialog(" ")
def success_delete_feedback():
    lottie = LOTTIE_STATUS.format_map({"src": "https://lottie.host/7c49e648-7d7c-4da5-91df-1c15d62b7b46/10eseZvsTb.json"})
    _,col1,_ = st.columns([1,1,1])
    with col1:
        st.components.v1.html(lottie, width=200, height=120)
    
    _,c1,_ = st.columns([1,7,1]) 
    
    with c1:
        st.write("# Policy Unpublished Successfully!")
        
@st.dialog(" ")
def success_refine_feedback():
    lottie = LOTTIE_STATUS.format_map({"src": "https://lottie.host/7c49e648-7d7c-4da5-91df-1c15d62b7b46/10eseZvsTb.json"})
    _,col1,_ = st.columns([1,1,1])
    with col1:
        st.components.v1.html(lottie, width=200, height=120)
    
    _,c1,_ = st.columns([1,6,1]) 
    
    with c1:
        st.write("# Policy Refinement Completed!")
        
@st.dialog(" ")
def success_generation_feedback(mode: Literal['single', 'multiple']='single'):
    lottie = LOTTIE_STATUS.format_map({"src": "https://lottie.host/7c49e648-7d7c-4da5-91df-1c15d62b7b46/10eseZvsTb.json"})
    _,col1,_ = st.columns([1,1,1])
    with col1:
        st.components.v1.html(lottie, width=200, height=120)
    
    
    if mode=='multiple':
        _,c1,_ = st.columns([1,7,1]) 
        
        with c1:
            st.write("# Policies Generated Successfully!")
            
    elif mode=='single':
        _,c1,_ = st.columns([1,6,1]) 
        
        with c1:
            st.write("# Policy Generated Successfully!")
            
@st.dialog(" ")
def failed_generation_feedback():
    lottie = LOTTIE_STATUS.format_map({"src": "https://lottie.host/b13ca72f-3e27-4524-9667-35ed76325bde/Fk03VBCLsD.json"})
    _,col1,_ = st.columns([1,1,1])
    with col1:
        st.components.v1.html(lottie, width=200, height=120)

    _,c1,_ = st.columns([1,15,1]) 
    
    with c1:
        st.write("# Incorrectly Generated Policies Found!")
    