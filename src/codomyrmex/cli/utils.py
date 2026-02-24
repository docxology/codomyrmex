import logging
from typing import Any

try:
    from codomyrmex.logging_monitoring.core.logger_config import get_logger
except ImportError:
    def get_logger(name: str) -> logging.Logger:
        """Execute Get Logger operations natively."""
        return logging.getLogger(name)

try:
    from codomyrmex.terminal_interface.terminal_utils import (
        CommandRunner,
        TerminalFormatter,
    )
    TERMINAL_INTERFACE_AVAILABLE = True
except ImportError:
    TERMINAL_INTERFACE_AVAILABLE = False
    TerminalFormatter = None
    CommandRunner = None

try:
    from codomyrmex.performance.monitoring.performance_monitor import (
        PerformanceMonitor,
        monitor_performance,
    )
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False
    PerformanceMonitor = None
    monitor_performance = None

def get_formatter() -> Any | None:
    """Get TerminalFormatter if available."""
    if TERMINAL_INTERFACE_AVAILABLE:
        return TerminalFormatter()
    return None

def print_success(msg: str):
    """Execute Print Success operations natively."""
    formatter = get_formatter()
    print(formatter.success(msg) if formatter else f"✅ {msg}")

def print_error(msg: str):
    """Execute Print Error operations natively."""
    formatter = get_formatter()
    print(formatter.error(msg) if formatter else f"❌ {msg}")

def print_warning(msg: str):
    """Execute Print Warning operations natively."""
    formatter = get_formatter()
    print(formatter.warning(msg) if formatter else f"⚠️  {msg}")

def print_header(msg: str, char: str = "=", length: int = 60):
    """Execute Print Header operations natively."""
    formatter = get_formatter()
    if formatter:
        print(formatter.header(msg, char, length))
    else:
        print(msg)
        print(char * length)
