---
sidebar_label: 'Usage Examples'
title: 'Environment Setup - Usage Examples'
---

# Environment Setup - Usage Examples

This section provides examples related to using the `environment_setup` module, primarily focusing on executing setup steps or verification scripts.

## Example 1: Initial Python Environment Setup

This example shows the commands for setting up the basic Python environment for the Codomyrmex project.

```bash
# 1. Clone the repository (if not done)
# git clone <repository_url>
# cd codomyrmex

# 2. Create a Python virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows (Git Bash or similar):
# source .venv/Scripts/activate
# On Windows (Command Prompt/PowerShell):
# .venv\Scripts\activate

# 4. Install Python dependencies
pip install -r requirements.txt
```

### Expected Outcome

- A `.venv` directory is created in the project root.
- Your shell prompt changes to indicate the virtual environment is active (e.g., `(.venv) your-prompt$`).
- All Python packages listed in `requirements.txt` are installed into the virtual environment.
- You can now run Python scripts that depend on these packages from within this activated environment.

## Example 2: Running the Conceptual Environment Checker Script

This example demonstrates how to run the conceptual `env_checker.py` script (if implemented) to verify your setup.

```bash
# Ensure your virtual environment is active
# source .venv/bin/activate

python environment_setup/env_checker.py
```

### Expected Outcome

- The script prints a series of checks to the console, for example:
  ```
  Checking Codomyrmex Environment...
  [OK] Python version 3.9.5 found.
  [OK] pip is available.
  [OK] Git is installed.
  [INFO] Node.js check: Version 18.12.0 found.
  [INFO] npm check: Version 8.19.2 found.
  [WARNING] Graphviz not found. Some visualization features may be unavailable.
  Environment check complete. Some optional tools are missing.
  ```
- The script exits with a status code (0 for all essential checks passed, non-zero otherwise).

## Example 3: Setting up Docusaurus for Documentation Development

This example shows the commands to set up and run the Docusaurus documentation site locally.

```bash
# 1. Navigate to the documentation module
cd documentation

# 2. Install Node.js dependencies (if not already done)
npm install

# 3. Start the Docusaurus development server
npm run start
```

### Expected Outcome

- Node.js dependencies are installed in `documentation/node_modules/`.
- A local web server starts, typically at `http://localhost:3000`.
- Your web browser opens to this address, showing the documentation site.
- Changes to documentation files will typically auto-reload the site in the browser.

## Common Pitfalls & Troubleshooting

- **Issue**: `command not found: python` or `pip`.
  - **Solution**: Ensure Python is installed and its `bin` directory (and `Scripts` on Windows) is in your system's PATH. For `pip`, it usually comes with Python but might need explicit installation or PATH adjustment in older/custom setups.
- **Issue**: `ModuleNotFoundError` when running Python scripts after activating `.venv`.
  - **Solution**: Double-check that `pip install -r requirements.txt` completed successfully *after* activating the virtual environment. Ensure you are in the correct virtual environment.
- **Issue**: `npm command not found`.
  - **Solution**: Ensure Node.js (which includes npm) is installed and its `bin` directory is in your system's PATH.
- **Issue**: Docusaurus `npm run start` fails due to port conflicts.
  - **Solution**: Another application might be using port 3000. You can often specify a different port: `npm run start -- --port 3001`. 