import streamlit as st
from models.pages import PAGE

def show_page_help():
    
    if st.session_state.current_page == PAGE.GEN_DOC:
        
        gen_doc_help()
        
    elif st.session_state.current_page == PAGE.GEN_SENT:
        
        gen_sent_help()
        
    elif st.session_state.current_page == PAGE.WRITE_XACML:
        
        write_xacml_help()
        
    elif st.session_state.current_page == PAGE.INCORRECT_POL:
        
        incorrect_pol_help()
        
    elif st.session_state.current_page == PAGE.CORRECT_POL:
        
        correct_pol_help()
        
    elif st.session_state.current_page == PAGE.VIZ_POLICY:
        
        visualize_help()

@st.dialog("What should I do?", width='large')
def gen_doc_help():
        
    st.write("### Step 1: Upload the Requirements Document")
    st.write("Upload the provided high-level access control requirement specification (e.g., `Hospital.md`).")

    st.write("### Step 2: Generate Policies")
    st.write("Click the **Generate** button to start the policy generation process.")
    st.info("Once generation is complete, a **Summary** of the results will be displayed, including both correct and incorrect policies.")

    st.write("### Step 3: Review Incorrect Policies")
    st.error("If any policies are generated incorrectly, you’ll be prompted to review them.")
    st.write("Click the **Review** button to navigate to the **Incorrect Policies** page where you can inspect and correct them.")

    st.success("If all policies are generated correctly, you’ll be automatically redirected to the **Correct Policies** page.")
    
@st.dialog("What should I do?", width='large')
def gen_sent_help():
        
    st.write("### Step 1: Enter Access Control Requirements")
    st.write("Write your access control requirement in natural language (e.g., English) in the text box at the bottom of the page.")

    st.write("### Step 2: Generate Policy")
    st.write("Click the **Generate** button to start the policy generation process.")

    st.info(
        "Once the policy is generated, you will see the original English requirement along with the **Generated Policy**, "
        "presented in a table format. The table breaks down each access control rule into its components: "
        "**decision**, **subject**, **action**, **resource**, **purpose**, and **condition**."
    )


    st.write("### Step 3: Review Incorrect Policies")
    st.error(
        "If the policy is generated incorrectly, an error message will appear. You will be prompted to review and correct the "
        "incorrectly generated policy."
    )
    st.write("Click the **Review** button to go to the **Incorrect Policies** page, where you can inspect and fix the errors.")

    st.success(
        "If the policy is generated correctly, no further action is needed. You can proceed to the **Correct Policies** page "
        "to continue the policy generation process."
    )

        
@st.dialog("What should I do?", width='large')
def write_xacml_help():
        
    st.write("### Step 1: Write the Policy in XACML")
    st.write("Enter your intended access control policy directly in **eXtensible Access Control Markup Language (XACML)** using the provided code editor.")

    st.info("Ensure that the `PolicyId` is **unique** across all policies you create.")

    st.write("### Step 2: Save the Policy")
    st.write("Click the **Save** icon (:material/save:) located at the bottom-right corner of the code editor.")

    st.warning(
        "Unlike policies generated from documents or natural language, policies written directly in XACML **will not be verified** "
        "for correctness, nor will they be **visualized** in the access matrix."
    )

    st.write("### Step 3: Publish the Policy")
    st.write("Click the **Publish Policy to Database** button at the bottom of the page to save your policy in AGentV’s policy database.")

    st.info(
        "The **Access Control Policy Database** is used to store all policies created through AGentV. "
        "Later, you can send access requests to this database to evaluate whether your policy correctly enforces the intended access requirements."
    )

    st.success("Once the policy is published, you can proceed to the **Correct Policies** page to continue with the policy generation workflow.")
    
@st.dialog("What should I do?", width='large')
def incorrect_pol_help():
        
    st.write("### Step 1: Review the Requirement")
    st.write(
        "Carefully read the high-level requirement specification shown in the text box labeled **Incorrectly Generated Policy**."
    )

    st.info(
        "The generated access control rules from the high-level requirement specification are displayed in a table below the requirement sentence. "
        "Each **row** represents a rule, and each **column** corresponds to a policy component: "
        "**decision**, **subject**, **action**, **resource**, **purpose**, and **condition**."
    )

    st.write("### Step 2: Understand the Feedback")
    st.write(
        "AGentV provides detailed feedback that includes:\n"
        "1. A description of the **error** in the generated policy.\n"
        "2. The **location** of the error (using the table's row number and column name).\n"
        "3. Guidance on **how to resolve** the error."
    )

    st.write("### Step 3: Fix the Policy")
    st.write(
        "Make the necessary corrections by editing specific table cells or adding new rows, as per the feedback."
    )

    st.info(
        "Double-check the entire policy for any other potential issues that may not have been flagged by AGentV, and fix them as well."
    )

    st.write("### Step 4: Submit the Corrected Policy")
    st.write(
        "Once you’ve made all corrections, click the **Submit** button to move the policy from **Incorrect Policies** "
        "to **Correct Policies**."
    )

    st.warning(
        "After submission, changes cannot be made to the policy. Please review it carefully before clicking **Submit**."
    )

    st.write("### Step 5: Navigate Between Policies")
    st.write(
        "Use the **Next** and **Previous** buttons to navigate through the incorrectly generated policies. "
        "Repeat Steps 1 to 4 for each one."
    )

    st.success(
        "Once all incorrect policies are corrected and submitted, you will be automatically redirected to the **Correct Policies** page, "
        "where you can review all your policies and publish them to the Policy Database."
    )
    
@st.dialog("What should I do?", width='large')
def correct_pol_help():
    
    st.write("### Step 1: Review Correct Policies")
    st.write(
        "View all the correct access control policies, including:\n"
        "- Policies **automatically generated correctly** by AGentV.\n"
        "- Policies **corrected and submitted** by you from the **Incorrect Policies** page."
    )

    st.info(
        "Each policy is shown in the text box labeled **Correctly Generated Policy**, and broken down into its components in a table format."
    )

    st.write("### Step 2: Navigate Through Policies")
    st.write(
        "Use the **Next** and **Previous** buttons below the policy viewer to browse through all correct policies one at a time."
    )

    st.write("### Step 3: Publish Policies to the Database")
    st.write(
        "Once you've reviewed the policies, you have two options to publish them to the **Policy Database**:"
    )
    st.markdown(
        "- Click **Publish Policy to Policy Database** to publish **only the currently viewed policy**.\n"
        "- Click **Publish Policies to Policy Database** to publish **all correct policies at once**."
    )

    st.warning(
        "Only published policies will be available in the next step for testing. "
        "Unpublished policies will not be stored in the Policy Database."
    )

    st.success(
        "After publishing the required policies, go to the **Test Policies** pages. "
        "There, you can send access requests and check whether your policies enforce the intended access control rules."
    )
    
@st.dialog("What should I do?", width='large')
def visualize_help():
    
    st.write("### View what subjects/roles can do what actions to what resources, represented in an access matrix")
    


