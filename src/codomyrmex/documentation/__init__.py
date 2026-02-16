"""
Documentation Module for Codomyrmex.

This module provides documentation management and website generation
capabilities for the Codomyrmex project.

Submodules:
    education: Consolidated education capabilities.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.

Available functions:
- check_doc_environment
- run_command_stream_output
- install_dependencies
- start_dev_server
- build_static_site
- serve_static_site
- print_assessment_checklist
- aggregate_docs
- validate_doc_versions
- assess_site
"""

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .consistency_checker import DocumentationConsistencyChecker
from .documentation_website import (
    aggregate_docs,
    assess_site,
    build_static_site,
    check_doc_environment,
    install_dependencies,
    print_assessment_checklist,
    run_command_stream_output,
    serve_static_site,
    start_dev_server,
    validate_doc_versions,
)
from .quality_assessment import DocumentationQualityAnalyzer, generate_quality_report

def cli_commands():
    """Return CLI commands for the documentation module."""
    def _generate(path=None):
        import os
        target = path or os.getcwd()
        print(f"Generating documentation for: {target}")
        try:
            result = aggregate_docs(target)
            if result:
                print(f"  Result: {result}")
            else:
                print("  Documentation aggregated successfully.")
        except Exception as e:
            print(f"Documentation error: {e}")

    def _list_formats():
        formats = ["html", "markdown", "json", "rst"]
        print("Supported output formats:")
        for fmt in formats:
            print(f"  {fmt}")

    return {
        "generate": _generate,
        "formats": _list_formats,
    }


from . import education

__all__ = [
    "education",
    "cli_commands",
    "check_doc_environment",
    "run_command_stream_output",
    "install_dependencies",
    "start_dev_server",
    "build_static_site",
    "serve_static_site",
    "print_assessment_checklist",
    "aggregate_docs",
    "validate_doc_versions",
    "assess_site",
    "DocumentationQualityAnalyzer",
    "generate_quality_report",
    "DocumentationConsistencyChecker",
]
