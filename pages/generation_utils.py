import streamlit as st
from feedback import warning

import plotly.graph_objects as go
from models.ac_engine_dto import WrittenPolicy
from feedback import success_generation_feedback, failed_generation_feedback

def get_updated_description(policy: WrittenPolicy):
    
    if not policy.is_incorrect:
        
        new_description = policy.sentence + " :green-badge[:material/check: Generated]"
    else:
        new_description = policy.sentence + " :red-badge[:material/error: Attention Needed]"
        
    # if not policy.with_context:
        
    #     new_description+= " :red-badge[:material/family_history: Outside context]"
        
    return f"**{new_description}**"

def show_bar_chart(container):
    
    value1=st.session_state.results_document['final_verification'].count(11)
    value2=len(st.session_state.results_document['generated_nlacps']) - st.session_state.results_document['final_verification'].count(11)
    color1="#177233"
    color2="#F84948"
    
    # Calculate proportions
    total = value1 + value2
    prop1 = (value1 / total) * 100
    prop2 = (value2 / total) * 100
    
    # Create the horizontal bar plot
    fig = go.Figure()
    
    # Add both segments to a single bar
    fig.add_trace(go.Bar(
        y=[''],
        x=[prop1],
        name=f'Correct Policies: {value1} ({prop1:.1f}%)',
        orientation='h',
        marker=dict(color=color1),
        text=f'{prop1:.1f}%',
        textposition='inside',
        insidetextanchor='middle'
    ))
    
    fig.add_trace(go.Bar(
        y=[''],
        x=[prop2],
        name=f'Incorrect Policies: {value2} ({prop2:.1f}%)',
        orientation='h',
        marker=dict(color=color2),
        text=f'{prop2:.1f}%',
        textposition='inside',
        insidetextanchor='middle'
    ))
    
    # Update layout for a stacked bar chart
    fig.update_layout(
        barmode='stack',
        height=130,
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        xaxis=dict(title='Percentage (%)', range=[0, 100])
    )
        
    container.plotly_chart(fig, use_container_width=True)

def show_summary(status_container):
        
    assert st.session_state.results_document['final_verification'].count(11) == len(st.session_state.results_document['final_correct_policies']), 'There is a mismatch between correct policies and correctly verified policies'

    summary = f"Sentences in uploaded document: {len(st.session_state.results_document['sentences'])}\nAccess control requirements identified: {len(st.session_state.results_document['generated_nlacps'])}\nCorrectly generated policies: {st.session_state.results_document['final_verification'].count(11)}\nIncorrectly generated policies: {len(st.session_state.results_document['generated_nlacps']) - st.session_state.results_document['final_verification'].count(11)}"
    
    status_container.text_area("Summary", summary, help=f"A summary of the completed access control policy generation process, outlining the total number of sentences found in the input document, the number of access control requirement found among the sentences, the number of correctly translated access control requirements into structured access control policies (See **Correct Policies** page), and the number of failed translations (See **Incorrect Policies** page)",disabled=False, height=112)
        
        
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
        st.switch_page('pages/get_started.py')
    

def on_click_review():
    st.switch_page('pages/incorrect_policies.py')
    
def on_click_publish():
    st.switch_page('pages/correct_policies.py')

@st.dialog("Review Incorrectly Generated Policies")
def review_incorrects(incorrects):
    
    st.write(f"You have {incorrects} incorrectly generated polic{'y' if incorrects==1 else 'ies'} to review. Do you want review {'it' if incorrects==1 else 'them'} now?")
    st.warning("### :material/warning: Caution\nPublishing incorrectly generated policies to the authroization system without reviewing and correcting them may result in misconfigured access control. This could lead to unauthorized access or data breaches.\n\n**Always ensure that policies are thoroughly reviewed and accurate before publishing them to the Policy Database.**")
    
    gencol1, gencol2 = st.columns([1,1])
    
    wait = gencol2.button("No", key="review_later", help="Review the incorrectly generated policies later", type='secondary', use_container_width=True)
    
    review = gencol1.button("Yes", key="review_now", help="Review the incorrectly generated policies.", type='primary', use_container_width=True)
    
    if review:
        st.switch_page('pages/incorrect_policies.py')
        
    elif wait:
        st.rerun()
        
    st.session_state.reviewed = True
    
def review_incorrects_notification(incorrects):
    
    st.toast(f"You have incorrectly generated policies. Go to **Incorrect Access Control Policies** page to review.",icon=":material/warning:")
        
    st.session_state.reviewed = True
    

def review_individual(written_p: WrittenPolicy):
    print(written_p.is_incorrect)
    review_container = st.container()
    if written_p.is_incorrect:
        review_container.error("The generated policy is found incorrect. Do you want to review it?", icon=":material/dangerous:")
        if review_container.button("Review", key=f'review_btn_{written_p.id}', use_container_width=True, type='primary', icon=":material/rate_review:"):
            on_click_review()
            
        if not written_p.is_reviewed:
            # st.toast(f"You have an incorrectly generated policy. Go to **Incorrect Access Control Policies** page to review.",icon=":material/warning:")
            failed_generation_feedback()
            written_p.is_reviewed = True
        
    else:
        review_container.info("Do you want to review and publish the generated policy to the policy database?", icon=":material/rate_review:")
        if review_container.button("Review", key=f'review_btn_{written_p.id}', use_container_width=True, type='primary', icon=":material/rate_review:"):
            on_click_publish()
            
        if not written_p.is_reviewed:
            # st.toast(f"Policy is generated successfully. Go to **Access Control Policies** page to review and publish.",icon=":material/check:")
            success_generation_feedback(mode='single')
            written_p.is_reviewed = True
        
    return review_container
    
    
@st.dialog(title="Publish to Policy Database")
def write_feedback(status_code):
    
    if status_code == 200:
        
        st.success("The policy is published to the policy database successfully!", icon=':material/check_circle:')
        
    else:
        
        st.error(f"An error occured with the HTTP status code {status_code} while trying to publish the policy.", icon=':material/dangerous:')
        
    ok = st.button("OK", key='ok_publish_xacml', use_container_width=True, type='primary')
    
    if ok:
        st.rerun()
    