# DEPRECATED(v0.2.0): Shim module. Import from maintenance.deps.dependency_consolidator instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: maintenance.deps.dependency_consolidator"""
from .deps.dependency_consolidator import *  # noqa: F401,F403
from .deps.dependency_consolidator import (
    analyze_dependencies,
    find_all_requirements_files,
    generate_deprecation_notice,
    parse_requirements_file,
)
