"""
Codomyrmex Terminal Interface Module

This module provides interactive terminal interfaces and utilities for
exploring and interacting with the Codomyrmex ecosystem in engaging,
accessible ways.
"""

from .shells.interactive_shell import InteractiveShell
from .utils.terminal_utils import CommandRunner, TerminalFormatter

# Submodule exports
from . import shells
from . import utils
from . import commands
from . import rendering
from . import completions

__all__ = [
    "InteractiveShell",
    "TerminalFormatter",
    "CommandRunner",
    "shells",
    "utils",
    "commands",
    "rendering",
    "completions",
]

__version__ = "0.1.0"

