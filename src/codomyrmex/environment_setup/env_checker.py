"""Environment validation and setup utilities.

This module provides functions for validating and configuring the development
environment, including dependency checking, environment variable management,
Python version validation, and uv package manager detection.
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
import os
import platform
import shutil
import sys
from dataclasses import dataclass, field
from typing import Any

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
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyStatus:
    """Status of a specific dependency."""

    name: str
    installed: bool
    version: str | None = None
    required_version: str | None = None
    satisfied: bool = False
    error: str | None = None


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
        # Simple comparison for common version strings
        min_parts = [int(p) for p in min_version.split(".")]
        current_parts = list(sys.version_info[: len(min_parts)])
        return current_parts >= min_parts
    except (ValueError, AttributeError) as e:
        logger.error("Invalid min_version format: %s (%s)", min_version, e)
        # Fallback to a safe default
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
    """Check if specified dependencies are installed and meet version constraints.

    Args:
        dependencies: List of package names or constraints (e.g., "requests", "numpy>=1.25.0").

    Returns:
        List of DependencyStatus objects.
    """
    results = []
    # Map from import name to distribution name if they differ
    # This is a common issue (e.g., 'python-dotenv' is the distribution, 'dotenv' is the module)
    dist_map = importlib.metadata.packages_distributions()

    for dep_req in dependencies:
        # Basic parsing of constraints
        import_name = dep_req
        constraint = None
        for op in [">=", "==", "<=", "~=", ">", "<"]:
            if op in dep_req:
                import_name, constraint = dep_req.split(op, 1)
                import_name = import_name.strip()
                constraint = f"{op}{constraint.strip()}"
                break

        # 1. Check if module is importable
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            # Maybe the import name is different from the package name
            # We check the distribution map
            dists = dist_map.get(import_name)
            if dists:
                # Use the first distribution found
                pkg_name = dists[0]
            else:
                pkg_name = import_name
        else:
            # Find which package provides this module
            dists = dist_map.get(import_name)
            pkg_name = dists[0] if dists else import_name

        try:
            version = importlib.metadata.version(pkg_name)
            installed = True
            satisfied = True

            if constraint:
                # Simple constraint check
                # For robust version comparison, we'd use 'packaging.version'
                # but we aim for zero extra dependencies if possible.
                # Here we do a basic string/tuple comparison if it's a simple version.
                satisfied = _check_version_satisfied(version, constraint)

            results.append(
                DependencyStatus(
                    name=pkg_name,
                    installed=installed,
                    version=version,
                    required_version=constraint,
                    satisfied=satisfied,
                )
            )
        except importlib.metadata.PackageNotFoundError:
            # If not found in metadata, but find_spec worked, it's installed but maybe not as a package
            if spec:
                results.append(
                    DependencyStatus(
                        name=import_name,
                        installed=True,
                        version="unknown",
                        satisfied=True,
                    )
                )
            else:
                results.append(
                    DependencyStatus(
                        name=import_name,
                        installed=False,
                        satisfied=False,
                    )
                )
    return results


def _check_version_satisfied(current: str, constraint: str) -> bool:
    """Basic version constraint checker without external dependencies.

    Supports simple >=, == comparisons.
    """
    try:
        op = ""
        for possible_op in [">=", "==", "<=", "~=", ">", "<"]:
            if constraint.startswith(possible_op):
                op = possible_op
                break

        if not op:
            return True

        req_version = constraint[len(op) :].strip()

        # Simple numeric tuple comparison
        def to_tuple(v: str) -> tuple[int, ...]:
            # Remove any pre-release/post-release tags for simple comparison
            clean_v = "".join(c if c.isdigit() or c == "." else " " for c in v).split()[
                0
            ]
            return tuple(int(p) for p in clean_v.split(".") if p.isdigit())

        cur_t = to_tuple(current)
        req_t = to_tuple(req_version)

        if op == ">=":
            return cur_t >= req_t
        if op == "==":
            return cur_t == req_t
        if op == "<=":
            return cur_t <= req_t
        if op == ">":
            return cur_t > req_t
        if op == "<":
            return cur_t < req_t
        if op == "~=":
            # Compatible release: same major, at least the minor
            return cur_t[0] == req_t[0] and cur_t >= req_t

        return True
    except Exception as e:
        logger.debug(
            "Version comparison failed for %s vs %s: %s", current, constraint, e
        )
        return True  # Be lenient if parsing fails


def ensure_dependencies_installed(dependencies: list[str] | None = None) -> bool:
    """Check if required dependencies are installed and accessible.

    Args:
        dependencies: Optional list of package names to check.
            If None, checks default ('cased-kit', 'python-dotenv').

    Returns:
        True if all specified dependencies are installed and satisfied, False otherwise.
    """
    if dependencies is None:
        # Using distribution names where possible
        dependencies = ["cased-kit", "python-dotenv"]

    statuses = check_dependencies(dependencies)
    all_satisfied = True

    for status in statuses:
        if status.satisfied:
            logger.info(
                "Dependency '%s' found (version %s).", status.name, status.version
            )
        elif status.installed:
            logger.warning(
                "Dependency '%s' version mismatch: found %s, required %s.",
                status.name,
                status.version,
                status.required_version,
            )
            all_satisfied = False
        else:
            logger.warning("Dependency '%s' NOT found.", status.name)
            all_satisfied = False

    if not all_satisfied:
        logger.error(
            "Missing or incompatible dependencies. Please install them using 'uv pip install' or 'pip install'."
        )

    return all_satisfied


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
    details = {}

    # Python version check
    python_valid = validate_python_version(min_python)
    details["python_version"] = sys.version.split()[0]
    details["python_valid"] = python_valid
    if not python_valid:
        missing_items.append(f"Python >= {min_python}")

    # Core dependencies check
    core_deps = ["dotenv", "cased-kit"]
    dep_statuses = check_dependencies(core_deps)
    details["dependencies"] = {s.name: s.satisfied for s in dep_statuses}

    for status in dep_statuses:
        if not status.satisfied:
            missing_items.append(status.name)

    return ValidationReport(
        valid=len(missing_items) == 0, missing_items=missing_items, details=details
    )


def generate_environment_report() -> str:
    """Generate a detailed environment status report."""
    report = [
        "Codomyrmex Environment Report",
        "===========================",
        f"Python Version: {sys.version.split()[0]}",
        f"Python Executable: {sys.executable}",
        f"OS Platform: {platform.platform()}",
        f"UV Available: {'Yes' if is_uv_available() else 'No'}",
        f"UV Path: {get_uv_path() or 'N/A'}",
        f"UV Environment: {'Yes' if is_uv_environment() else 'No'}",
    ]

    try:
        from codomyrmex.environment_setup.dependency_resolver import DependencyResolver

        resolver = DependencyResolver(python_path=sys.executable)
        venv = resolver.detect_virtualenv()
        report.append(f"Virtualenv: {venv['type']} ({venv['path'] or 'None'})")

        installed = resolver.list_installed()
        report.append(f"Installed Packages: {len(installed)}")
    except ImportError:
        report.append(f"Virtualenv: {'Yes' if os.environ.get('VIRTUAL_ENV') else 'No'}")

    # Add core dependency status
    report.append("\nCore Dependencies:")
    core_deps = ["python-dotenv", "cased-kit", "pydantic", "jsonschema"]
    statuses = check_dependencies(core_deps)
    for s in statuses:
        status_str = "✅" if s.satisfied else "❌"
        ver_str = f"({s.version})" if s.version else ""
        report.append(f"  {status_str} {s.name} {ver_str}")

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
    print(f"\nEnvironment Valid: {val_report.valid}")
    if not val_report.valid:
        print(f"Missing: {val_report.missing_items}")
