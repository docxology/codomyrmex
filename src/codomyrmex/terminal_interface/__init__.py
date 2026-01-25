"""
Codomyrmex Terminal Interface Module

This module provides interactive terminal interfaces and utilities for
exploring and interacting with the Codomyrmex ecosystem in engaging,
accessible ways.
"""

# Submodule exports - import first
from . import shells
from . import commands
from . import rendering
from . import completions

# Try optional submodules
try:
    from . import utils
except ImportError:
    pass

# Try to import from existing modules, but don't fail if they don't exist
try:
    from .shells.interactive_shell import InteractiveShell as LegacyInteractiveShell
except ImportError:
    LegacyInteractiveShell = None

try:
    from .utils.terminal_utils import CommandRunner, TerminalFormatter
except ImportError:
    CommandRunner = None
    TerminalFormatter = None

__all__ = [
    "shells",
    "commands",
    "rendering",
    "completions",
]

if LegacyInteractiveShell:
    __all__.append("InteractiveShell")
if CommandRunner:
    __all__.extend(["CommandRunner", "TerminalFormatter"])

__version__ = "0.1.0"
