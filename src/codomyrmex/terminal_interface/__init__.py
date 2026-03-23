"""
Codomyrmex Terminal Interface Module

This module provides interactive terminal interfaces and utilities for
exploring and interacting with the Codomyrmex ecosystem in engaging,
accessible ways.
"""

# Submodule exports - import first
import contextlib

from codomyrmex.logging_monitoring import get_logger

from . import commands, completions, rendering, shells

logger = get_logger(__name__)

# Try optional submodules
try:
    from . import utils
except ImportError as e:
    logger.debug("Optional terminal_interface submodule 'utils' not available: %s", e)

# Try to import from existing modules, but don't fail if they don't exist
with contextlib.suppress(ImportError):
    from .shells.interactive_shell import InteractiveShell

with contextlib.suppress(ImportError):
    from .utils.terminal_utils import CommandRunner, TerminalFormatter

# Shared schemas for cross-module interop
with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus


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
        "gemini": {
            "help": "Run the Gemini CLI directly (requires @google/gemini-cli installed)",
            "handler": lambda **kwargs: __import__(
                "codomyrmex.terminal_interface.commands.gemini_cmd", fromlist=[""]
            ).run_gemini_cli(),
        },
    }


__all__ = [
    "cli_commands",
    "commands",
    "completions",
    "rendering",
    "shells",
]

if InteractiveShell:
    __all__.append("InteractiveShell")
if CommandRunner:
    __all__.extend(["CommandRunner", "TerminalFormatter"])

__version__ = "0.1.0"
