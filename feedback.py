import streamlit as st
from typing import List

def success(message, icon = "✅"):
    
    st.success(body = message, icon= icon)
    

def warning(message, icon = "⚠️"):
    
    st.warning(body = message, icon= icon)
    
def error(message, icon = "🚨"):
    
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
    
    
    return f"**The rule {get_rule_id_str(error_rules)} of the access control policy contain{'s a/an' if len(error_rules)==1 else ''} {error_type}{'s' if len(error_rules)>1 else ''}.** To correct the incorrect rule, \n1. Go to the row {get_rule_id_str(error_rules)} of the table below.\n2. Double click on the cell corresponding to the **{error_type.split(' ')[-1]}** and choose the correct value.\n3. Make sure that no other errors are present in the updated policy.\n4. Click **Submit** to submit the corrected policy."

def get_locate_warning_missing_rule_msg():
    return f"**One or more access control rules are missing in the generated policy.**\n1. Click on a cell in the last row of the table below.\n2. Add the missing rule with the correct policy components.\n3. Make sure that no other errors are present in the updated policy.\n4. Click ***Submit*** to submit the corrected policy."