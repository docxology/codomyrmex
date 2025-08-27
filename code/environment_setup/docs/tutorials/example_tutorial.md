# Environment Setup - Troubleshooting Common Setup Issues

This document provides troubleshooting tips for common environment setup issues encountered while setting up the Codomyrmex project, along with some OS-specific considerations.

This guide is a living document. Please contribute by adding new issues and solutions as they are encountered.

## 1. General Troubleshooting Steps

When you encounter an issue during setup, try these general steps first:

1.  **Read Error Messages Carefully**: Error messages often contain clues about the problem and sometimes suggest solutions.
2.  **Consult `environment_setup/README.md`**: Ensure you've followed all steps in the "General Project Development Environment Setup" section of the module's main README.
3.  **Check `env_checker.py` Output**: Run `python environment_setup/env_checker.py` from the project root. It can pinpoint missing Python dependencies or `.env` file issues.
4.  **Active Virtual Environment**: Ensure your Python virtual environment (e.g., `.venv`) is activated. Your terminal prompt usually indicates this (e.g., `(.venv) your-prompt$`). If not, activate it:
    - Linux/macOS: `source .venv/bin/activate`
    - Windows: `.venv\Scripts\activate`
5.  **Python and Pip Versions**: Verify your Python version (`python --version` or `python3 --version`) and pip version (`pip --version` or `pip3 --version`). Ensure they meet the project prerequisites (Python 3.9+).
6.  **Internet Connection**: Some steps (like `pip install` or `npm install`) require an internet connection to download packages.
7.  **Permissions**: Ensure you have the necessary permissions to install software or create files/directories in the locations required. You might need `sudo` for system-wide package installations on Linux/macOS.

## 2. Common Python Setup Issues

### Issue: `python` or `pip` command not found (or points to Python 2)

- **Cause**: Python 3 is not installed, or its installation directory (and Scripts subdirectory for pip) is not in your system's PATH environment variable, or `python` and `pip` aliases point to an older Python 2 installation.
- **Solution**:
    - **All OS**:
        - Download Python from [python.org](https://www.python.org/downloads/).
        - During installation, ensure to check the option "Add Python to PATH" (or similar).
        - Prefer using `python3` and `pip3` explicitly if `python` and `pip` are ambiguous.
    - **Linux**:
        - Debian/Ubuntu: `sudo apt update && sudo apt install python3 python3-pip python3-venv`
        - Fedora: `sudo dnf install python3 python3-pip python3-virtualenv` (or `python3-venv`)
        - CentOS/RHEL: `sudo yum install python3 python3-pip python3-virtualenv` (may require EPEL repository for older versions)
    - **macOS**:
        - macOS often comes with an older Python 2. Install Python 3 from [python.org](https://www.python.org/downloads/) or using Homebrew: `brew install python`. 
        - Ensure the Homebrew-installed Python is prioritized in PATH (Homebrew usually handles this). Use `python3` and `pip3`.
    - **Windows**:
        - Emphasize checking "Add Python to PATH" during installation from [python.org](https://www.python.org/downloads/).
        - To manually add Python to PATH if missed: Search for "environment variables" -> "Edit the system environment variables" -> Environment Variables button -> Under "System variables", find and select "Path", then click "Edit". Add paths to your Python installation (e.g., `C:\Users\YourUser\AppData\Local\Programs\Python\Python3X`) and its `Scripts` subdirectory (e.g., `C:\Users\YourUser\AppData\Local\Programs\Python\Python3X\Scripts`).

### Issue: `ModuleNotFoundError: No module named 'venv'` (when trying `python3 -m venv .venv`)

- **Cause**: The `python3-venv` package (or equivalent standard library component) might be missing or not installed correctly with your Python distribution.
- **Solution**:
    - **Linux (Debian/Ubuntu)**: `sudo apt install python3-venv`
    - **Linux (Fedora)**: Usually included with `python3` package. If not, `sudo dnf install python3-virtualenv` or ensure core Python dev packages are there.
    - Other OS: This is uncommon if Python 3 was installed correctly from official sources, as `venv` is part of the standard library since Python 3.3. Try reinstalling Python.

### Issue: `pip install` fails with errors (e.g., compiler errors for packages like `numpy`, `scipy`, or other C-extension packages)

- **Cause**: Some Python packages with C extensions require system-level build tools (like a C compiler) or development headers for Python and other libraries.
- **Solution**:
    - **Linux (Debian/Ubuntu)**: `sudo apt install python3-dev build-essential`
    - **Linux (Fedora)**: `sudo dnf install python3-devel gcc make redhat-rpm-config` (or `dnf groupinstall "Development Tools" "C Development Tools and Libraries"`)
    - **macOS**: Ensure Xcode Command Line Tools are installed: `xcode-select --install`. If issues persist, ensure your active developer directory is correct.
    - **Windows**:
        - This can be complex. The easiest solution is often to install pre-compiled wheels if the package provides them for your Python version and architecture. Pip usually tries this by default.
        - If compilation is required, you may need Microsoft C++ Build Tools. Download "Build Tools for Visual Studio" from the [Visual Studio downloads page](https://visualstudio.microsoft.com/downloads/), and during installation, select "C++ build tools" and the latest Windows SDK.
        - For some scientific packages, using Anaconda/Miniconda can simplify installation as Conda manages pre-compiled binaries.

### Issue: `ModuleNotFoundError` for a package listed in `requirements.txt` (e.g., `cased`, `dotenv`)

- **Cause**: Virtual environment not activated, or `pip install -r requirements.txt` was not run, failed silently, or was run in the wrong environment.
- **Solution**:
    1. Ensure your project's virtual environment is active (e.g., `source .venv/bin/activate`).
    2. Run `pip install -r requirements.txt` again from the project root and check for any error messages during installation.
    3. Run `python environment_setup/env_checker.py` from the project root to diagnose.
    4. Check `pip list` to see if the package is listed in the active environment.

## 3. `.env` File and API Key Issues

### Issue: Script complains API key is missing, but it's in `.env`

- **Cause**:
    - `.env` file is not in the correct location (should be project root, e.g., `codomyrmex/.env`).
    - The script calling `dotenv.load_dotenv()` is not doing so correctly, or `check_and_setup_env_vars()` was called with an incorrect `repo_root_path`.
    - Typo in the API key name within the `.env` file (e.g., `OPEN_AI_API_KEY` instead of `OPENAI_API_KEY`).
    - Typo in the script accessing the key via `os.getenv("API_KEY_NAME")`.
    - Extra quotes or spaces around keys/values in the `.env` file: `MY_KEY = " value "` is different from `MY_KEY=value`.
- **Solution**:
    - Verify `.env` is in the project root directory.
    - If using `env_checker.py` functions in your own script, ensure `check_and_setup_env_vars(project_root)` is called early and `project_root` is correctly identified.
    - Double-check key names for exact matches (case-sensitive).
    - Ensure `.env` format is `KEY=VALUE` per line, without extraneous shell commands or Bash-like exports, unless specifically handled by your dotenv library version.

## 4. Node.js / Docusaurus Setup Issues (for `documentation` module)

### Issue: `npm` or `node` command not found

- **Cause**: Node.js is not installed, or its installation directory is not in the system PATH.
- **Solution**:
    - Download Node.js from [nodejs.org](https://nodejs.org/en/download), LTS version is recommended.
    - **Linux**:
        - Using Node Version Manager (nvm) is highly recommended: `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash`, then `nvm install --lts`.
        - Alternatively, for Debian/Ubuntu: `sudo apt update && sudo apt install nodejs npm`. For Fedora: `sudo dnf module install nodejs:<version>/common` (e.g., `nodejs:18/common`).
    - **macOS**: Install via installer from [nodejs.org](https://nodejs.org/en/download) or Homebrew (`brew install node`). Nvm also works on macOS.
    - **Windows**: Install via installer from [nodejs.org](https://nodejs.org/en/download). Ensure it adds Node.js to PATH.

### Issue: `npm install` fails in `documentation/` directory

- **Cause**: Network issues, outdated npm/Node.js, permission problems, corrupted `package-lock.json`, or corporate proxy issues.
- **Solution**:
    - Check internet connection.
    - Ensure Node.js and npm are reasonably up-to-date (`node -v`, `npm -v`). If using nvm, `nvm use --lts`.
    - Try removing `documentation/node_modules` and `documentation/package-lock.json` (or `yarn.lock` if using Yarn) and run `npm install` (or `yarn install`) again.
    - If behind a corporate proxy, configure npm for the proxy: 
      `npm config set proxy http://your_proxy_server_address:port`
      `npm config set https-proxy http://your_proxy_server_address:port`
    - Check for specific error messages from npm, they often provide more clues.
    - On Linux/macOS, permission issues might require `sudo npm install -g some-global-package` for global packages, but for local project installs (`npm install` in `documentation/`), `sudo` should NOT be needed and indicates a problem with directory ownership or permissions.

## 5. Git Setup Issues

### Issue: `git` command not found

- **Cause**: Git is not installed or not in PATH.
- **Solution**:
    - Download from [git-scm.com/downloads](https://git-scm.com/downloads).
    - **Linux**: `sudo apt install git` (Debian/Ubuntu), `sudo dnf install git` (Fedora).
    - **macOS**: Often comes with Xcode Command Line Tools. If not, `xcode-select --install` or `brew install git`.
    - **Windows**: Download and run the installer from [git-scm.com](https://git-scm.com/downloads). Ensure it adds Git to PATH (usually an option like "Git from the command line and also from 3rd-party software").

## 6. Graphviz Installation (Optional, for some visualizations)

- **Issue**: Dependency visualization tools (like `cased kit depgraph`) fail, complaining about Graphviz or `dot` command not found.
- **Solution**: Install Graphviz system package and the Python `graphviz` library.
    - **System Package**:
        - Linux (Debian/Ubuntu): `sudo apt install graphviz`
        - Linux (Fedora): `sudo dnf install graphviz`
        - macOS: `brew install graphviz`
        - Windows: Download installer from [graphviz.org/download/](https://graphviz.org/download/) and ensure the `bin` directory (containing `dot.exe`) is added to PATH.
    - **Python Library** (within your `.venv`):
        - `pip install graphviz` (Ensure this is added to the root `requirements.txt` if it becomes a core project dependency).

## 7. OS-Specific Path Issues

- **Windows Path Length Limit**: 
    - Older Windows versions (pre-Windows 10 Anniversary Update) had a 260-character path limit (MAX_PATH). This can affect deeply nested Node.js projects (`node_modules`) or long Python paths.
    - **Solution**: Enable long path support. On modern Windows 10/11: Search for "Edit group policy" -> Local Computer Policy -> Computer Configuration -> Administrative Templates -> System -> Filesystem -> Enable "Enable Win32 long paths". Or, via Registry Editor: `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled` (set to 1, type DWORD). A reboot might be needed. See [Microsoft Docs on Long Path Support](https://docs.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=registry) for details.
- **Case Sensitivity**: 
    - Linux/macOS file systems are typically case-sensitive by default (e.g., `MyFile.txt` and `myfile.txt` are different).
    - Windows NTFS is case-insensitive but case-preserving (you can create `MyFile.txt` and `myfile.txt` in the same directory if case sensitivity is enabled per-directory, but by default, trying to create the second one might refer to the first).
    - **Impact**: Git can be configured to handle case sensitivity. Issues arise if code has `import MyModule` but the directory is `mymodule/`. This might work on Windows but fail on Linux/macOS.
    - **Solution**: Use consistent, all-lowercase names for modules and filenames where possible. If mixed case is used, ensure it matches exactly in imports and file system paths. Check Git's `core.ignorecase` setting (`git config core.ignorecase`).

## 8. Contact / Further Help

If you continue to experience issues after consulting this guide and the module READMEs:

- **Check Project Issues**: Look for existing issues on the project's GitHub repository that might match your problem.
- **Ask the Team**: If part of a team, consult your colleagues or the project maintainers.
- **Create a New Issue**: If you suspect a bug in Codomyrmex setup scripts or a gap in documentation, please [open an issue on the project's GitHub repository](https://github.com/MAE-NeuroPsych-Lab/codomyrmex/issues) with detailed information about the problem, your OS, steps taken, and full error messages.

Thank you for helping improve the Codomyrmex setup experience! 