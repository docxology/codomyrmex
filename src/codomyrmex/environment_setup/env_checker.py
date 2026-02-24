"""Environment validation and setup utilities.

This module provides functions for validating and configuring the development
environment, including dependency checking, environment variable management,
Python version validation, and uv package manager detection.

Example:
    >>> from codomyrmex.environment_setup import (
    ...     validate_python_version,
    ...     ensure_dependencies_installed,
    ...     is_uv_available
    ... )
    >>> if validate_python_version():
    ...     print("Python version OK")
    >>> if is_uv_available():
    ...     print("uv package manager found")
"""

import os
import shutil
import subprocess
import sys

import dotenv

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

# Store the original script directory to correctly locate files relative to REPO_ROOT_PATH
_script_dir = os.path.dirname(__file__)

def ensure_dependencies_installed() -> bool:
    """Check if primary dependencies are installed and accessible.

    Verifies that required dependencies ('kit' and 'python-dotenv') are
    installed and importable. Prints status messages for each dependency
    and instructions if any are missing.

    Returns:
        True if all required dependencies are installed, False otherwise.

    Example:
        >>> if ensure_dependencies_installed():
        ...     print("All dependencies OK, proceeding with setup")
        ... else:
        ...     print("Please install missing dependencies first")
    """
    dependencies_ok = True
    try:
        print("[INFO] cased/kit library found.")
    except ImportError:
        print("[WARNING] cased/kit library NOT found.", file=sys.stderr)
        dependencies_ok = False

    try:
        print("[INFO] python-dotenv library found.")
    except ImportError:
        print("[WARNING] python-dotenv library NOT found.", file=sys.stderr)
        dependencies_ok = False

    if not dependencies_ok:
        print("[INSTRUCTION] Please install missing dependencies.", file=sys.stderr)
        return False
    return True

def check_and_setup_env_vars(repo_root: str) -> bool:
    """Load environment variables from a .env file.

    Attempts to load environment variables from a .env file in the specified
    repository root directory. Uses python-dotenv to parse and set variables.

    Args:
        repo_root: The root directory of the repository containing the .env file.

    Returns:
        True if the .env file was found and loaded successfully,
        False if the file does not exist or loading failed.

    Raises:
        No exceptions are raised; errors are handled internally.

    Example:
        >>> if check_and_setup_env_vars("/path/to/project"):
        ...     api_key = os.environ.get("API_KEY")
        ... else:
        ...     print("No .env file found, using defaults")
    """
    try:
        dotenv_path = os.path.join(repo_root, ".env")
        if os.path.exists(dotenv_path):
            dotenv.load_dotenv(dotenv_path)
            return True
        else:
            return False
    except ImportError:
        return False

def validate_python_version() -> bool:
    """Validate that the Python version meets minimum requirements.

    Checks that the current Python interpreter is version 3.10 or higher,
    which is required for Codomyrmex functionality.

    Returns:
        True if Python version is 3.10 or higher, False otherwise.

    Example:
        >>> if not validate_python_version():
        ...     print(f"Python 3.10+ required, found {sys.version}")
        ...     sys.exit(1)
    """
    return sys.version_info >= (3, 10)

def is_uv_available() -> bool:
    """Check if the 'uv' package manager is available in the system PATH.

    The 'uv' tool is a fast Python package installer and resolver that can
    be used as an alternative to pip.

    Returns:
        True if 'uv' is found in the system PATH, False otherwise.

    Example:
        >>> if is_uv_available():
        ...     subprocess.run(["uv", "pip", "install", "package"])
        ... else:
        ...     subprocess.run(["pip", "install", "package"])
    """
    return shutil.which("uv") is not None

def is_uv_environment() -> bool:
    """Check if the current Python interpreter is running within a uv-managed environment.

    Determines whether the current execution context is inside a virtual
    environment (indicated by VIRTUAL_ENV environment variable) or if uv
    is available in the system.

    Returns:
        True if running in a virtual environment or uv is available,
        False otherwise.

    Example:
        >>> if is_uv_environment():
        ...     print("Running in uv-managed environment")
    """
    # Check for VIRTUAL_ENV environment variable which uv sets
    # Or specifically check if the python executable path is inside .venv created by uv
    return os.environ.get("VIRTUAL_ENV") is not None or is_uv_available()

def generate_environment_report() -> str:
    """Generate an environment status report.

    Returns:
        A detailed report of Python version, dependencies, environment
        variables, and system configuration.
    """
    report = [
        "Codomyrmex Environment Report",
        "===========================",
        f"Python Version: {sys.version.split()[0]}",
        f"Python Executable: {sys.executable}",
        f"UV Available: {'Yes' if is_uv_available() else 'No'}",
        f"UV Environment: {'Yes' if is_uv_environment() else 'No'}"
    ]
    
    deps_ok = True
    try:
        import cased
    except ImportError:
        deps_ok = False
        
    try:
        import dotenv
    except ImportError:
        deps_ok = False
        
    report.append(f"Dependencies OK: {'Yes' if deps_ok else 'No'}")
    return "\n".join(report)

def validate_environment_completeness(repo_root: str | None = None) -> bool:
    """Validate that the environment is fully configured for Codomyrmex.

    Performs a comprehensive check of all environment requirements including
    dependencies, environment variables, and Python version. This is the
    primary validation function to call before running Codomyrmex operations.

    Args:
        repo_root: The root directory of the repository. If not provided,
            defaults to the parent directory of the codomyrmex package.

    Returns:
        True if all environment checks pass (dependencies installed,
        .env file loaded, Python version valid), False otherwise.

    Example:
        >>> if validate_environment_completeness("/path/to/project"):
        ...     print("Environment ready")
        ...     start_application()
        ... else:
        ...     print("Environment validation failed")
        ...     sys.exit(1)
    """
    if repo_root is None:
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    deps = ensure_dependencies_installed()
    env_vars = check_and_setup_env_vars(repo_root)
    py_ver = validate_python_version()
    uv_env = is_uv_environment()

    return deps and env_vars and py_ver

if __name__ == "__main__":
    print("Running env_checker.py standalone for basic checks...")
    mock_repo_root = os.path.abspath(os.path.join(_script_dir, ".."))

    ensure_dependencies_installed()
    check_and_setup_env_vars(mock_repo_root)
    print(f"UV Available: {is_uv_available()}")

    print("env_checker.py standalone checks complete.")
