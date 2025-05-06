import sys
from streamlit_authenticator import Hasher
import warnings
import logging

logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context").setLevel(logging.ERROR)

if len(sys.argv) != 2:
    print("Usage: python hash_password.py <password>")
    sys.exit(1)

password = sys.argv[1]

hashed_password = Hasher.hash(password)
print(hashed_password)
