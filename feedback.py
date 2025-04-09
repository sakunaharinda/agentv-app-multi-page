import streamlit as st
from typing import List

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
    
    msg = f"#### :material/dangerous: Error in Access Control Policy\nRule {get_rule_id_str(error_rules)} contain{'s a/an' if len(error_rules)==1 else ''} {error_type}{'s' if len(error_rules)>1 else ''} which may restrict or permit unintended access.\nTo correct this:\n1. **Locate Rule 2**: In the table below, go to the row {get_rule_id_str(error_rules)} corresponding to the rule {get_rule_id_str(error_rules)}.\n2. **Edit the {error_type.split(' ')[-1]}**: Double-click the cell under the '{error_type.split(' ')[-1]}' column in this row. A dropdown menu will appear; select the appropriate {error_type.split(' ')[-1]} from the list.\n3. **Submit the Policy**: Click the **'Submit'** button to save the corrected policy."
    
    
    return msg

# f"**The rule {get_rule_id_str(error_rules)} of the access control policy contain{'s a/an' if len(error_rules)==1 else ''} {error_type}{'s' if len(error_rules)>1 else ''}.** To correct the incorrect rule, \n1. Go to the row {get_rule_id_str(error_rules)} of the table below.\n2. Double click on the cell corresponding to the **{error_type.split(' ')[-1]}** and choose the correct value.\n3. Make sure that no other errors are present in the updated policy.\n4. Click **Submit** to submit the corrected policy."

def get_locate_warning_missing_rule_msg():
    
    msg = f"#### :material/dangerous: Error: Missing Access Control Rules\nIt appears that one or more access control rules are absent from the current policy, which may lead to unintended access permissions.\nTo correct this:\n1. **Add a New Rule**: In the table below, locate the last row and click on an empty cell within this row to initiate the addition of a new rule.\n2. **Enter Rule Details**: Input the necessary policy components, such as subject, action, resource, purpose, and condition, ensuring each field accurately reflects the intended access control requirement.\n3. **Submit the Policy**: Click the **'Submit'** button to save the corrected policy."
    
    # return f"**One or more access control rules are missing in the generated policy.**\n1. Click on a cell in the last row of the table below.\n2. Add the missing rule with the correct policy components.\n3. Make sure that no other errors are present in the updated policy.\n4. Click ***Submit*** to submit the corrected policy."
    
    return msg