"""
Code Execution Sandbox Module for Codomyrmex.

This module provides a secure environment for executing untrusted code in various
programming languages using Docker containers for isolation.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Requires Docker to be installed and running on the host system.

Available functions:
- execute_code
"""

from .code_executor import execute_code

__all__ = [
    'execute_code',
] 