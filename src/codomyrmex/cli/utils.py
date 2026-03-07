from typing import Any

try:
    from codomyrmex.terminal_interface.terminal_utils import TerminalFormatter

    TERMINAL_INTERFACE_AVAILABLE = True
except ImportError:
    TERMINAL_INTERFACE_AVAILABLE = False
    TerminalFormatter = None

try:
    import psutil  # noqa: F401

    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False


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


__all__ = [
    "PERFORMANCE_MONITORING_AVAILABLE",
    "TERMINAL_INTERFACE_AVAILABLE",
    "get_formatter",
    "print_error",
    "print_header",
    "print_success",
    "print_warning",
]
