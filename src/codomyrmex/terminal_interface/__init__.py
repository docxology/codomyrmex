"""
Codomyrmex Terminal Interface Module

This module provides interactive terminal interfaces and utilities for
exploring and interacting with the Codomyrmex ecosystem in engaging,
accessible ways.
"""

import logging

logger = logging.getLogger(__name__)

# Submodule exports - import first
from . import commands, completions, rendering, shells

# Try optional submodules
try:
    from . import utils
except ImportError as e:
    logger.debug("Optional terminal_interface submodule 'utils' not available: %s", e)
    pass

# Try to import from existing modules, but don't fail if they don't exist
try:
    from .shells.interactive_shell import InteractiveShell
except ImportError:
    InteractiveShell = None

try:
    from .utils.terminal_utils import CommandRunner, TerminalFormatter
except ImportError:
    CommandRunner = None
    TerminalFormatter = None

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the terminal_interface module."""
    import os
    import shutil

    return {
        "themes": {
            "help": "List available terminal themes",
            "handler": lambda **kwargs: print(
                "Available themes:\n"
                "  - default: Standard terminal output\n"
                "  - rich: Rich text formatting with colors\n"
                "  - minimal: Minimal output, no decorations\n"
                "  - json: JSON-structured output"
            ),
        },
        "info": {
            "help": "Show terminal environment info",
            "handler": lambda **kwargs: print(
                f"Terminal: {os.environ.get('TERM', 'unknown')}\n"
                f"Shell: {os.environ.get('SHELL', 'unknown')}\n"
                f"Columns: {shutil.get_terminal_size().columns}\n"
                f"Lines: {shutil.get_terminal_size().lines}\n"
                f"Interactive shell available: {InteractiveShell is not None}\n"
                f"Command runner available: {CommandRunner is not None}"
            ),
        },
    }


__all__ = [
    "shells",
    "commands",
    "rendering",
    "completions",
    "cli_commands",
]

if InteractiveShell:
    __all__.append("InteractiveShell")
if CommandRunner:
    __all__.extend(["CommandRunner", "TerminalFormatter"])

__version__ = "0.1.0"

