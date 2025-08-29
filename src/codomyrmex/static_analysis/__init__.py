"""
Static Analysis Module for Codomyrmex.

The Static Analysis module provides tools and integrations for analyzing source code
without executing it. Its core purpose is to enhance code quality through automated
analysis and error detection.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.

Available functions:
- parse_pyrefly_output
- run_pyrefly_analysis
"""

from .pyrefly_runner import (
    parse_pyrefly_output,
    run_pyrefly_analysis,
)

__all__ = [
    'parse_pyrefly_output',
    'run_pyrefly_analysis',
] 