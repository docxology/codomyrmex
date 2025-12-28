"""
Documentation Module for Codomyrmex.

This module provides documentation management and website generation
capabilities for the Codomyrmex project.

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

__all__ = [
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
