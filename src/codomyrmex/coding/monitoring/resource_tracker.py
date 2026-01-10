"""
Resource Tracking

Monitors resource usage during code execution.
"""

from typing import Any, Dict
import time

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Create a dummy psutil module for type hints
    class _DummyPSUtil:
        Process = None
        cpu_percent = lambda *args, **kwargs: 0.0
        virtual_memory = lambda: type('obj', (object,), {'used': 0, 'total': 0})()
    psutil = _DummyPSUtil()

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

class ResourceMonitor:
    """Monitor resource usage during code execution."""

    def __init__(self):
        """Initialize the resource monitor."""
        self.start_time = None
        self.start_memory = None
        self.peak_memory = 0
        self.cpu_usage = []

    def start_monitoring(self) -> None:
        """Start resource monitoring."""
        self.start_time = time.time()
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available - resource monitoring disabled")
            self.start_memory = 0
            return
        try:
            process = psutil.Process()
            self.start_memory = process.memory_info().rss / 1024 / 1024  # MB
            self.peak_memory = self.start_memory
        except (AttributeError, psutil.NoSuchProcess, psutil.AccessDenied):
            logger.warning("Unable to start memory monitoring")
            self.start_memory = 0

    def update_monitoring(self) -> None:
        """Update resource usage metrics."""
        if not PSUTIL_AVAILABLE:
            return
        try:
            process = psutil.Process()
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            self.peak_memory = max(self.peak_memory, current_memory)

            # Get CPU usage (sample for 0.1 seconds)
            cpu_percent = process.cpu_percent(interval=0.1)
            self.cpu_usage.append(cpu_percent)
        except (AttributeError, psutil.NoSuchProcess, psutil.AccessDenied):
            pass  # Process may have ended

    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage statistics."""
        execution_time = time.time() - self.start_time if self.start_time else 0

        return {
            "execution_time_seconds": round(execution_time, 3),
            "memory_start_mb": round(self.start_memory or 0, 2),
            "memory_peak_mb": round(self.peak_memory, 2),
            "cpu_samples": len(self.cpu_usage),
            "cpu_average_percent": round(sum(self.cpu_usage) / len(self.cpu_usage), 2) if self.cpu_usage else 0,
            "cpu_peak_percent": round(max(self.cpu_usage), 2) if self.cpu_usage else 0,
        }
