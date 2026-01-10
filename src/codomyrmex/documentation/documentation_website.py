import argparse
import glob
import logging
import os
import shutil  # For checking if command exists
import subprocess
import sys

from documentation_website import FunctionName, ClassName
import webbrowser

from codomyrmex.logging_monitoring import get_logger, setup_logging











































# Standard logging import kept for compatibility with basicConfig structure

# --- Determine project structure and add appropriate path to sys.path for package import ---

"""Main entry point and utility functions

This module provides documentation_website functionality including checks for
environment, verifying dependencies, and managing the documentation lifecycle.
"""
_codomyrmex_dir_for_import_msg = "Unknown"
_path_added_for_import_msg = "Unknown"

try:
    # Assumes __file__ is defined (standard for scripts)
    # SCRIPT_DIR is the directory containing this script (e.g., .../codomyrmex/src/codomyrmex/documentation/)
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    # CODOMYRMEX_DIR is the root of the 'codomyrmex' package (e.g., .../codomyrmex/src/)
    CODOMYRMEX_SRC_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
    # To import 'from codomyrmex.something import ...', the src directory needs to be in sys.path
    PATH_TO_ADD_FOR_MODULE_IMPORT = CODOMYRMEX_SRC_DIR
except NameError:
    # Fallback if __file__ is not defined (e.g., interactive execution)
    # Assume CWD is the script's directory: .../codomyrmex/src/codomyrmex/documentation/
    SCRIPT_DIR = os.getcwd()
    CODOMYRMEX_SRC_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
    PATH_TO_ADD_FOR_MODULE_IMPORT = CODOMYRMEX_SRC_DIR

_codomyrmex_dir_for_import_msg = CODOMYRMEX_SRC_DIR
_path_added_for_import_msg = PATH_TO_ADD_FOR_MODULE_IMPORT

if PATH_TO_ADD_FOR_MODULE_IMPORT not in sys.path:
    pass
#     sys.path.insert(0, PATH_TO_ADD_FOR_MODULE_IMPORT)  # Removed sys.path manipulation
# --- End sys.path modification ---

# Global logger variable, to be initialized by custom or fallback logging
logger = None

try:

    # Call setup_logging() which reads .env from the project root and configures handlers.
    # This should be called once, early in the application.
    # setup_logging() itself calls load_dotenv() which should find the .env file
    # in CODOMYRMEX_DIR if this script is run from SCRIPT_DIR.
    setup_logging()
    logger = get_logger(
        __name__
    )  # Use __name__ which will be '__main__' if script is run directly
    logger.info(
        "Codomyrmex centralized logging initialized successfully via documentation_website.py."
    )
except ImportError as e_import:
    # Fallback if the custom logging module cannot be imported
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s (fallback due to import error)",
        handlers=[logging.StreamHandler(sys.stdout)],  # Ensure logs go to stdout
    )
    logger = logging.getLogger(__name__)
    logger.warning(
        f"Could not import 'codomyrmex.logging_monitoring' (Error: {e_import}). "
        f"Attempted to add parent of CODOMYRMEX_DIR ('{_path_added_for_import_msg}') to sys.path. "
        f"Identified CODOMYRMEX_DIR as '{_codomyrmex_dir_for_import_msg}'. "
        f"Relevant sys.path entries (first 3): {sys.path[:3]}. "
        "This might indicate a missing '__init__.py' in the 'codomyrmex' directory or its parent not being the correct path. "
        "Using basic Python logging as a fallback."
    )
except Exception as e_setup:
    # Fallback if importing works but setup_logging() itself fails
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s (fallback due to setup error)",
        handlers=[logging.StreamHandler(sys.stdout)],  # Ensure logs go to stdout
    )
    logger = logging.getLogger(__name__)
    logger.error(
        f"Error occurred during setup_logging from 'codomyrmex.logging_monitoring' (Error: {e_setup}). "
        "Using basic Python logging as a fallback."
    )

# Final check to ensure logger is always minimally configured (should not be strictly necessary if above logic is sound)
if logger is None:
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s (critical fallback - logger was None)",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger = logging.getLogger(__name__)
    logger.critical(
        "Logger was not initialized by custom or primary fallback setups. Using emergency basic configuration."
    )

# All subsequent logging in this script should use the 'logger' instance.
# For example: logger.info("Starting script operations...")
# Make sure to replace any direct calls to logging.info, print() used for logging, etc.,
# with logger.info, logger.warning, etc. throughout the rest of this file.

# Script's directory is 'documentation/'
DOCUSAURUS_ROOT_DIR = SCRIPT_DIR  # This script is inside the Docusaurus root

DEFAULT_DOCS_PORT = 3000
DOCUSAURUS_BASE_PATH = "/codomyrmex/"  # Standard Docusaurus baseUrl, ensure trailing slash if needed by join

# Construct the effective URL by joining, ensuring no double slashes if base_path is / or empty
_base_url_for_construction = f"http://localhost:{DEFAULT_DOCS_PORT}"
_docs_base_path_for_construction = DOCUSAURUS_BASE_PATH.strip("/")

if _docs_base_path_for_construction:  # if base path is not empty or just "/"
    EFFECTIVE_DOCS_URL = (
        f"{_base_url_for_construction}/{_docs_base_path_for_construction}/"
    )
else:
    EFFECTIVE_DOCS_URL = f"{_base_url_for_construction}/"

DEFAULT_ACTION = "full_cycle"  # New default action


def command_exists(command):
    """Check if a command exists on PATH."""
    return shutil.which(command) is not None


def check_doc_environment():
    """Checks for Node.js and npm/yarn."""
    logger.info("Checking documentation development environment...")
    node_ok = command_exists("node")
    npm_ok = command_exists("npm")
    yarn_ok = command_exists("yarn")

    if not node_ok:
        logger.error("Node.js not found. Please install Node.js (v18+ recommended).")
        logger.error("See: https://nodejs.org/")
        return False
    logger.info("Node.js found.")

    if not (npm_ok or yarn_ok):
        logger.error(
            "Neither npm nor yarn found. Please install npm (comes with Node.js) or yarn."
        )
        logger.error("npm: https://www.npmjs.com/get-npm")
        logger.error("Yarn: https://classic.yarnpkg.com/en/docs/install")
        return False

    if npm_ok:
        logger.info("npm found.")
    else:
        logger.warning(
            "npm not found. Some operations might require it if yarn is not preferred/available."
        )

    if yarn_ok:
        logger.info("Yarn found.")
    else:
        logger.warning("Yarn not found. Operations will default to npm if available.")

    logger.info(
        "Basic documentation environment check passed (Node.js and at least one package manager)."
    )
    return True


def run_command_stream_output(command_parts, cwd):
    """
    Helper to run a shell command and stream its output to the logger.
    Returns True if successful, False otherwise.
    """
    try:
        logger.info(f"Running command: {' '.join(command_parts)} in {cwd}")
        process = subprocess.Popen(
            command_parts,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                logger.info(line.strip())

        process.wait()

        if process.returncode == 0:
            logger.info(f"Command '{' '.join(command_parts)}' executed successfully.")
            return True
        else:
            logger.error(
                f"Command '{' '.join(command_parts)}' failed with return code {process.returncode}."
            )
            return False
    except FileNotFoundError:
        logger.error(
            f"Error: Command '{command_parts[0]}' not found. Is it installed and in PATH?"
        )
        return False
    except Exception as e:
        logger.error(
            f"An error occurred while running '{' '.join(command_parts)}': {e}"
        )
        return False


def install_dependencies(package_manager="npm"):
    """Installs Docusaurus dependencies."""
    logger.info(f"Attempting to install dependencies using {package_manager}...")
    if package_manager == "yarn" and command_exists("yarn"):
        cmd = ["yarn", "install"]
    elif command_exists("npm"):
        cmd = ["npm", "install"]
        if package_manager == "yarn":
            logger.warning("Yarn specified but not found, falling back to npm.")
    else:
        logger.error("Neither npm nor yarn found. Cannot install dependencies.")
        return False

    return run_command_stream_output(cmd, DOCUSAURUS_ROOT_DIR)


def start_dev_server(package_manager="npm"):
    """Starts the Docusaurus development server (hot-reloading)."""
    logger.info(f"Attempting to start development server using {package_manager}...")
    logger.info(
        f"Docusaurus site should be available at {EFFECTIVE_DOCS_URL} once started."
    )
    logger.info("This command will run until you stop it (Ctrl+C).")

    if package_manager == "yarn" and command_exists("yarn"):
        cmd = ["yarn", "start"]
    elif command_exists("npm"):
        cmd = ["npm", "run", "start"]
        if package_manager == "yarn":
            logger.warning("Yarn specified but not found, falling back to npm.")
    else:
        logger.error("Neither npm nor yarn found. Cannot start server.")
        return False

    try:
        logger.info(f"Running command: {' '.join(cmd)} in {DOCUSAURUS_ROOT_DIR}")
        logger.info(
            f"Try opening your browser at {EFFECTIVE_DOCS_URL} if it doesn't open automatically."
        )
        subprocess.run(cmd, cwd=DOCUSAURUS_ROOT_DIR, check=False)
        logger.info("Development server process finished or was stopped.")
        return True
    except FileNotFoundError:
        logger.error(
            f"Error: Command '{cmd[0]}' not found. Is it installed and in PATH?"
        )
        return False
    except KeyboardInterrupt:
        logger.info("Development server process interrupted by user (Ctrl+C).")
        return True
    except Exception as e:
        logger.error(f"An error occurred while trying to start the dev server: {e}")
        return False


def build_static_site(package_manager="npm"):
    """Builds the static Docusaurus site."""
    logger.info(f"Attempting to build static site using {package_manager}...")
    if package_manager == "yarn" and command_exists("yarn"):
        cmd = ["yarn", "build"]
    elif command_exists("npm"):
        cmd = ["npm", "run", "build"]
        if package_manager == "yarn":
            logger.warning("Yarn specified but not found, falling back to npm.")
    else:
        logger.error("Neither npm nor yarn found. Cannot build site.")
        return False

    success = run_command_stream_output(cmd, DOCUSAURUS_ROOT_DIR)
    if success:
        logger.info(
            f"Static site built successfully in '{os.path.join(DOCUSAURUS_ROOT_DIR, 'build')}'"
        )
    return success


def serve_static_site(package_manager="npm"):
    """Serves the built static Docusaurus site."""
    logger.info(f"Attempting to serve the built static site using {package_manager}...")
    build_dir = os.path.join(DOCUSAURUS_ROOT_DIR, "build")
    if not os.path.exists(build_dir) or not os.listdir(build_dir):
        logger.error(
            f"Build directory '{build_dir}' does not exist or is empty. Please build the site first using the 'build' action."
        )
        return False

    logger.info(
        f"Site will be served from '{build_dir}' and should be available at {EFFECTIVE_DOCS_URL}."
    )
    logger.info("This command will run until you stop it (Ctrl+C).")

    # Docusaurus `serve` command should be run from the Docusaurus root directory.
    if package_manager == "yarn" and command_exists("yarn"):
        # `yarn docusaurus serve` is the typical command
        cmd = ["yarn", "docusaurus", "serve"]
    elif command_exists("npm"):
        # `npx docusaurus serve` is the typical command for npm
        # Ensure npx is available or handle if not. `npm exec` is an alternative for npm v7+
        if command_exists("npx"):
            cmd = ["npx", "docusaurus", "serve"]
        elif command_exists(
            "npm"
        ):  # Fallback to `npm exec` if npx not found, for npm v7+
            logger.info(
                "npx not found, trying 'npm exec docusaurus serve'. Requires npm v7+."
            )
            cmd = ["npm", "exec", "--", "docusaurus", "serve"]
        else:  # Should not happen if npm was found by check_doc_environment and install_dependencies
            logger.error(
                "npm found, but npx not found and 'npm exec' attempt might also fail. Cannot determine serve command."
            )
            return False

        if (
            package_manager == "yarn"
        ):  # This warning is if yarn was preferred but npm is used
            logger.warning(
                "Yarn specified but not found or serve command unclear, falling back to npm/npx for serving."
            )
    else:
        logger.error(
            "Neither npm nor yarn found, or cannot determine serve command. Cannot serve site."
        )
        return False

    try:
        logger.info(f"Running command: {' '.join(cmd)} in {DOCUSAURUS_ROOT_DIR}")
        logger.info(
            f"Try opening your browser at {EFFECTIVE_DOCS_URL} if it doesn't open automatically."
        )
        subprocess.run(cmd, cwd=DOCUSAURUS_ROOT_DIR, check=False)
        logger.info("Static site server process finished or was stopped.")
        return True
    except FileNotFoundError:
        logger.error(
            "Error: Command for serving (e.g., 'npx', 'yarn', or 'docusaurus') not found. Is Docusaurus installed and in PATH?"
        )
        return False
    except KeyboardInterrupt:
        logger.info("Static site server process interrupted by user (Ctrl+C).")
        return True
    except Exception as e:
        logger.error(f"An error occurred while trying to serve the static site: {e}")
        return False


def print_assessment_checklist():
    """Prints a checklist for manually assessing the documentation website."""
    print("\n--- Documentation Website Assessment Checklist ---")
    checklist = [
        "Overall Navigation: Check main navbar and sidebar. Are all modules present and clickable?",
        "Content Rendering: Verify Markdown rendering (headings, lists, code blocks, tables).",
        "Content Accuracy: Read through content. Is it up-to-date and correct?",
        "Internal Links: Test all internal links within pages and between pages/modules.",
        "External Links: Verify any external links lead to correct destinations.",
        "Code Blocks: Ensure code examples are correctly formatted and highlighted.",
        "Look and Feel: Check overall appearance. Is it responsive on different screen sizes?",
        "Console Errors: Open browser developer tools (F12) and check for JavaScript console errors.",
    ]
    for item in checklist:
        print(f"- [ ] {item}")
    print("--- End of Checklist ---")


def aggregate_docs(source_root: str = None, dest_root: str = None):
    """Aggregate module documentation into the Docusaurus docs/modules folder.

    This copies canonical documentation files from each src/codomyrmex/<module>/ directory into
    documentation/docs/modules/<module>/ so the Docusaurus site can present a unified view.

    By default, it scans the project `src/codomyrmex/` directory and copies recognized
    documentation files and the `docs/` subfolder contents.
    """
    logger.info("Starting documentation aggregation process...")

    project_root = os.path.abspath(os.path.join(DOCUSAURUS_ROOT_DIR, "..", "..", ".."))
    source_root = source_root or os.path.join(project_root, "src", "codomyrmex")
    dest_root = dest_root or os.path.join(DOCUSAURUS_ROOT_DIR, "docs", "modules")

    logger.info(f"Source docs root: {source_root}")
    logger.info(f"Destination docs root: {dest_root}")

    os.makedirs(dest_root, exist_ok=True)

    # Recognized top-level module doc filenames to copy
    top_level_files = [
        "README.md",
        "API_SPECIFICATION.md",
        "MCP_TOOL_SPECIFICATION.md",
        "USAGE_EXAMPLES.md",
        "CHANGELOG.md",
        "SECURITY.md",
    ]

    for module_path in sorted(glob.glob(os.path.join(source_root, "*"))):
        if not os.path.isdir(module_path):
            continue
        module_name = os.path.basename(module_path)

        # Skip the documentation module to avoid recursive copying
        if module_name == "documentation":
            continue

        dest_module_dir = os.path.join(dest_root, module_name)
        # Create destination module dir
        os.makedirs(dest_module_dir, exist_ok=True)

        # Copy top-level recognized files
        for fname in top_level_files:
            src = os.path.join(module_path, fname)
            if os.path.exists(src):
                try:
                    # Convert filename to lowercase for consistency with Docusaurus
                    dest_fname = fname.lower()
                    dest_path = os.path.join(dest_module_dir, dest_fname)
                    shutil.copy2(src, dest_path)
                    logger.info(f"Copied {src} -> {dest_path}")
                except Exception as e:
                    logger.error(f"Failed to copy {src} -> {dest_module_dir}: {e}")

        # Copy module docs/ subtree if present
        src_docs_dir = os.path.join(module_path, "docs")
        if os.path.exists(src_docs_dir) and os.path.isdir(src_docs_dir):
            # Destination docs subfolder
            dest_docs_subdir = os.path.join(dest_module_dir, "docs")
            # Remove existing dest subtree to avoid stale files
            if os.path.exists(dest_docs_subdir):
                try:
                    shutil.rmtree(dest_docs_subdir)
                except Exception as e:
                    logger.warning(
                        f"Could not remove existing docs at {dest_docs_subdir}: {e}"
                    )
            try:
                shutil.copytree(src_docs_dir, dest_docs_subdir)
                logger.info(f"Copied docs tree {src_docs_dir} -> {dest_docs_subdir}")
            except Exception as e:
                logger.error(
                    f"Failed to copy docs tree {src_docs_dir} -> {dest_docs_subdir}: {e}"
                )

    logger.info(
        "Documentation aggregation complete. Please review 'documentation/docs/modules' for results."
    )


def validate_doc_versions():
    """Validate version consistency between source and aggregated documentation."""
    logger.info("Starting documentation version validation...")

    project_root = os.path.abspath(os.path.join(DOCUSAURUS_ROOT_DIR, "..", "..", ".."))
    source_root = os.path.join(project_root, "src", "codomyrmex")
    dest_root = os.path.join(DOCUSAURUS_ROOT_DIR, "docs", "modules")

    validation_errors = []
    validation_warnings = []

    for module_path in sorted(glob.glob(os.path.join(source_root, "*"))):
        if not os.path.isdir(module_path):
            continue
        module_name = os.path.basename(module_path)
        dest_module_dir = os.path.join(dest_root, module_name)

        # Check if aggregated docs exist
        if not os.path.exists(dest_module_dir):
            validation_warnings.append(
                f"Module {module_name}: No aggregated documentation found"
            )
            continue

        # Compare CHANGELOG.md versions
        src_changelog = os.path.join(module_path, "CHANGELOG.md")
        dest_changelog = os.path.join(dest_module_dir, "CHANGELOG.md")

        if os.path.exists(src_changelog) and os.path.exists(dest_changelog):
            try:
                with open(src_changelog) as f:
                    src_content = f.read()
                with open(dest_changelog) as f:
                    dest_content = f.read()

                if src_content != dest_content:
                    validation_errors.append(
                        f"Module {module_name}: CHANGELOG.md differs between source and aggregated docs"
                    )
            except Exception as e:
                validation_errors.append(
                    f"Module {module_name}: Error comparing CHANGELOG.md: {e}"
                )

        # Check file modification times
        for fname in ["README.md", "API_SPECIFICATION.md", "MCP_TOOL_SPECIFICATION.md"]:
            src_file = os.path.join(module_path, fname)
            dest_file = os.path.join(dest_module_dir, fname)

            if os.path.exists(src_file) and os.path.exists(dest_file):
                src_mtime = os.path.getmtime(src_file)
                dest_mtime = os.path.getmtime(dest_file)

                if src_mtime > dest_mtime:
                    validation_warnings.append(
                        f"Module {module_name}: {fname} is newer in source than aggregated docs"
                    )

    if validation_errors:
        logger.error("Version validation found errors:")
        for error in validation_errors:
            logger.error(f"  - {error}")
    else:
        logger.info("No version validation errors found")

    if validation_warnings:
        logger.warning("Version validation found warnings:")
        for warning in validation_warnings:
            logger.warning(f"  - {warning}")
    else:
        logger.info("No version validation warnings found")

    return len(validation_errors) == 0, validation_errors, validation_warnings


def assess_site():
    """Guides user through assessing the site by opening browser and printing checklist."""
    logger.info(f"Attempting to open {EFFECTIVE_DOCS_URL} in your web browser.")
    logger.info(
        "Ensure a local server (dev or static) is running and accessible at this URL."
    )
    try:
        if not webbrowser.open(EFFECTIVE_DOCS_URL):
            logger.warning(
                f"webbrowser.open() returned False. Could not open {EFFECTIVE_DOCS_URL} automatically."
            )
            logger.info(f"Please open manually: {EFFECTIVE_DOCS_URL}")
    except Exception as e:
        logger.warning(
            f"Could not open web browser automatically: {e}. Please open manually: {EFFECTIVE_DOCS_URL}"
        )

    print_assessment_checklist()


def main():
    
    parser = argparse.ArgumentParser(
        description=(
            "Manage and assess the Codomyrmex documentation website. "
            "This script should be run from the 'documentation' directory, "
            "or ensure 'codomyrmex' project root is in PYTHONPATH for full logging features. "
            f"If no action is specified, it defaults to '{DEFAULT_ACTION}'."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "action",
        nargs="?",
        default=DEFAULT_ACTION,
        choices=[
            "checkenv",
            "install",
            "start",
            "build",
            "serve",
            "assess",
            "aggregate_docs",
            "validate_docs",
            DEFAULT_ACTION,
        ],
        help=(
            "Action to perform:\n"
            "'checkenv'   Check Node.js/npm/yarn.\n"
            "'install'    Install Docusaurus dependencies.\n"
            "'start'      Run the Docusaurus development server (hot-reloading).\n"
            "'build'      Build the static Docusaurus site to the 'build/' directory.\n"
            "'serve'      Serve the statically built site from 'build/'.\n"
            "'assess'     Open browser to site and print assessment checklist.\n"
            "'aggregate_docs' Aggregate module documentation into 'docs/modules'.\n"
            "'validate_docs' Validate version consistency between source and aggregated docs.\n"
            f"'{DEFAULT_ACTION}' (Default) Perform: checkenv -> install -> build -> assess -> serve."
        ),
    )
    parser.add_argument(
        "--pm",
        choices=["npm", "yarn"],
        default="npm",
        help="Package manager to use (npm or yarn). Default: npm.",
    )

    args = parser.parse_args()

    action_to_perform = args.action

    if action_to_perform == "checkenv":
        check_doc_environment()
    elif action_to_perform == "install":
        if check_doc_environment():
            install_dependencies(args.pm)
    elif action_to_perform == "start":
        if check_doc_environment():
            start_dev_server(args.pm)
    elif action_to_perform == "build":
        if check_doc_environment():
            install_dependencies(args.pm)  # Ensure deps are there before build
            build_static_site(args.pm)
    elif action_to_perform == "serve":
        # For 'serve', we assume build is done. We don't re-check env or install.
        serve_static_site(args.pm)
        assess_site()  # Assess after starting the server
    elif action_to_perform == "assess":
        assess_site()
    elif action_to_perform == "aggregate_docs":
        aggregate_docs()
    elif action_to_perform == "validate_docs":
        is_valid, errors, warnings = validate_doc_versions()
        if not is_valid:
            logger.error("Documentation validation failed!")
            sys.exit(1)
    elif action_to_perform == DEFAULT_ACTION:
        logger.info(f"--- Starting '{DEFAULT_ACTION}' sequence ---")
        if not check_doc_environment():
            logger.error(f"Environment check failed. Aborting '{DEFAULT_ACTION}'.")
            sys.exit(1)

        logger.info(f"--- Step 1 ({DEFAULT_ACTION}): Installing dependencies ---")
        if not install_dependencies(args.pm):
            logger.error(
                f"Dependency installation failed. Aborting '{DEFAULT_ACTION}'."
            )
            sys.exit(1)

        logger.info(f"--- Step 2 ({DEFAULT_ACTION}): Building static site ---")
        if not build_static_site(args.pm):
            logger.error(f"Static site build failed. Aborting '{DEFAULT_ACTION}'.")
            sys.exit(1)

        logger.info(f"--- Step 3 ({DEFAULT_ACTION}): Assessing and serving site ---")
        assess_site()  # Open browser and print checklist
        serve_static_site(args.pm)  # Serve the built site (blocking)
        logger.info(
            f"--- '{DEFAULT_ACTION}' sequence potentially finished (server might have been stopped) ---"
        )


if __name__ == "__main__":
    main()
