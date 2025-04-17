import streamlit as st
from utils import store_value_gen_h, change_page_icon
from feedback import *
from streamlit_float import *
from models.pages import PAGE
from menus import standard_menu
from hierarchy_visualizer import visualize_hierarchy_dialog

@st.fragment
def start():
    st.session_state.current_page = PAGE.START

    float_init()

    st.markdown(
            f"""
            <style>
                .st-key-gen_doc button,
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

    # if st.session_state.first_time:
    #     intro()


    full_container = st.container()

    with full_container:
        st.title("Welcome to AGentV")
        
        st.container(height=20, border=False)
        
        st.markdown("## To start the policy generation, ")
        st.markdown("### Upload the provided organization hierarchy in YAML format.")
        
        # load_value("hierarchy_upload")
        upload_container =  st.container(border=False, height=160)
        pbar = st.container(height=50, border=False)
        
        hierarchy_file = upload_container.file_uploader("Upload the provided organization hierarchy in YAML format.", key='_hierarchy_upload', help='The provided organization hierarchy shows how the subjects (i.e., roles), actions, and resources are arranged in the organization. The **subjects/roles** are the different job titles or responsibilities people have (like HCP, LHCP, and DLHCP). Each role can perform certain **actions** (like read, edit, or write) on specific **resources** (like medical records), which helps define who can do what in access control policies.', type=['yaml', 'yml'], on_change=store_value_gen_h, args=("hierarchy_upload",pbar,), label_visibility='collapsed')
        
        if st.session_state._hierarchy_upload and st.session_state.show_hierarchy:
            change_page_icon('start_icon')
            st.session_state.show_hierarchy = False
            visualize_hierarchy_dialog()
            
                

        _,col1, col2,col3,_ = st.columns([0.05, 1,1,1, 0.05])
        gen_doc = col1.button(f"Generate from a **Document**", 
                            key='gen_doc', 
                            type='secondary', 
                            icon=":material/article:", 
                            use_container_width=True, 
                            disabled= not st.session_state.enable_generation, 
                            help = "Upload a high-level requirement document (e.g., Hospital.md) to auto-generate machine-executable access control policies."
                            )
        
        gen_sent = col2.button(f"Generate from a **Sentence**",
                                help = "Enter your access control requirement in plain English and let AGentV convert it into a machine-executable policy.",
                            key='gen_sent', type='secondary', icon=":material/create:", use_container_width=True, disabled= not st.session_state.enable_generation
                            )
        
        write_xacml = col3.button(f"Write in **XACML**", 
                                help="Manually author your access control policy directly in XACML for full control and customization.", 
                                key='write_xacml', type='secondary', icon=":material/code:", use_container_width=True, disabled= not st.session_state.enable_generation
                                )
            

    if gen_doc:
        change_page_icon('start_icon')
        st.switch_page('pages/generate_document.py')
        
    elif gen_sent:
        change_page_icon('start_icon')
        st.switch_page('pages/generate_individual.py')
        
    elif write_xacml:
        change_page_icon('start_icon')
        st.switch_page('pages/write_policy.py')
        


    # with pbar:
    #     set_hierarchy(hierarchy_file)
        
    full_container.float("top: 20%;")

standard_menu()
start()
