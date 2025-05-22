#!/bin/bash
# Codomyrmex Project - Git Hooks Installation Script

# This script helps set up Git hooks for the Codomyrmex project.
# It should be run from the root of the Codomyrmex project directory.

set -e # Exit immediately if a command exits with a non-zero status.

GIT_HOOKS_DIR=".git/hooks"
PROJECT_HOOKS_DIR="scripts/git-hooks"

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

# --- Main Logic ---
echo_info "Starting Git Hooks Installation..."

# 1. Ensure .git directory exists (i.e., we are in a git repo)
if [ ! -d ".git" ]; then
    echo_error "This does not appear to be a Git repository. Please run this script from the root of the Codomyrmex project."
fi

# 2. Create project-specific hooks directory if it doesn't exist
#    (This is where you would store your hook scripts in the repository)
if [ ! -d "$PROJECT_HOOKS_DIR" ]; then
    echo_info "Creating directory for project Git hooks: '$PROJECT_HOOKS_DIR'"
    mkdir -p "$PROJECT_HOOKS_DIR"
    echo_info "Please add your hook scripts (e.g., pre-commit, prepare-commit-msg) to '$PROJECT_HOOKS_DIR' directory."
    echo_info "For now, a sample pre-commit hook will be created."

    # Create a sample pre-commit hook
    cat << 'EOF' > "$PROJECT_HOOKS_DIR/pre-commit"
#!/bin/bash
# Sample pre-commit hook for Codomyrmex

echo "[HOOK] Running pre-commit checks..."

# Example: Run a linter (replace with actual linting commands)
# echo "[HOOK] Linting Python files..."
# pylint **/*.py || exit 1 # Adjust path and command as needed

# Example: Check for "TODO" or "FIXME" comments
# if git diff --cached --name-only | xargs grep -E 'TODO|FIXME'; then
#  echo "[HOOK] Warning: Found TODO/FIXME comments in staged files. Please address them or acknowledge."
# fi

echo "[HOOK] Pre-commit checks passed."
exit 0
EOF
    chmod +x "$PROJECT_HOOKS_DIR/pre-commit"
    echo_info "Sample pre-commit hook created at '$PROJECT_HOOKS_DIR/pre-commit'. Customize it as needed."
fi

# 3. For each hook in our project's hook directory, create a symlink in .git/hooks
#    This allows hooks to be version-controlled with the project.
echo_info "Installing/Updating Git hooks..."

if [ -d "$PROJECT_HOOKS_DIR" ]; then
    for hook_script in "$PROJECT_HOOKS_DIR"/*; do
        if [ -f "$hook_script" ] && [ -x "$hook_script" ]; then
            hook_name=$(basename "$hook_script")
            target_hook_path="$GIT_HOOKS_DIR/$hook_name"

            # Remove existing hook if it's a file or a broken symlink
            if [ -f "$target_hook_path" ] || [ -L "$target_hook_path" ]; then
                rm -f "$target_hook_path"
            fi

            echo_info "Creating symlink for $hook_name hook..."
            # Use relative path for symlink for better portability
            ln -s "../../$PROJECT_HOOKS_DIR/$hook_name" "$target_hook_path"
            echo_info "Hook '$hook_name' installed."
        else
            echo_warn "Skipping '$hook_script' as it is not an executable file."
        fi
    done
else
    echo_warn "Project hooks directory '$PROJECT_HOOKS_DIR' not found. No custom hooks installed."
fi

echo_info "Git Hooks Installation finished."
echo_info "Ensure your hook scripts in '$PROJECT_HOOKS_DIR' are executable (chmod +x <script_name>)." 