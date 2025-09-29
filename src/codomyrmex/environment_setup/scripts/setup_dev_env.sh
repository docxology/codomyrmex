#!/bin/bash
# Codomyrmex Project - Development Environment Setup Script

# This script helps automate the initial setup of the Codomyrmex development environment.
# It should be run from the root of the Codomyrmex project directory.

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
PYTHON_VERSION_MAJOR=3
PYTHON_VERSION_MINOR=10
VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"
PYPROJECT_FILE="pyproject.toml"
ENV_CHECKER_SCRIPT="src/codomyrmex/environment_setup/env_checker.py"

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

check_uv() {
    if command -v "uv" &> /dev/null; then
        echo_info "uv is available on your system."
        return 0
    fi
    echo_error "uv is required for this setup. Install it from https://github.com/astral-sh/uv and re-run the script."
}

setup_uv_environment() {
    echo_info "Setting up environment using uv..."

    # Create uv virtual environment
    if [ ! -d "$VENV_DIR" ]; then
        echo_info "Creating uv virtual environment in '$VENV_DIR'..."
        uv venv "$VENV_DIR"
        echo_info "uv virtual environment created."
    else
        echo_info "uv virtual environment '$VENV_DIR' already exists."
    fi

    # Activate uv environment
    echo_info "Activating uv virtual environment..."
    source "$VENV_DIR/bin/activate"

    # Check if activation worked
    if [ -z "$VIRTUAL_ENV" ]; then
        echo_warn "Virtual environment activation failed. Please activate manually and re-run if installation steps fail."
    fi

    # Install dependencies using uv
    echo_info "Installing/Updating Python dependencies using uv..."
    if [ -f "$PYPROJECT_FILE" ]; then
        uv pip install -e .
    elif [ -f "$REQUIREMENTS_FILE" ]; then
        echo_warn "pyproject.toml not found. Installing from $REQUIREMENTS_FILE via uv."
        uv pip install -r "$REQUIREMENTS_FILE"
    else
        echo_error "Neither pyproject.toml nor requirements.txt found."
    fi
    echo_info "Python dependencies installation attempt complete."
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

# Ensure uv is available
check_uv
echo_info "Using uv for environment setup..."

# 1. Ensure we are in the project root (rudimentary check)
if ([ ! -f "$REQUIREMENTS_FILE" ] && [ ! -f "$PYPROJECT_FILE" ]) || [ ! -d "src/codomyrmex/environment_setup" ]; then
    echo_error "This script must be run from the root directory of the Codomyrmex project."
fi
echo_info "Running in project root: $(pwd)"

# 2. Setup Python Environment
setup_uv_environment

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
if [ -n "$VIRTUAL_ENV" ]; then
    echo_info "Virtual environment is active and ready to use!"
else
    echo_info "Note: Virtual environment may need manual activation in new shell sessions."
fi 