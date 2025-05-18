import streamlit as st
from models.pages import PAGE

def show_page_help():
    
    if st.session_state.current_page == PAGE.START:
        
        starting_page_help()
    
    elif st.session_state.current_page == PAGE.GEN_DOC:
        
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
        
    elif st.session_state.current_page == PAGE.TEST_POLICY:
        
        test_pol_help()
        
    elif st.session_state.current_page == PAGE.SAVE_PAGE:
        
        save_pol_help()
        

@st.dialog("What should I do?", width='large')
def starting_page_help():

    st.write("### Welcome to AGentV 👋")
    
    st.write(
        "AGentV is an intelligent access control policy generation system that helps you translate high-level, human-readable access control requirements "
        "into machine-executable policies using a combination of natural language processing and policy authoring tools."
    )

    st.write("### Step 1: Upload Organization Hierarchy")
    
    st.write(
        "To get started, please **upload the provided organization hierarchy file** in `.yaml` format using the file uploader above."
    )
    
    st.info(
        "The organization hierarchy shows how the subjects (i.e., roles), actions, and resources are arranged in the organization. The **subjects/roles** are the different job titles or responsibilities people have (like HCP, LHCP, and DLHCP). Each role can perform certain **actions** (like read, edit, or write) on specific **resources** (like medical records), which helps define who can do what in access control policies."
    )

    st.write(
        "Once the hierarchy is uploaded, AGentV will automatically process it in the background. "
        "After processing is complete, you’ll see three buttons become active—these are your entry points to begin policy generation."
    )

    st.write("### Step 2: Choose How You Want to Generate Policies")

    st.markdown(
        "**1. Generate from a Document** – Upload a complete access control requirement specification (e.g., `Hospital.md`).\n\n"
        "AGentV will extract and generate access control policies from the document's contents."
    )
    
    st.markdown(
        "**2. Generate from a Sentence** – Type your own access control requirement in English.\n\n"
        "AGentV will convert your sentence into a structured policy by identifying subjects, actions, resources, and other components."
    )

    st.markdown(
        "**3. Write in XACML** – If you’re an experienced user, you can write access control policies directly in XACML.\n\n"
        "This option gives you full control over the policy definition and is ideal for advanced customization."
    )

    st.success(
        "After choosing one of the above options and generating policies, you’ll be able to review, correct, test, and save your policies through AGentV’s guided interface."
    )


@st.dialog("What should I do?", width='large')
def gen_doc_help():
    
    st.write("### Overview")
    
    st.write("This page allows you to upload the provided high-level requirement specification document and translate its access control requirements into machine-executable access control policies.")
        
    st.write("### Step 1: Upload the Requirements Document")
    st.write("Upload the provided high-level access control requirement specification (e.g., `Hospital.md`).")

    st.write("### Step 2: Generate Policies")
    st.write("Click the **Generate** button to start the policy generation process.")
    st.info("Once generation is complete, a **Summary** of the results will be displayed, including the number of sentences in the uploaded document, how many of them are access control requirements, how many of the requirements were correctly translated by AGentV, and how many were incorrectly transltaed.")

    st.write("### Step 3: Review Incorrect Policies")
    st.error("If any policies are generated incorrectly, you’ll be prompted to review them.")
    st.write("Click the **Review** button to navigate to the **Incorrect Policies** page where you can inspect and correct them.")

    st.success("If all policies are generated correctly, you’ll be automatically redirected to the **Correct Policies** page.")
    
@st.dialog("What should I do?", width='large')
def gen_sent_help():
    
    st.write("### Overview")
    
    st.write("This page allows you to write your own access control requirements in English and translate them into machine-executable access control policies.")
        
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
        "If the policy is generated correctly, no further action is needed. You can proceed to the **Access Control Policies** page "
        "to continue the policy generation process."
    )

        
@st.dialog("What should I do?", width='large')
def write_xacml_help():
    
    st.write("### Overview")
    
    st.write("This page allows you to write an access control policy directly in **eXtensible Access Control Markup Language (XACML)**.")
        
    st.write("### Step 1: Write the Policy in XACML")
    st.write("Enter your intended access control policy directly in **XACML** using the provided code editor.")

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

    st.success("Once the policy is published, you can proceed to the **Access Control Policies** page to continue with the policy generation workflow.")
    
@st.dialog("What should I do?", width='large')
def incorrect_pol_help():
    st.write("### Overview")
    
    st.write("This page allows you to review the incorrectly generated access control policies and correct them before publishing them to the policy database.")
    
        
    st.write("### Step 1: Review the Requirement")
    st.write(
        "Carefully read the high-level requirement specification."
    )

    st.info(
        "The generated access control rules from the high-level requirement specification are displayed in a table right below the requirement sentence. "
        "Each **row** represents a rule, and each **column** corresponds to a policy component: "
        "**decision**, **subject**, **action**, **resource**, **purpose**, and **condition**."
        "The erroneous component is highlighted in red for greater visibility."
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
        "Make the necessary corrections by editing specific table cells."
    )

    st.info(
        "Double-check the entire policy for any other potential issues that may not have been flagged by AGentV, and fix them as well."
    )

    st.write("### Step 4: Submit the Corrected Policy")
    st.write(
        "Once you’ve made all corrections, click the **Submit** button to move the policy from **Incorrect Policies** "
        "to **Access Control Policies**."
    )

    st.warning(
        "After submission, changes cannot be made to the policy. Please review it carefully before clicking **Submit**."
    )

    st.write("### Step 5: Repeat")
    st.write(
        "Repeat the same procedure for all the incorrect policies listed in the page."
    )

    st.success(
        "Once all incorrect policies are corrected and submitted, go to the **Access Control Policies** page, "
        "where you can review all your policies and publish them to the Policy Database."
    )
    
@st.dialog("What should I do?", width='large')
def correct_pol_help():
    
    st.write("### Overview")
    st.write(
        "This page allows you to view all the correct access control policies, including:\n"
        "- Policies **automatically generated correctly** by AGentV.\n"
        "- Policies **corrected and submitted** by you from the **Incorrect Policies** page."
    )

    st.info(
        "Each policy is shown with its unique policy ID, access control requirement, and its access control rules broken down into its components in a table format."
    )

    st.write("### Step 1: Filter Policies")
    st.write(
        "Open the :material/tune: Filter expander and set the filtering criteria (i.e., policy ID or the sentence) to see only a subset of policies to review."
    )

    st.write("### Step 2: Publish Policies to the Database")
    st.write(
        "Once you've reviewed the policies, you have several options to publish them to the **Policy Database**:"
    )
    st.markdown(
        "- Click **Publish** infront of each policy to publish **only selected policy** to the policy database.\n"
        "- Click **Publish All** to publish **all the policies at once** to the policy database."
        "- Select the policies you want to publish to the policy database by using the checkbox next to the **Generated Policy** expander in each policy, and click **Publish (x)** button at the bottom of the page."
    )
    
    st.info(
        "There are three badges that can be seen in front of the English access control requirement.\n"
        
        "- :orange-badge[:material/publish: Ready to Publish] : Indicates that the policy is ready to publish to the policy database.\n"
        "- :green-badge[:material/check: Published] : Indicate that the policy is already published to the policy database.\n"
        "- :red-badge[:material/family_history: Outside context] : Indicates that the policy is generated **without** using an organization hierarchy."
        )

    st.warning(
        "Only the published policies will be visualized and available in the next step for testing. "
        "Unpublished policies will not be stored in the Policy Database."
    )
    

    st.success(
        "After publishing the required policies, go to the **Test Policies** pages. "
        "There, you can send access requests and check whether your policies enforce the intended access control rules."
    )
    
@st.dialog("What should I do?", width='large')
def visualize_help():
    
    st.write("View what subjects/roles can do what actions to what resources, represented in an access matrix")
    
@st.dialog("What should I do?", width='large')
def test_pol_help():
    
    st.write("### Overview")
    st.write(
        "This page allows you to **test the published policies** in the Policy Database by sending simulated access requests. "
        "It mimics how real-world access decisions are made using your policies."
    )

    st.info(
        "Each published policy is shown with its unique policy ID, access control requirement, and its access control rules broken down into its components in a table format."
    )

    st.write("### Step 1: Filter Policies")
    st.write(
        "Open the :material/tune: Filter expander and set the filtering criteria (i.e., policy ID or the sentence) to see only a subset of policies to test."
    )
    # st.info(
    #     "The **Access Control Policy Database** serves as the Policy Administration Point (PAP), where all policies created using AGentV are stored."
    # )

    st.write("### Step 2: Ensure All Required Policies Are Available")
    st.write(
        "If any required policies are missing, return to the **Access Control Policies** page and publish them before proceeding."
    )

    st.write("### Step 3: Choose a Testing Option")
    st.write("You can test policies in two ways:")
    st.markdown(
        "1. **Test** – Tests only the **selected policy**.\n"
        "2. **Test** – Tests **all policies** in the Policy Database."
    )
    
    st.warning("If the policy is generated without using an organization hierarchy, :red-badge[:material/family_history: Outside context] badge can be seen in front of the English access control requirement.")

    st.write("### Step 4: Build an Access Request")
    st.write(
        "After choosing a testing option, a dialog will appear where you can select the **Subject**, **Action**, and **Resource** (i.e., policy components) using dropdown menus."
    )
    
    st.info(
        "These dropdown options are based on the organization hierarchy file you uploaded earlier. "
        "To view the hierarchy, click the :material/family_history: **Organization Hierarchy** button at the bottom of the sidebar."
    )
    
    st.write("In case you decide to test a policy generated without using an organization hierarachy, you will need to write the above policy components instead of selecting them via a drop down menu.")

    st.write("### Step 5: Send the Request")
    st.write(
        "After selecting the Subject, Action, and Resource, click **Send Request**. "
        "AGentV will evaluate your request and return a response."
    )

    with st.expander("How does this work under the hood?", icon=":material/biotech:"):
        st.info(
            "When you click **Send Request**, AGentV builds a XACML access control request based on your input and sends it to the Policy Decision Point (PDP). "
            "The PDP retrieves the relevant policies from the PAP, evaluates the request, and returns a decision.\n\n"
            "- AGentV uses the **first-applicable** rule combining algorithm to resolve conflicts within a policy.\n"
            "- It uses the **deny-overrides** policy combining algorithm to resolve conflicts across policies.\n\n"
            "You can learn more about XACML-based systems on the "
            "[official XACML website](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-cd-1-en.html)."
        )

    st.write("### Step 6: Understand the Evaluation Result")
    st.info("Your access request will return one of the following outcomes:")

    st.success("**Allowed** – The selected subject **can** perform the selected action on the selected resource.")
    st.error("**Denied** – The selected subject **cannot** perform the selected action on the selected resource.")
    st.warning(
        "**Not Applicable** – The policy (or policies) do **not apply** to the selected Subject-Action-Resource combination."
    )

    with st.expander("Additional Notes", icon=":material/info:"):
        st.write(
            "You’ll receive a **Not Applicable** result only when testing a specific policy (using the **Test Policy** button) "
            "that does not match the request. "
            "However, when testing the entire system (using the **Test System** button), if **none** of the policies match the request, "
            "AGentV will return a **Deny** decision. This is because it follows the `default-deny` principle."
        )

    st.success(
        "Once you're satisfied with your policy testing, go to the **Save Policies** page from the sidebar. "
        "There, you can export your policies in **JSON** or **XACML** format."
    )
    
@st.dialog("What should I do?", width='large')
def save_pol_help():

    st.write("### Overview")
    st.write(
        "This page allows you to **download and save** all the **published** policies. "
        "You can choose to download them in two formats: **JSON** or **XACML**."
    )

    st.write("### Step 1: Choose a Format")
    st.write("You have two options to save your policies:")

    st.markdown(
        "1. **Save as JSON** – Click this button to download **published policies in a single JSON file**.\n"
        "2. **Save as XACML** – Click this button to download the policies as **separate XML files** written in XACML. "
        "Each file will represent one policy."
    )

    st.info(
        "The **JSON format** is useful for programmatic analysis, debugging, or integrating with other systems.\n\n"
        "The **XACML format** is the official standard for expressing access control policies and can be directly used "
        "in any XACML-compliant authorization system."
    )

    st.write("### Step 2: Download the Policies")
    st.write(
        "Once you click your preferred option, your browser will start downloading the file(s). "
        "You can store these files locally or use them in your organization’s access control infrastructure."
    )

    st.success("🎉 That’s it! You’ve completed the policy generation, verification, and export process with AGentV.")
    st.write("You may return to any previous tab using the sidebar to make changes or test policies again.")

