#!/bin/bash
# Codomyrmex Project - Development Environment Setup Script

# This script helps automate the initial setup of the Codomyrmex development environment.
# It should be run from the root of the Codomyrmex project directory.

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
PYTHON_VERSION_MAJOR=3
PYTHON_VERSION_MINOR=9
VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"
ENV_CHECKER_SCRIPT="environment_setup/env_checker.py"

# --- Helper Functions ---
echo_info() {
    echo "[INFO] $1"
}

echo_warn() {
    echo "[WARN] $1"
}

echo_error() {
    echo "[ERROR] $1"
    exit 1
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo_error "$1 command not found. Please install $1 and ensure it's in your PATH."
    fi
}

check_python_version() {
    echo_info "Checking Python version..."
    if ! python_cmd=$(command -v python3 || command -v python); then
        echo_error "Python not found. Please install Python ${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR} or higher."
    fi

    # Get major and minor version numbers
    version_output=$($python_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    major=$(echo "$version_output" | cut -d. -f1)
    minor=$(echo "$version_output" | cut -d. -f2)

    if [ "$major" -lt "$PYTHON_VERSION_MAJOR" ] || ([ "$major" -eq "$PYTHON_VERSION_MAJOR" ] && [ "$minor" -lt "$PYTHON_VERSION_MINOR" ]); then
        echo_error "Python version $major.$minor is installed. Codomyrmex requires Python ${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR} or higher."
    fi
    echo_info "Python version $major.$minor found ($python_cmd). Looks good."
    # Export the python command found to be used later
    export PYTHON_CMD="$python_cmd"
}


# --- Main Setup Logic ---

echo_info "Starting Codomyrmex Development Environment Setup..."

# 0. Check for essential commands
check_command "git"
check_python_version # This also sets PYTHON_CMD

# 1. Ensure we are in the project root (rudimentary check)
if [ ! -f "$REQUIREMENTS_FILE" ] || [ ! -d "environment_setup" ]; then
    echo_error "This script must be run from the root directory of the Codomyrmex project."
fi
echo_info "Running in project root: $(pwd)"

# 2. Create Python Virtual Environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo_info "Creating Python virtual environment in '$VENV_DIR'..."
    "$PYTHON_CMD" -m venv "$VENV_DIR"
    echo_info "Virtual environment created."
else
    echo_info "Virtual environment '$VENV_DIR' already exists."
fi

# 3. Activate Virtual Environment (Instruction for user)
echo_info "--------------------------------------------------------------------"
echo_info "IMPORTANT: Activate the virtual environment in your CURRENT shell session."
echo_info "Run one of the following commands:"
echo_info "  source $VENV_DIR/bin/activate  (for Bash/Zsh on Linux/macOS)"
echo_info "  .\$VENV_DIR\Scripts\activate   (for PowerShell on Windows)"
echo_info "  $VENV_DIR\Scripts\activate.bat (for CMD on Windows)"
echo_info "After activation, re-run this script if needed, or proceed manually."
echo_info "--------------------------------------------------------------------"

# Check if already in an active venv related to the project
if [ -z "$VIRTUAL_ENV" ] || [ "$(basename "$VIRTUAL_ENV")" != "$VENV_DIR" ]; then
    echo_warn "Virtual environment is not active or is not '$VENV_DIR'. Please activate it as instructed above and re-run if installation steps fail."
    # No exit here, allow to proceed if user wants to install globally or has it activated in a way script can't detect
fi


# 4. Install/Update Python Dependencies
echo_info "Installing/Updating Python dependencies from '$REQUIREMENTS_FILE'..."
if [ -f "$VENV_DIR/bin/pip" ]; then
    "$VENV_DIR/bin/pip" install -r "$REQUIREMENTS_FILE"
elif [ -f "$VENV_DIR/Scripts/pip.exe" ]; then
    "$VENV_DIR/Scripts/pip.exe" install -r "$REQUIREMENTS_FILE"
else
    # Fallback if pip path in venv is not standard or venv not active
    echo_warn "Could not find pip in the virtual environment. Attempting to use 'pip' command."
    echo_warn "Ensure your virtual environment is active for correct package installation."
    check_command "pip"
    pip install -r "$REQUIREMENTS_FILE"
fi
echo_info "Python dependencies installation attempt complete."

# 5. Run Environment Checker Script
if [ -f "$ENV_CHECKER_SCRIPT" ]; then
    echo_info "Running environment checker script: '$ENV_CHECKER_SCRIPT'..."
    if [ -f "$VENV_DIR/bin/python" ]; then
        "$VENV_DIR/bin/python" "$ENV_CHECKER_SCRIPT"
    elif [ -f "$VENV_DIR/Scripts/python.exe" ]; then
        "$VENV_DIR/Scripts/python.exe" "$ENV_CHECKER_SCRIPT"
    else
        # Fallback if python path in venv is not standard or venv not active
        echo_warn "Could not find python in the virtual environment. Attempting to use '$PYTHON_CMD' command."
        "$PYTHON_CMD" "$ENV_CHECKER_SCRIPT"
    fi
    echo_info "Environment checker script finished."
else
    echo_warn "Environment checker script '$ENV_CHECKER_SCRIPT' not found. Skipping."
fi

# 6. Node.js and Docusaurus (Informational)
echo_info "--------------------------------------------------------------------"
echo_info "For Documentation Development (Docusaurus):"
echo_info "The 'documentation' module uses Node.js and Docusaurus."
echo_info "If you plan to work on documentation, ensure Node.js (v18+) and npm/yarn are installed."
echo_info "Then, navigate to the 'documentation' directory and run 'npm install' or 'yarn install'."
echo_info "See 'documentation/README.md' for more details."
echo_info "--------------------------------------------------------------------"


echo_info "Codomyrmex Development Environment Setup Script finished."
echo_info "Remember to activate your virtual environment ('source $VENV_DIR/bin/activate' or equivalent) if you haven't already." 