# Environment Setup - Troubleshooting and OS-Specific Guide

This document provides troubleshooting tips for common environment setup issues encountered while setting up the Codomyrmex project, along with some OS-specific considerations.

<!-- TODO: This guide should be a living document. Add new issues and solutions as they are encountered by developers. -->

## 1. General Troubleshooting Steps

When you encounter an issue during setup, try these general steps first:

1.  **Read Error Messages Carefully**: Error messages often contain clues about the problem and sometimes suggest solutions.
2.  **Consult `environment_setup/README.md`**: Ensure you've followed all steps in the "General Project Development Environment Setup" section of the module's main README.
3.  **Check `env_checker.py` Output**: Run `python environment_setup/env_checker.py`. It can pinpoint missing Python dependencies or `.env` file issues.
4.  **Active Virtual Environment**: Ensure your Python virtual environment (e.g., `.venv`) is activated. Your terminal prompt usually indicates this (e.g., `(.venv) your-prompt$`). If not, activate it:
    - Linux/macOS: `source .venv/bin/activate`
    - Windows: `.venv\Scripts\activate`
5.  **Python and Pip Versions**: Verify your Python version (`python --version` or `python3 --version`) and pip version (`pip --version`). Ensure they meet the project prerequisites (Python 3.9+).
6.  **Internet Connection**: Some steps (like `pip install` or `npm install`) require an internet connection to download packages.
7.  **Permissions**: Ensure you have the necessary permissions to install software or create files/directories in the locations required.

## 2. Common Python Setup Issues

### Issue: `python` or `pip` command not found

- **Cause**: Python is not installed, or its installation directory (and Scripts subdirectory for pip) is not in your system's PATH environment variable.
- **Solution**:
    - **All OS**: 
        - <!-- TODO: Provide a link to official Python download page (python.org). -->
        - Install Python, ensuring to check the option "Add Python to PATH" (or similar) during installation if available (especially on Windows).
    - **Linux**:
        - <!-- TODO: Add common commands for installing Python via package managers like apt (Debian/Ubuntu) or yum/dnf (Fedora/CentOS), e.g., `sudo apt update && sudo apt install python3 python3-pip python3-venv`. -->
    - **macOS**:
        - <!-- TODO: Mention that macOS often comes with an older Python 2. Explain how to install Python 3 (e.g., from python.org, or using Homebrew: `brew install python`). Ensure `python3` and `pip3` are used or that the Homebrew-installed Python is prioritized in PATH. -->
    - **Windows**:
        - <!-- TODO: Emphasize checking "Add Python to PATH" during installation. Explain how to manually add Python to PATH if missed: Control Panel -> System -> Advanced system settings -> Environment Variables. Add Python install path (e.g., `C:\Users\YourUser\AppData\Local\Programs\Python\Python3X`) and Scripts path (e.g., `C:\Users\YourUser\AppData\Local\Programs\Python\Python3X\Scripts`) to the Path variable. -->

### Issue: `ModuleNotFoundError: No module named 'venv'` (when trying `python -m venv .venv`)

- **Cause**: The `python3-venv` package (or equivalent) might be missing on some Linux distributions.
- **Solution**:
    - **Linux (Debian/Ubuntu)**: `sudo apt install python3-venv`
    - <!-- TODO: Add commands for other Linux distributions if necessary. -->

### Issue: `pip install` fails with errors (e.g., compiler errors for packages like `numpy`, `scipy`)

- **Cause**: Some Python packages with C extensions require system-level build tools or development libraries.
- **Solution**:
    - **Linux (Debian/Ubuntu)**: `sudo apt install python3-dev build-essential`
    - <!-- TODO: Add commands for other Linux distributions (e.g., `python3-devel gcc` for Fedora/CentOS). -->
    - **macOS**: Ensure Xcode Command Line Tools are installed: `xcode-select --install`
    - **Windows**: 
        - <!-- TODO: This can be complex. Suggest installing pre-compiled wheels if available. Mention Microsoft C++ Build Tools might be needed from Visual Studio Installer. Link to relevant guides if possible. -->
        - Often, using `conda` via Anaconda/Miniconda can simplify installing such packages on Windows as it provides pre-compiled versions.

### Issue: `ModuleNotFoundError` for a package listed in `requirements.txt` (e.g., `kit`, `dotenv`)

- **Cause**: Virtual environment not activated, or `pip install -r requirements.txt` was not run or failed.
- **Solution**: 
    1. Ensure virtual environment is active.
    2. Run `pip install -r requirements.txt` again and check for errors during installation.
    3. Run `python environment_setup/env_checker.py`.

## 3. `.env` File and API Key Issues

### Issue: Script complains API key is missing, but it's in `.env`

- **Cause**:
    - `.env` file is not in the correct location (should be project root).
    - `dotenv.load_dotenv()` was not called, or the script couldn't find the `.env` file.
    - Typo in the API key name within `.env` or in the script accessing `os.getenv("API_KEY_NAME")`.
- **Solution**:
    - Verify `.env` is in the project root (e.g., `codomyrmex/.env`).
    - Ensure `check_and_setup_env_vars(project_root)` is called early in scripts that need it (if not using `env_checker.py` directly).
    - Double-check key names for typos (e.g., `OPENAI_API_KEY`).
    - Ensure no extra quotes or spaces around keys/values in the `.env` file unless intentional.

## 4. Node.js / Docusaurus Setup Issues (for `documentation` module)

### Issue: `npm` or `node` command not found

- **Cause**: Node.js is not installed, or its installation directory is not in the system PATH.
- **Solution**:
    - <!-- TODO: Provide link to Node.js official download page (nodejs.org). Recommend LTS version. -->
    - **Linux**: 
        - <!-- TODO: Instructions for installing Node.js via package manager (e.g., `sudo apt install nodejs npm`) or using Node Version Manager (nvm). -->
    - **macOS**: 
        - <!-- TODO: Install via installer from nodejs.org or Homebrew (`brew install node`). -->
    - **Windows**: 
        - <!-- TODO: Install via installer from nodejs.org. Ensure it adds to PATH. -->

### Issue: `npm install` fails in `documentation/` directory

- **Cause**: Network issues, outdated npm/Node.js, permission problems, or corrupted `package-lock.json`.
- **Solution**:
    - Check internet connection.
    - Ensure Node.js and npm are reasonably up-to-date (`node -v`, `npm -v`).
    - Try removing `documentation/node_modules` and `documentation/package-lock.json` (or `yarn.lock`) and run `npm install` again.
    - <!-- TODO: Mention potential proxy issues if applicable in a corporate environment. -->
    - Check for specific error messages from npm.

## 5. Git Setup Issues

### Issue: `git` command not found

- **Cause**: Git is not installed or not in PATH.
- **Solution**:
    - <!-- TODO: Provide link to official Git download page (git-scm.com). -->
    - **Linux**: `sudo apt install git` (or equivalent for your distribution).
    - **macOS**: Often comes with Xcode Command Line Tools. If not, `brew install git`.
    - **Windows**: Download and run the installer from git-scm.com. Ensure it adds Git to PATH (usually an option during install).

<!-- TODO: Add sections for other common tools if they become problematic, e.g., Graphviz installation details for different OS. -->

## 6. OS-Specific Path Issues

- **Windows Path Length Limit**: 
    - <!-- TODO: Briefly explain the 260-character path limit on older Windows versions and how it can affect deeply nested Node.js projects or Python paths. Mention enabling long path support via Group Policy or registry edit if relevant and provide links to Microsoft documentation. -->
- **Case Sensitivity**: 
    - <!-- TODO: Remind users that Linux/macOS file systems are typically case-sensitive, while Windows is case-insensitive by default. This can lead to issues if, e.g., an import `from MyModule` works on Windows but fails on Linux if the directory is `mymodule`. Stress consistent naming. -->

## 7. Contact / Further Help

<!-- TODO: Specify where users should ask for help if these troubleshooting steps don't resolve their issue (e.g., a specific Slack channel, GitHub Discussions for the project, or point to project maintainers). -->

If you continue to experience issues after consulting this guide and the module READMEs, please [Specify Channel for Help, e.g., reach out on the project's GitHub Discussions page]. 