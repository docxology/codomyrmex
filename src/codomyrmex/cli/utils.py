from __future__ import annotations

import importlib.util
from typing import Any


class _PlainTerminalFormatter:
    """Small fallback formatter used when terminal_interface is unavailable."""

    def success(self, msg: str) -> str:
        return f"✅ {msg}"

    def error(self, msg: str) -> str:
        return f"❌ {msg}"

    def warning(self, msg: str) -> str:
        return f"⚠️  {msg}"

    def header(self, msg: str, char: str = "=", length: int = 60) -> str:
        return f"{msg}\n{char * length}"

    def box(self, msg: str, title: str = "") -> str:
        header = self.header(title, "=", 60) if title else "=" * 60
        return f"{header}\n{msg}\n{'=' * 60}"

    def color(self, msg: str, _color: str) -> str:
        return msg


try:
    from codomyrmex.terminal_interface.terminal_utils import TerminalFormatter

    TERMINAL_INTERFACE_AVAILABLE = True
except ImportError:
    TERMINAL_INTERFACE_AVAILABLE = False
    TerminalFormatter = _PlainTerminalFormatter

PERFORMANCE_MONITORING_AVAILABLE = (
    importlib.util.find_spec("codomyrmex.performance.monitoring") is not None
)


def get_formatter() -> Any | None:
    """Get TerminalFormatter if available."""
    if TERMINAL_INTERFACE_AVAILABLE:
        return TerminalFormatter()
    return None


def print_success(msg: str):
    formatter = get_formatter()
    print(formatter.success(msg) if formatter else f"✅ {msg}")


def print_error(msg: str):
    formatter = get_formatter()
    print(formatter.error(msg) if formatter else f"❌ {msg}")


def print_warning(msg: str):
    formatter = get_formatter()
    print(formatter.warning(msg) if formatter else f"⚠️  {msg}")


def print_header(msg: str, char: str = "=", length: int = 60):
    formatter = get_formatter()
    if formatter:
        print(formatter.header(msg, char, length))
    else:
        print(msg)
        print(char * length)
