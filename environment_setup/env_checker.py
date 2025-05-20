import sys
import os

# Store the original script directory to correctly locate files relative to REPO_ROOT_PATH
_script_dir = os.path.dirname(__file__)

def ensure_dependencies_installed():
    """
    Checks if primary dependencies 'kit' and 'python-dotenv' are installed.
    If not, it prints detailed instructions for setting them up.
    """
    dependencies_ok = True
    try:
        import kit
        print("[INFO] cased/kit library found.")
    except (ImportError, ModuleNotFoundError):
        dependencies_ok = False
        print("[ERROR] The 'cased/kit' library is not installed or not found.", file=sys.stderr)

    try:
        import dotenv
        print("[INFO] python-dotenv library found.")
    except (ImportError, ModuleNotFoundError):
        dependencies_ok = False
        print("[ERROR] The 'python-dotenv' library is not installed or not found.", file=sys.stderr)
        print("[INFO]  This is needed for loading API keys from a .env file.", file=sys.stderr)

    if not dependencies_ok:
        # Determine the workspace root. Assumes env_checker.py is in environment_setup/ under the root.
        workspace_root = os.path.abspath(os.path.join(_script_dir, '..')) # Use _script_dir
        requirements_path = os.path.join(workspace_root, 'requirements.txt')
        readme_path = os.path.join(workspace_root, 'environment_setup', 'README.md')

        print("[INSTRUCTION] Please ensure you have set up the Python virtual environment and installed all dependencies.", file=sys.stderr)
        print("\nTo set up/update the environment:", file=sys.stderr)
        print("1. Create and activate a virtual environment in the project root (e.g., 'codomyrmex/').", file=sys.stderr)
        print("   Example: python -m venv .venv", file=sys.stderr)
        print("            source .venv/bin/activate  (Linux/macOS)", file=sys.stderr)
        print("            .venv\\Scripts\\activate    (Windows)", file=sys.stderr)
        print(f"2. Install/update dependencies from '{requirements_path}':", file=sys.stderr)
        print(f"   pip install -r \"{requirements_path}\"", file=sys.stderr)
        print(f"   (Ensure 'cased-kit' and 'python-dotenv' are listed in {requirements_path})", file=sys.stderr)
        print("\nFor detailed setup instructions, please refer to: '{readme_path}'", file=sys.stderr)
        sys.exit(1)
    else:
        print("[INFO] Core dependencies (kit, python-dotenv) are installed.")

def check_and_setup_env_vars(repo_root_path: str):
    """
    Checks for a .env file in the repository root and guides the user to create one if it's missing.
    Also, reminds about API keys for LLM features.
    """
    env_file_path = os.path.join(repo_root_path, ".env")
    print(f"[INFO] Checking for .env file at: {env_file_path}")

    if not os.path.exists(env_file_path):
        print(f"[WARN] .env file not found at '{env_file_path}'.")
        print("[INSTRUCTION] To use LLM-dependent features (like code summarization and advanced docstring indexing), API keys are recommended.")
        print("[INSTRUCTION] Please create a '.env' file in the root of your repository ('{repo_root_path}') with the following format:")
        print("------------- .env file example ------------- ")
        print("OPENAI_API_KEY=\"your_openai_api_key_here\"")
        print("ANTHROPIC_API_KEY=\"your_anthropic_api_key_here\"")
        print("GOOGLE_API_KEY=\"your_google_api_key_here\"")
        print("# Add other environment variables as needed")
        print("---------------------------------------------")
        print("[INFO] The script will attempt to load this .env file using 'python-dotenv'.")
        print("[INFO] You can leave keys blank if you do not intend to use a specific LLM provider.")
    else:
        print(f"[INFO] .env file found at '{env_file_path}'. Make sure it contains your API keys if you plan to use LLM features.")

# Example of how ensure_dependencies_installed might be called by itself for basic checks.
# The main analysis script will call it.
if __name__ == '__main__':
    print("Running env_checker.py standalone for basic checks...")
    # To test check_and_setup_env_vars, you'd need to define a mock repo_root_path
    # For example, assuming this script is in codomyrmex/environment_setup/
    mock_repo_root = os.path.abspath(os.path.join(_script_dir, '..'))
    
    ensure_dependencies_installed()
    check_and_setup_env_vars(mock_repo_root)
    print("env_checker.py standalone checks complete.") 