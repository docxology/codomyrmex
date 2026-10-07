from __future__ import annotations

import importlib.util

from codomyrmex.terminal_interface.utils.terminal_utils import TerminalFormatter

PERFORMANCE_MONITORING_AVAILABLE = (
    importlib.util.find_spec("codomyrmex.performance.monitoring") is not None
)


def get_formatter() -> TerminalFormatter:
    """Get a TerminalFormatter for CLI output."""
    return TerminalFormatter()


def print_success(msg: str):
    """Print a success message using the terminal formatter."""
    print(get_formatter().success(msg))


def print_error(msg: str):
    """Print an error message using the terminal formatter."""
    print(get_formatter().error(msg))


def print_warning(msg: str):
    """Print a warning message using the terminal formatter."""
    print(get_formatter().warning(msg))


def print_header(msg: str, char: str = "=", length: int = 60):
    """Print a header message using the terminal formatter."""
    print(get_formatter().header(msg, char, length))
