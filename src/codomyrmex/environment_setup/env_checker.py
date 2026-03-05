"""Environment validation and setup utilities.

This module provides functions for validating and configuring the development
environment, including dependency checking, environment variable management,
Python version validation, and uv package manager detection.
"""

import importlib.util
import os
import shutil
import sys
from dataclasses import dataclass, field

import dotenv

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Store the original script directory to correctly locate files relative to REPO_ROOT_PATH
_script_dir = os.path.dirname(__file__)


@dataclass
class ValidationReport:
    """Report on environment validation status."""

    valid: bool
    missing_items: list[str] = field(default_factory=list)


@dataclass
class DependencyStatus:
    """Status of a specific dependency."""

    name: str
    installed: bool


@dataclass
class APIKeyReport:
    """Report on API key presence."""

    all_present: bool
    missing: list[str] = field(default_factory=list)


def validate_python_version(min_version: str = "3.10") -> bool:
    """Validate that the Python version meets minimum requirements.

    Args:
        min_version: Minimum required version string (e.g., "3.11").

    Returns:
        True if Python version meets or exceeds min_version, False otherwise.
    """
    try:
        min_tuple = tuple(map(int, min_version.split(".")))
        return sys.version_info >= min_tuple
    except (ValueError, AttributeError):
        logger.error("Invalid min_version format: %s", min_version)
        return sys.version_info >= (3, 10)


def is_uv_available() -> bool:
    """Check if the 'uv' package manager is available in the system PATH."""
    return shutil.which("uv") is not None


def get_uv_path() -> str | None:
    """Get the path to the 'uv' executable if available."""
    return shutil.which("uv")


def is_uv_environment() -> bool:
    """Check if the current Python interpreter is running within a uv-managed environment."""
    return (
        os.environ.get("UV_ACTIVE") == "1"
        or os.environ.get("VIRTUAL_ENV") is not None
        or is_uv_available()
    )


def check_dependencies(dependencies: list[str]) -> list[DependencyStatus]:
    """Check if specified dependencies are installed.

    Args:
        dependencies: List of package names to check.

    Returns:
        List of DependencyStatus objects.
    """
    results = []
    for dep in dependencies:
        installed = importlib.util.find_spec(dep) is not None
        results.append(DependencyStatus(name=dep, installed=installed))
    return results


def ensure_dependencies_installed(dependencies: list[str] | None = None) -> bool:
    """Check if required dependencies are installed and accessible.

    Args:
        dependencies: Optional list of package names to check.
            If None, checks default ('kit', 'python-dotenv').

    Returns:
        True if all specified dependencies are installed, False otherwise.
    """
    if dependencies is None:
        dependencies = ["kit", "dotenv"]

    statuses = check_dependencies(dependencies)
    all_installed = True

    for status in statuses:
        if status.installed:
            logger.info("Dependency '%s' found.", status.name)
        else:
            logger.warning("Dependency '%s' NOT found.", status.name)
            all_installed = False

    if not all_installed:
        logger.error(
            "Missing dependencies. Please install them using 'uv pip install' or 'pip install'."
        )

    return all_installed


def check_and_setup_env_vars(
    repo_root: str | None = None,
    required: list[str] | None = None,
    optional: list[str] | None = None,
) -> list[str]:
    """Load environment variables from a .env file and check for required keys.

    Args:
        repo_root: Directory to look for .env file.
        required: List of environment variables that MUST be present.
        optional: List of environment variables that are optional.

    Returns:
        List of missing required environment variable names.
    """
    if repo_root:
        dotenv_path = os.path.join(repo_root, ".env")
        if os.path.exists(dotenv_path):
            dotenv.load_dotenv(dotenv_path)
            logger.info("Loaded .env from %s", dotenv_path)
        else:
            logger.debug("No .env found at %s", dotenv_path)
    else:
        dotenv.load_dotenv()

    missing = []
    if required:
        for var in required:
            if var not in os.environ:
                missing.append(var)

    if missing:
        logger.warning("Missing required environment variables: %s", missing)

    return missing


def check_api_keys(keys: list[str]) -> APIKeyReport:
    """Check if required API keys are set in the environment.

    Args:
        keys: List of environment variable names to check.

    Returns:
        APIKeyReport indicating status.
    """
    missing = [k for k in keys if k not in os.environ]
    return APIKeyReport(all_present=len(missing) == 0, missing=missing)


def validate_environment(min_python: str = "3.10") -> ValidationReport:
    """Comprehensive environment validation.

    Returns:
        ValidationReport containing overall status and missing items.
    """
    missing_items = []

    if not validate_python_version(min_python):
        missing_items.append(f"Python >= {min_python}")

    # Check for basic dependencies
    if not importlib.util.find_spec("dotenv"):
        missing_items.append("python-dotenv")

    return ValidationReport(valid=len(missing_items) == 0, missing_items=missing_items)


def generate_environment_report() -> str:
    """Generate a detailed environment status report."""
    report = [
        "Codomyrmex Environment Report",
        "===========================",
        f"Python Version: {sys.version.split()[0]}",
        f"Python Executable: {sys.executable}",
        f"UV Available: {'Yes' if is_uv_available() else 'No'}",
        f"UV Path: {get_uv_path() or 'N/A'}",
        f"UV Environment: {'Yes' if is_uv_environment() else 'No'}",
    ]

    try:
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver()
        venv = resolver.detect_virtualenv()
        report.append(f"Virtualenv: {venv['type']} ({venv['path'] or 'None'})")
    except ImportError:
        report.append(f"Virtualenv: {'Yes' if os.environ.get('VIRTUAL_ENV') else 'No'}")

    return "\n".join(report)


def validate_environment_completeness(repo_root: str | None = None) -> bool:
    """Legacy wrapper for backward compatibility."""
    if repo_root is None:
        # Default to repo root (3 levels up from this file)
        repo_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

    report = validate_environment()
    check_and_setup_env_vars(repo_root)

    return report.valid


if __name__ == "__main__":
    print(generate_environment_report())
    val_report = validate_environment()
    print(f"Environment Valid: {val_report.valid}")
    if not val_report.valid:
        print(f"Missing: {val_report.missing_items}")
