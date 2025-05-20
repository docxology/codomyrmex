"""
AI Code Editing Module for Codomyrmex.

This module provides utilities for AI-powered code generation and editing.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks (see project setup docs).

Available functions:
- generate_code_snippet
- refactor_code_snippet
"""

from .ai_code_helpers import (
    generate_code_snippet,
    refactor_code_snippet,
)

__all__ = [
    'generate_code_snippet',
    'refactor_code_snippet',
] 