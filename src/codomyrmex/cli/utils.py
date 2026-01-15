from typing import Optional, Any
import logging

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
except ImportError:
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)

try:
    from codomyrmex.terminal_interface.terminal_utils import CommandRunner, TerminalFormatter
    TERMINAL_INTERFACE_AVAILABLE = True
except ImportError:
    TERMINAL_INTERFACE_AVAILABLE = False
    TerminalFormatter = None
    CommandRunner = None

try:
    from codomyrmex.performance.performance_monitor import PerformanceMonitor, monitor_performance
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False
    PerformanceMonitor = None
    monitor_performance = None

def get_formatter() -> Optional[Any]:
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
