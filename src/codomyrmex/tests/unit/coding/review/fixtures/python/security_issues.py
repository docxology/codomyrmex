import os
import pickle

import base64
import hashlib







"""Python file with security issues for testing security analysis.
"""

def insecure_function(user_input):
    """Function with multiple security issues."""
    # SQL injection vulnerability

    # Command injection vulnerability
    os.system(f"echo {user_input}")

    # Path traversal vulnerability
    file_path = f"/var/data/{user_input}"
    with open(file_path) as f:
        content = f.read()

    # Insecure deserialization
    data = base64.b64decode(user_input)
    pickle.loads(data)

    # Information disclosure
    print(f"Debug info: {user_input}")

    return content

def weak_crypto_example(password):
    """Example of weak cryptographic practices."""
    # Weak hashing (MD5)
    hash_obj = hashlib.md5(password.encode())
    return hash_obj.hexdigest()

def hardcoded_credentials():
    """Example with hardcoded credentials."""
    username = "admin"
    password = "super_secret_password_123"

    if username == "admin" and password == "super_secret_password_123":
        return True

    return False

class InsecureClass:
    """Class with insecure defaults."""

    def __init__(self):


        self.api_key = "sk-1234567890abcdef"  # Hardcoded API key
        self.debug_mode = True  # Debug mode enabled by default

    def process_sensitive_data(self, data):
        """Process sensitive data without proper validation."""
        # No input validation
        # No encryption
        # Logs sensitive data
        print(f"Processing: {data}")

        return data

