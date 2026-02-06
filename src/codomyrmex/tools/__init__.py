"""
Tools Module for Codomyrmex.

The Tools module provides development utilities and helper tools for project analysis,
dependency management, and maintenance tasks. These are command-line utilities
designed to support development workflows and project maintenance.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.
- Integrates with `static_analysis` for code quality analysis.
- Works with `system_discovery` for system introspection.

Available functions:
- analyze_project_structure: Analyze project structure and file organization
- analyze_project_dependencies: Analyze project dependencies
- analyze_code_quality: Analyze code quality metrics
- check_dependencies: Check and validate project dependencies
- consolidate_dependencies: Analyze dependencies for consolidation
- add_deprecation_notice: Add deprecation notice to requirements.txt files

Available classes:
- DependencyAnalyzer: Analyze module dependencies and detect circular imports

Data structures:
- DependencyAnalyzer: Analyzes module dependencies for circular imports
- ProjectAnalyzer: Analyzes project structure and code quality
- DependencyValidator: Validates dependency configurations
"""

from .add_deprecation_notices import add_deprecation_notice
from .add_deprecation_notices import main as add_deprecation_notices_main
from .analyze_project import analyze_code_quality, analyze_project_structure
from .analyze_project import analyze_dependencies as analyze_project_dependencies
from .analyze_project import generate_report as generate_analysis_report
from .analyze_project import main as analyze_project_main
from .dependency_analyzer import DependencyAnalyzer
from .dependency_analyzer import main as dependency_analyzer_main
from .dependency_checker import check_dependencies
from .dependency_checker import main as dependency_checker_main
from .dependency_consolidator import analyze_dependencies as consolidate_dependencies
from .dependency_consolidator import main as dependency_consolidator_main
from .validate_dependencies import main as validate_dependencies_main

__all__ = [
    # Main analysis functions
    "analyze_project_structure",
    "analyze_project_dependencies",
    "analyze_code_quality",
    "check_dependencies",
    "consolidate_dependencies",
    "add_deprecation_notice",

    # Main classes
    "DependencyAnalyzer",

    # CLI entry points
    "analyze_project_main",
    "dependency_analyzer_main",
    "dependency_checker_main",
    "dependency_consolidator_main",
    "validate_dependencies_main",
    "add_deprecation_notices_main",
]
