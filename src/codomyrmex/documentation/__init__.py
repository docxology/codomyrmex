"""
Documentation Module for Codomyrmex.

This module provides comprehensive documentation management and website generation
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

from .documentation_website import (
    check_doc_environment,
    run_command_stream_output,
    install_dependencies,
    start_dev_server,
    build_static_site,
    serve_static_site,
    print_assessment_checklist,
    aggregate_docs,
    validate_doc_versions,
    assess_site,
)

__all__ = [
    'check_doc_environment',
    'run_command_stream_output',
    'install_dependencies',
    'start_dev_server',
    'build_static_site',
    'serve_static_site',
    'print_assessment_checklist',
    'aggregate_docs',
    'validate_doc_versions',
    'assess_site',
] 