import streamlit as st
from feedback import warning

def show_summary(status_container):
    
    if 'results_document' in st.session_state:
        
        assert st.session_state.results_document['final_verification'].count(11) == len(st.session_state.results_document['final_correct_policies']), 'There is a mismatch between correct policies and correctly verified policies'
    
        summary = f"No. of sentences: {len(st.session_state.results_document['sentences'])}\nNo. of access requirement: {len(st.session_state.results_document['generated_nlacps'])}\nCorrectly generated policies: {st.session_state.results_document['final_verification'].count(11)}\nIncorrectly generated policies: {len(st.session_state.results_document['generated_nlacps']) - st.session_state.results_document['final_verification'].count(11)}"
        
        status_container.text_area("Summary", summary, help=f"A summary of the completed access control policy generation process, outlining the total number of sentences found in the input document, the number of access control requirement found among the sentences, the number of correctly translated access control requirements into structured access control policies (See **Correct Policies** page), and the number of failed translations (See **Incorrect Policies** page)",disabled=True, height=150)
        
@st.dialog("Generation without Organization Hierarchy")
def generating_wo_hierarchy():
    
    st.write("You are attempting to generate access control policies without an organization hierarchy. Are you sure you want to continue with the policy generation?")
    warning("The generated policies can contain policy components (i.e., subject, action, etc.) that may not align with organizational context, which is supposed to be provided by the '**Organization Hierarchy**'")
    
    gencol1, gencol2 = st.columns([1,1])
    
    continue_gen = gencol2.button("Continue Generation", key="gen_contd", help="Continue with the policy generation without organization hierarchy", type='secondary', use_container_width=True)
    
    upload_hierarchy = gencol1.button("Upload Hierarchy", key="upload_h", help="Upload the hierarchy", type='primary', use_container_width=True)
    
    if continue_gen:
        st.session_state.is_generating = True
        st.session_state.do_align = False
        st.session_state.generate_wo_context = True
        st.rerun()
        
    elif upload_hierarchy:
        st.session_state.is_generating = False
        st.switch_page('sections/get_started.py')
    
    
@st.dialog("Review Incorrectly Generated Policies")
def review_incorrects(incorrects):
    
    st.write(f"You have {incorrects} incorrectly generated polic{'y' if incorrects==1 else 'ies'} to review. Do you want review {'it' if incorrects==1 else 'them'} now?")
    warning("Applying the incorrectly generated policies to the policy database without reviewing may result in access control failure that could lead to data breaches.")
    
    gencol1, gencol2 = st.columns([1,1])
    
    wait = gencol2.button("No", key="review_later", help="Review the incorrectly generated policies later", type='secondary', use_container_width=True)
    
    review = gencol1.button("Yes", key="review_now", help="Review the incorrectly generated policies.", type='primary', use_container_width=True)
    
    if review:
        st.switch_page('sections/review/incorrect_policies.py')
        
    elif wait:
        st.rerun()
        
    st.session_state.reviewed = True
    