# DEPRECATED(v0.2.0): Shim module. Import from maintenance.deps.dependency_checker instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: maintenance.deps.dependency_checker"""
from .deps.dependency_checker import *  # noqa: F401,F403
from .deps.dependency_checker import (
    check_dependencies,
    check_python_version,
)
