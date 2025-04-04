import streamlit as st
import streamlit.components.v1 as components

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
            else:
                markmap(condition_m, height=height, vertical_padding=vertical_padding)
                
@st.fragment
def visualize_hierarchy_expander(main_hierarchy, key):
    with st.expander("Organization Hierarchy", expanded=st.session_state.expand):
        
            _,hcol,_ = st.columns([1,2,1])
            show_hierarchy = hcol.segmented_control(label="Organization hierarchy", label_visibility='hidden', options=["Subjects", "Actions", "Resources", "Conditions"], selection_mode='single', default="Subjects", key=key)
            
            display_hierarchy(main_hierarchy, show_hierarchy, height=350, vertical_padding=40)
            