from enum import Enum

class PAGE(Enum):
    START = "starting_page"
    GEN_DOC = "gen_from_doc_page"
    GEN_SENT = "gen_from_sent_doc"
    WRITE_XACML = "write_xacml_doc"
    CORRECT_POL = "correct_policy_page"
    INCORRECT_POL = "incorrect_policy_page"
    VIZ_POLICY = "visualize_policy_page"
    TEST_POLICY = "test_policy_page"
    SAVE_PAGE = "save_policy_page"