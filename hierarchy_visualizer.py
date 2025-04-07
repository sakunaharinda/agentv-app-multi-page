import streamlit as st
import streamlit.components.v1 as components
from utils import store_value
from feedback import *
from loading import get_entity_hierarchy
from vectorstore import build_vectorstores


def set_hierarchy(hierarchy_file):
    
    # try:
    if hierarchy_file is not None:
        main_hierarchy, hierarchies = get_entity_hierarchy(hierarchy_file)
        st.session_state['main_hierarchy'] = main_hierarchy
        st.session_state['hierarchies'] = hierarchies
        
        st.session_state.enable_generation = True
        
        st.session_state.models.vectorestores = build_vectorstores(hierarchies.to_dict())
        
        st.session_state.started = True # To show all the tabs
        
    if st.session_state.vs_generated:
        st.session_state.vs_generated = False
        st.rerun()
            
    # except Exception as e:
    #     error("The hierarchy file cannot be processed. Please ensure that it adheres to YAML guidelines and upload it again")

@st.dialog("Upload the Organization Hierarchy")
def ask_hierarchy():
    
    st.write("Please upload the organization hierarchy and click **OK** to continue")
    
    hierarchy_file = st.file_uploader("Upload the organization hierarchy", key='_hierarchy_upload', help='Upload the organization hierarchy specified in YAML format', type=['yaml', 'yml'], on_change=store_value, args=("hierarchy_upload",))
            
    
    with st.container(height=50, border=False):
        set_hierarchy(hierarchy_file)
    
    col1, col2 = st.columns([1,1])
    with col1:
        req_submit = st.button("OK", key='ok_hierarchy', type='primary', use_container_width=True, disabled=not st.session_state.enable_generation)
        
    with col2:
        req_back = st.button("Cancel", key='cancel_hierarchy', type='secondary', use_container_width=True)
        
    if req_submit:
        
        st.rerun()
            
    elif req_back:
        st.rerun()

def markmap(data, height=600, vertical_padding=50):
    data = str(data)
    markdown_style = '''
            <style>
                .markmap-container {{
                    display: flex;
                    justify-content: center;
                    width: 100%;
                    padding-top: {1}px;
                }}
                svg {{
                    width: 100%;
                    height: {0}px;
                }}
                .markmap {{
                    width: 100%;
                }}
            </style>'''.format(height, vertical_padding)
    
    markdown_html = f'''
        {markdown_style}
        <script src="https://cdn.jsdelivr.net/npm/markmap-autoloader"></script>
        
        <div class="markmap-container">
            <div class='markmap'>{data}</div>
        </div>
    '''

    # Add extra height to accommodate padding
    total_height = height + (vertical_padding)
    markmap_component = components.html(markdown_html, height=total_height)
    return markmap_component

@st.cache_data(show_spinner=False)
def to_markdown(nested_list, entity):
    
    def process_item(item, level=1):
        result = []
        
        if isinstance(item, dict):
            # Process dictionary items
            for key, value in item.items():
                # Add heading for the key
                result.append(f"{'#' * level} {key}\n")
                # Process nested value with increased heading level
                nested_result = process_item(value, level + 1)
                if nested_result:
                    result.append(nested_result)
        
        elif isinstance(item, list):
            # Process list items
            for element in item:
                nested_result = process_item(element, level)
                if nested_result:
                    result.append(nested_result)
        
        else:
            # Process string or other primitive
            result.append(f"{'#' * level} {item}\n")
        
        return "".join(result)
    
    # Generate markdown for the entire nested list
    markdown_content = f"# {entity}\n\n"
    for item in nested_list:
        markdown_content += process_item(item, level=2)
    return markdown_content

@st.cache_data(show_spinner=False)
def get_mardowns(hierarchy):
    
    subject_h = to_markdown(hierarchy['subjects'],'Subjects')
    action_h = to_markdown(hierarchy['actions'], 'Actions')
    resource_h = to_markdown(hierarchy['resources'], 'Resources')
    condition_h = to_markdown(hierarchy['conditions'], 'Conditions')
    
    return subject_h, action_h, resource_h, condition_h


@st.cache_data(show_spinner=False)
def display_hierarchy(main_hierarchy, show_hierarchy, height=300, vertical_padding=40):
    container = st.container()
    subject_m, action_m, resource_m, condition_m = get_mardowns(main_hierarchy)
    with container:
        # Optional: add columns for extra centering control
        _, col2, _ = st.columns([1, 10, 1])
        with col2:
            if show_hierarchy == "Subjects":
                markmap(subject_m, height=height, vertical_padding=vertical_padding)
            elif show_hierarchy == "Actions":
                markmap(action_m, height=height, vertical_padding=vertical_padding)
            elif show_hierarchy == "Resources":
                markmap(resource_m, height=height, vertical_padding=vertical_padding)
            # else:
            #     markmap(condition_m, height=height, vertical_padding=vertical_padding)
                
@st.fragment
def visualize_hierarchy_expander(key):
    
    if st.session_state.main_hierarchy is not None:
        with st.expander("Organization Hierarchy", expanded=st.session_state.expand):
            _,hcol,_ = st.columns([2,2,2])
            show_hierarchy = hcol.segmented_control(label="Organization hierarchy", label_visibility='hidden', options=["Subjects", "Actions", "Resources"], selection_mode='single', default="Subjects", key=key)
            
            display_hierarchy(st.session_state.main_hierarchy, show_hierarchy, height=350, vertical_padding=40)
            
    else:
        ask_hierarchy()

@st.fragment
@st.dialog("Organization Hierarchy", width='large')
def visualize_hierarchy_dialog():
    
    if st.session_state.main_hierarchy is not None:
        _,hcol,_ = st.columns([0.70,1,0.5])
        show_hierarchy = hcol.segmented_control(label="Organization hierarchy", label_visibility='hidden', options=["Subjects", "Actions", "Resources"], selection_mode='single', default="Subjects")
            
        display_hierarchy(st.session_state.main_hierarchy, show_hierarchy, height=350, vertical_padding=40)
    
    ok = st.button("OK", key='ok', type='primary', use_container_width=True)
    
    if ok:
        st.rerun()
            