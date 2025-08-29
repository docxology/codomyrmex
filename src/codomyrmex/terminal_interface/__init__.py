"""
Codomyrmex Terminal Interface Module

This module provides interactive terminal interfaces and utilities for
exploring and interacting with the Codomyrmex ecosystem in engaging,
accessible ways.
"""

from .interactive_shell import InteractiveShell
from .terminal_utils import TerminalFormatter, CommandRunner

__all__ = [
    'InteractiveShell',
    'TerminalFormatter', 
    'CommandRunner'
]

__version__ = "0.1.0"
