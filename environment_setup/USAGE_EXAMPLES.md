# Environment Setup - Usage Examples

This document provides usage examples for the `environment_setup` module, primarily focusing on the `env_checker.py` script and its functions.

## Example 1: Running `env_checker.py` as a Standalone Script

This is the most common way to quickly validate your project environment.

```bash
# Navigate to the Codomyrmex project root directory
# cd /path/to/codomyrmex

# Execute the env_checker.py script
python environment_setup/env_checker.py
```

### Expected Outcome

- The script will first attempt to import essential Python dependencies (e.g., `cased`, `dotenv`). 
    - If any are missing, it will print an error message to `stderr` instructing you to install them (usually via `pip install -r requirements.txt`) and then exit.
- If dependencies are present, it will then check for the `.env` file in the project root.
    - If `.env` is found, it will print a confirmation message and attempt to load it.
    - If `.env` is missing, it will print a detailed message to `stdout` guiding you on how to create it, including a template with common API key placeholders (e.g., `OPENAI_API_KEY`), and then exit.
- If both checks pass, you should see messages indicating success.

## Example 2: Importing and Using `env_checker.py` Functions in Another Script

Modules or utility scripts within Codomyrmex can programmatically use the functions from `env_checker.py` to perform environment validation at runtime.

```python
# In your_module/your_script.py

import os
import sys

# Determine the project root path (adjust if your script is nested differently)
# This example assumes your_script.py is one level inside a module directory, 
# and the module directory is at the project root.
# For example: codomyrmex/your_module/your_script.py
# then project_root should be codomyrmex/

# A more robust way to find project root might be needed depending on script location
# This is a basic example assuming a known structure.
try:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..')) # Adjust '..', '..' based on actual depth
    # Verify a known marker for project root, e.g., the presence of 'requirements.txt' or '.git'
    if not os.path.exists(os.path.join(project_root, 'requirements.txt')):
        # Fallback or raise error if heuristic fails
        print("Error: Could not reliably determine project root for env_checker.py. Please ensure your script correctly identifies it.", file=sys.stderr)
        # As a simple fallback, assuming script is run from somewhere within project:
        project_root = os.getcwd() 
        print(f"Attempting to use current working directory as project root: {project_root}", file=sys.stderr)

except NameError: # __file__ is not defined (e.g. in an interactive session)
    project_root = os.getcwd()
    print(f"Warning: __file__ not defined. Using current working directory as project root for env_checker: {project_root}", file=sys.stderr)


# Import the functions
# Ensure environment_setup is in PYTHONPATH or script is run in a way that allows the import
try:
    from environment_setup.env_checker import ensure_dependencies_installed, check_and_setup_env_vars
except ImportError:
    print("Error: Could not import from environment_setup.env_checker. Make sure PYTHONPATH is set correctly or run from project root.", file=sys.stderr)
    # Potentially add environment_setup to sys.path if a known relative path exists
    # For example, if this script is in codomyrmex/some_module/script.py:
    # sys.path.append(os.path.join(project_root, 'environment_setup'))
    # from env_checker import ensure_dependencies_installed, check_and_setup_env_vars
    sys.exit(1) # Exit if import fails

print("Performing environment checks...")

# Check 1: Ensure core Python dependencies are installed
ensure_dependencies_installed()
print("Core Python dependencies seem to be installed.")

# Check 2: Ensure .env file is present and set up
# The check_and_setup_env_vars function expects the absolute path to the repository root.
check_and_setup_env_vars(repo_root_path=project_root)
print(f".env file check completed. API keys should now be loaded if .env exists at {project_root}.")

# Now you can safely access environment variables, e.g.:
# my_api_key = os.getenv("OPENAI_API_KEY")
# if my_api_key:
#     print("Successfully retrieved OPENAI_API_KEY.")
# else:
#     print("OPENAI_API_KEY not found in environment.")

print("Environment checks passed. Proceeding with script execution.")
# ... rest of your script's logic ...

```

### Expected Outcome

- Similar to Example 1, the imported functions will perform their respective checks.
- If `ensure_dependencies_installed()` fails, the script will exit with a message.
- If `check_and_setup_env_vars()` finds the `.env` file missing (after being provided the project root), it will print guidance and exit.
- If both checks pass, messages indicating success will be printed, and the calling script can proceed, assuming necessary environment variables are loaded.

## Example 3: Shell Scripts for General Environment Setup

For examples of shell commands and step-by-step instructions for setting up the broader project environment (including Python virtual environments, `pip install`, Node.js setup for the `documentation` module, etc.), please refer to:

- **The `environment_setup/README.md` file**: Specifically, the section "I. General Project Development Environment Setup".
- **The main project `README.md`**: This may also contain or be the primary source for these instructions once reorganized as suggested.

These READMEs provide the command sequences for initial setup.

## Common Pitfalls & Troubleshooting

- **Issue**: `ImportError: No module named environment_setup.env_checker` (or similar) when trying to import functions in your own script.
  - **Solution**: 
    - Ensure your script is run from a context where Python can find the `environment_setup` module. This usually means running your script from the project root directory (`codomyrmex/`).
    - If running from a subdirectory, ensure the `codomyrmex/` directory (which contains `environment_setup/`) is in your `PYTHONPATH` environment variable, or modify `sys.path` dynamically in your script (see commented example in the Python script above, but use with caution).
    - Activate your Python virtual environment (`source .venv/bin/activate`) where project dependencies are installed.

- **Issue**: `env_checker.py` (or imported functions) cannot find `.env` even if it exists, or suggests creating it in the wrong place.
  - **Solution**: The `check_and_setup_env_vars()` function relies on the `repo_root_path` argument being correctly passed to it. Ensure this path accurately points to the directory where your `.env` file is (or should be) located, which is typically the main `codomyrmex/` project root.

- **Issue**: "Essential dependencies are missing" for packages you believe are installed.
  - **Solution**: 
    - Double-check you are in the correct Python virtual environment (`source .venv/bin/activate`).
    - Run `pip list` to see installed packages in the current environment.
    - Ensure `requirements.txt` in the project root is up-to-date and re-run `pip install -r requirements.txt`. 