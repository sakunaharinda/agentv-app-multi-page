import streamlit as st
from utils import change_page_icon, store_value
from feedback import *
from streamlit_float import *
from models.pages import PAGE
from menus import standard_menu
from hierarchy_visualizer import visualize_hierarchy_dialog

# @st.fragment
def start():
    st.session_state.current_page = PAGE.START

    float_init()

    st.markdown(
            f"""
            <style>
                .st-key-gen_doc button,
                .st-key-cor_pol button,
                .st-key-inc_pol button,
                .st-key-test_pol button,
                .st-key-save_pol button,
                .st-key-write_xacml button,
                .st-key-gen_sent button {{
                    height: 100px;
                    font-size: 100px !important;
                    border-radius: 2rem;
                    box-shadow: rgba(0, 0, 0, 0.16) 0px 4px 16px;
                }}
                
            </style>
            """,
            unsafe_allow_html=True,
        )


    full_container = st.container()
    call_name = st.session_state.name.split(" ")[0]
    st.title(f"Welcome to AGentV, {call_name}")
    with full_container:
        
        
        # st.container(height=20, border=False)
        
        # st.markdown("## To start the policy generation, ")
        # st.markdown("### Upload the provided organization hierarchy in YAML format.")
        
        # upload_container =  st.container(border=False)
        
            
            # st.container(height=50, border=False)
            
        _,r1col1,s1,r1col2,_ = st.columns([0.20, 1,0.03, 1, 0.20])
        gen_doc = r1col1.button(f"Generate from a **Document**", 
                            key='gen_doc', 
                            type='secondary', 
                            icon=":material/article:", 
                            use_container_width=True, 
                            # disabled= not st.session_state.enable_generation, 
                            help = "Upload a high-level requirement document (e.g., Hospital.md) to auto-generate machine-executable access control policies."
                            )
        
        gen_sent = r1col2.button(f"Generate from a **Sentence**",
                                help = "Enter your access control requirement in plain English and let AGentV convert it into a machine-executable policy.",
                            key='gen_sent', type='secondary', icon=":material/create:", use_container_width=True, 
                            # disabled= not st.session_state.enable_generation
                            )
        
        st.container(height=10, border=False)
        _,r2col1, s2, r2col2,_ = st.columns([0.20, 1,0.03, 1, 0.20])
        corr_policies = r2col1.button(f"Access Control Policies", 
                            key='cor_pol', 
                            type='secondary', 
                            icon=":material/verified_user:", 
                            use_container_width=True, 
                            # disabled= not st.session_state.enable_generation, 
                            help = "Review already generated access control policies and publish to the policy database for testing."
                            )
        
        inc_policies = r2col2.button(f"Incorrect Access Control Policies",
                                help = "Review and refine the incorrectly generated policies manually.",
                            key='inc_pol', type='secondary', icon=":material/gpp_bad:", use_container_width=True, 
                            # disabled= not st.session_state.enable_generation
                            )
        
        st.container(height=10, border=False)
        _,r3col1, s3, r3col2,_ = st.columns([0.20, 1, 0.03, 1, 0.20])
        test_policies = r3col1.button(f"Test Policies", 
                            key='test_pol', 
                            type='secondary', 
                            icon=":material/assignment:", 
                            use_container_width=True, 
                            # disabled= not st.session_state.enable_generation, 
                            help = "Test the published policies by sending access requests."
                            )
        
        save_policies = r3col2.button(f"Download Policies",
                                help = "Download the generated policies.",
                            key='save_pol', type='secondary', icon=":material/download:", use_container_width=True, 
                            # disabled= not st.session_state.enable_generation
                            )
        
        # write_xacml = col3.button(f"Write in **XACML**", 
        #                         help="Manually author your access control policy directly in XACML for full control and customization.", 
        #                         key='write_xacml', type='secondary', icon=":material/code:", use_container_width=True, disabled= not st.session_state.enable_generation
        #                         )
            

        if gen_doc:
            change_page_icon('start_icon')
            st.switch_page('pages/generate_document.py')
            
            
        elif gen_sent:
            change_page_icon('start_icon')
            st.switch_page('pages/generate_individual.py')
        # elif write_xacml:
        #     change_page_icon('start_icon')
        #     st.switch_page('pages/write_policy.py')
        # else:
        #     st.session_state.enable_generation = False
        
        elif corr_policies:
            st.switch_page('pages/correct_policies.py')
        elif inc_policies:
            st.switch_page('pages/incorrect_policies.py')
        elif test_policies:
            st.switch_page('pages/test_policies.py')
        elif save_policies:
            st.switch_page('pages/policy_export.py')

    full_container.float("top: 30%;")
    
start()
standard_menu(turn_on=True)

