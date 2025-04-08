import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout

def show_workflow():
    
    primary_button_style = {'color': 'white', 'backgroundColor': '#FF4B4B', 'border-style': 'none', 'text-align': 'center', 'padding': 0, 'height': '35px', 'padding-left': '10px', 'padding-right': '10px'}
    
    normal_cell_style = {'text-align': 'center', 'padding': 0, 'height': '35px', 'padding-left': '10px', 'padding-right': '10px'}
    
    nodes = [
        StreamlitFlowNode( id='0', 
            pos=(-50, 125), 
            data={'content': 'Upload Hierarchy'}, 
            node_type='input', 
            source_position='right', 
            draggable=False,
            style=normal_cell_style
            ),
        StreamlitFlowNode( id='1', 
            pos=(250, 0), 
            data={'content': 'Write in XACML'}, 
            node_type='default', 
            source_position='right', 
            target_position='left',
            draggable=False,
            style=normal_cell_style
            ),
        StreamlitFlowNode( id='1.1', 
            pos=(250, 125), 
            data={'content': 'Generate from Document'}, 
            node_type='default', 
            source_position='right', 
            target_position='left',
            draggable=False,
            style = normal_cell_style
            ),
        StreamlitFlowNode( id='1.2', 
            pos=(250, 200), 
            data={'content': 'Generate from Sentence'}, 
            node_type='default', 
            source_position='right', 
            target_position='left',
            draggable=False,
            style = normal_cell_style
            ),
        # StreamlitFlowNode(  '2',
        #     (230, 125), 
        #     {'content': 'Generate'}, 
        #     'default', 
        #     'right', 
        #     'left', 
        #     draggable=False,
        #     style= primary_button_style
        #     ),
        StreamlitFlowNode(  '3', 
            (100, 125), 
            {'content': 'Policy Generation'}, 
            'default', 
            'right', 
            'left', 
            draggable=False,
            style=normal_cell_style
            ),
        StreamlitFlowNode(  '4', 
            (430, 125), 
            {'content': 'Review'}, 
            'default', 
            'right',
            'left', 
            draggable=False,
            style=normal_cell_style
            ),
        
        StreamlitFlowNode(  '5', 
            (570, 50), 
            {'content': 'Correct Policies'}, 
            'default', 
            'right',
            'left', 
            draggable=False,
            style={'color': '#177233', 'backgroundColor': '#EBF9EE', 'border-style': 'none', 'text-align': 'center', 'padding': 0, 'height': '35px', 'padding-left': '10px', 'padding-right': '10px'}
            ),
        
        StreamlitFlowNode(  '12', 
            (700, 0), 
            {'content': 'Publish to Database'}, 
            'default', 
            'right',
            'left', 
            draggable=False,
            style=normal_cell_style
            ),
        
        StreamlitFlowNode(  '6', 
            (530, 200), 
            {'content': 'Incorrect Policies'}, 
            'default', 
            'top',
            'left' ,
            draggable=False,
            style={'color': '#7D353A', 'backgroundColor': '#F2E1E5', 'border-style': 'none', 'text-align': 'center', 'padding': 0, 'height': '35px', 'padding-left': '10px', 'padding-right': '10px'}
            ),
        
        StreamlitFlowNode(  '7', 
            (520, 125), 
            {'content': 'Fix Incorrect Policies'}, 
            'default', 
            'top',
            'bottom' ,
            draggable=False,
            style=normal_cell_style
            ),
        StreamlitFlowNode(  '8', 
            (900, 0), 
            {'content': 'Test Policy'}, 
            'output', 
            'right',
            'left', 
            draggable=False,
            style=normal_cell_style),
        StreamlitFlowNode(  '9', 
            (900, 50), 
            {'content': 'Test System'}, 
            'output', 
            'right',
            'left', 
            draggable=False,
            style=normal_cell_style),
        StreamlitFlowNode(  '10', 
            (900, 100), 
            {'content': 'Export as JSON'}, 
            'output', 
            'right',
            'left', 
            draggable=False,
            style=normal_cell_style
            ),
        StreamlitFlowNode(  '11', 
            (900, 200), 
            {'content': 'Visualize'}, 
            'output', 
            'right',
            'left', 
            draggable=False,
            style=normal_cell_style
            ),
        StreamlitFlowNode(  '13', 
            (900, 150), 
            {'content': 'Export as XACML'}, 
            'output', 
            'right',
            'left', 
            draggable=False,
            style=normal_cell_style
            )
        
        ]

    edges = [
        StreamlitFlowEdge('0-3', '0', '3', animated=True, marker_end={'type': 'arrow'}),
        StreamlitFlowEdge('3-1', '3', '1', animated=True, marker_end={'type': 'arrow'}),
        StreamlitFlowEdge('3-1.1', '3', '1.1', animated=True, marker_end={'type': 'arrow'}),
        StreamlitFlowEdge('3-1.2', '3', '1.2', animated=True, marker_end={'type': 'arrow'}),
        StreamlitFlowEdge('1.1-4', '1.1', '4', animated=True, marker_end={'type': 'arrow'}),
        # StreamlitFlowEdge('1-2', '1', '3', animated=True, marker_end={'type': 'arrow'}),
        StreamlitFlowEdge('1.2-4', '1.2', '4', animated=True, marker_end={'type': 'arrow'}),
            StreamlitFlowEdge('1-12', '1', '12', animated=True, marker_end={'type': 'arrow'}),
            # StreamlitFlowEdge('3-4', '3', '4', animated=True, marker_end={'type': 'arrow'}),
            StreamlitFlowEdge('4-5', '4', '5', animated=True, marker_end={'type': 'arrow'}),
            StreamlitFlowEdge('4-6', '4', '6', animated=True, marker_end={'type': 'arrow'}),
            StreamlitFlowEdge('6-7', '6', '7', animated=True, marker_end={'type': 'arrow'}),
            StreamlitFlowEdge('7-5', '7', '5', animated=True, marker_end={'type': 'arrow'}),
            StreamlitFlowEdge('5-12', '5', '12', animated=True, marker_end={'type': 'arrow'}),
            StreamlitFlowEdge('12-8', '12', '8', animated=True, marker_end={'type': 'arrow'}),
            StreamlitFlowEdge('12-9', '12', '9', animated=True, marker_end={'type': 'arrow'}),
            StreamlitFlowEdge('12-10', '12', '10', animated=True, marker_end={'type': 'arrow'}),
            StreamlitFlowEdge('5-11', '5', '11', animated=True, marker_end={'type': 'arrow'}),
            StreamlitFlowEdge('12-13', '12', '13', animated=True, marker_end={'type': 'arrow'})
            ]

    if 'static_flow_state' not in st.session_state:
        st.session_state.static_flow_state = StreamlitFlowState(nodes, edges)

    streamlit_flow('static_flow',
        st.session_state.static_flow_state,
        height=250,
        fit_view=True,
        show_minimap=False,
        show_controls=False,
        pan_on_drag=True,
        allow_zoom=True,
        hide_watermark=True)
    
@st.dialog("🚀 Welcome to AGentV", width="large")
def intro():
    
    # with st.container(height=600, border=False,):
    # _,col,_ = st.columns([1,2,1])

    # col.title("🚀 Welcome to AGentV")
    
    st.write("**AGentV** is an intelligent access control policy generation tool designed to assist system administrators in seamlessly translating high-level natural language requirements into enforceable policies. By leveraging advanced natural language processing (NLP) techniques and structured policy verification, AGentV streamlines policy creation, minimizes errors, and enhances decision-making efficiency.")
    
    show_workflow()
    
    with st.expander("**Step 1: Upload the Organization Hierarchy**", icon=":material/family_history:"):
        st.write("Before start the policy generation, upload the organization hierarchy as a YAML file.")
        st.success("If the processing of the hierarchy is successful, you will be able access the organization hierarchy as a graph in the side bar.")
    
    with st.expander("**Step 2: Choose a Generation Mode**", icon=":material/input:"):
        st.write("After the Step 1 you have three options/paths to start the policy generation:")
        st.markdown("- **Option 1: Generate from a Document** – Upload a document containing high-level natural language access control requirements.")
        st.markdown("- **Option 2: Generate from a Sentence** – Manually enter an access control requirement in natural language.")
        st.success("Click the **Generate** button to start policy generation.")
        st.markdown("- **Option 3: Write in XACML** – Manually write the access control policy in XACML using the provided code editor")
        st.warning("If you proceed with **Option 3**, the resultant policies will neither be verified nor visualized.")
        
    with st.expander("**Step 3: Review Generated Policies**", icon=":material/reviews:"):
        st.write("Generated policies are displayed under two main categories:")
        st.markdown("- **Correct Policies** – Successfully translated policies.")
        st.markdown("- **Incorrect Policies** – Policies requiring corrections.")
        st.error("Check the **Incorrect Policies** tab to fix errors.")
        
    with st.expander("**Step 4: Fix Incorrect Policies**", icon=":material/construction:"):
        st.write("Go to the **Incorrect Policies** page.")
        st.markdown("- View the original natural language requirement. Click Next/Previous buttons through navigate through the incorrect access control policies.")
        st.markdown("- Read the system-generated error feedback.")
        st.markdown("- Edit policy components (Decision, Subject, Action, Resource, Purpose, Condition) according to the feedback, by choosing the correct component from the drop down menus.")
        st.success("Click **Submit** to move the corrected policy to the **Correct Policies** tab.")
        
    with st.expander("**Step 5: Visualize Policies**", icon=":material/table:"):
        st.write("Visualize the **Correct Policies** as an **Access Matrix** by navigating to the **Visualize Policies** page from the side bar.")
        st.info("This helps in analyzing how policies are connected within the system.")
            
    with st.expander("**Step 6: Publish Correct Policies to the Policy Database**", icon=":material/publish:"):
        st.write("Once the all incorrect policies are reviewed and corrected, publish the policies to the **Policy Database** by clicking either **Publish Policy to Database** or **Publish All Policies to Database**")
        st.info("The published policies can be tested in the **Test Policies** page")
        
    with st.expander("**Step 7: Test the Policies**", icon=":material/bug_report:"):
        st.write("You can create and send access requests to the policies published to the policy database by clicking, ")
        st.markdown("- **Test Policy** to create and send requests to test the currently-viewed policy.")
        st.markdown("- **Test System** to create and send requests to test the entire policy database.")
        st.success("View authorization results directly in AGentV.")

    with st.expander("**Step 8: Save the generated policies**", icon=":material/save:"):
        
        st.write("You can click **Save Policies** tab in the side bar and click,")
        st.markdown("- **Save as JSON** to download a JSON file containing all the correct policies.")
        st.markdown("- **Save as XACML** to download a zip file containing correct policies written in XACML.")
        st.success("Saved policies can be applied to your own authorization system")
        
if __name__ == '__main__':
    
    intro()