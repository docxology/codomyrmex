"""
Isolation Mechanisms

Provides process isolation and resource limit enforcement for secure code execution.
"""

import multiprocessing
import resource
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Create a dummy psutil module for type hints
    class _DummyPSUtil:
        def cpu_percent(self, interval=None): return 0.0
        class NoSuchProcess(Exception): pass
    psutil = _DummyPSUtil()

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

# Constants
MAX_TIMEOUT = 300


@dataclass
class ExecutionLimits:
    """Structured configuration for execution resource limits."""
    time_limit: int = 30  # seconds
    memory_limit: int = 256  # MB
    cpu_limit: float = 0.5  # CPU cores
    max_output_chars: int = 100000  # Maximum output size

    def __post_init__(self):
        """Validate limits after initialization."""
        if self.time_limit < 1 or self.time_limit > MAX_TIMEOUT:
            raise ValueError(f"Time limit must be between 1 and {MAX_TIMEOUT} seconds")
        if self.memory_limit < 1:
            raise ValueError("Memory limit must be at least 1 MB")
        if self.cpu_limit <= 0 or self.cpu_limit > 4:
            raise ValueError("CPU limit must be between 0.1 and 4.0 cores")
        if self.max_output_chars < 1000:
            raise ValueError("Max output chars must be at least 1000")


@contextmanager
def resource_limits_context(limits: ExecutionLimits):
    """Context manager to set and restore resource limits."""
    old_limits = {}

    try:
        # Set CPU time limit (soft limit)
        soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
        old_limits[resource.RLIMIT_CPU] = (soft, hard)
        if hard != resource.RLIM_INFINITY:
             limited_time = min(limits.time_limit, hard)
        else:
             limited_time = limits.time_limit
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (limited_time, hard))
        except (ValueError, OSError) as e:
            logger.warning(f"Failed to set CPU limit: {e}")

        # Set memory limit (address space)
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        old_limits[resource.RLIMIT_AS] = (soft, hard)
        memory_bytes = limits.memory_limit * 1024 * 1024  # Convert MB to bytes
        if hard != resource.RLIM_INFINITY:
            memory_bytes = min(memory_bytes, hard)
        try:
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        except (ValueError, OSError) as e:
            logger.warning(f"Failed to set memory limit: {e}")

        yield

    finally:
        # Restore original limits
        for rlimit, (soft, hard) in old_limits.items():
            try:
                resource.setrlimit(rlimit, (soft, hard))
            except Exception as e:
                logger.warning(f"Failed to restore resource limit {rlimit}: {e}")


def execute_with_limits(
    language: str,
    code: str,
    limits: ExecutionLimits,
    stdin: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Execute code with resource limits and monitoring.

    Args:
        language: Programming language of the code
        code: Source code to execute
        limits: ExecutionLimits configuration
        stdin: Standard input to provide to the program
        session_id: Optional session identifier for persistent environments

    Returns:
        Dictionary with execution results including resource usage
    """
    from ..monitoring.resource_tracker import ResourceMonitor

    monitor = ResourceMonitor()

    # Set resource limits for the current process
    with resource_limits_context(limits):
        monitor.start_monitoring()

        # Execute the code
        from ..execution.executor import execute_code
        result = execute_code(language, code, stdin, limits.time_limit, session_id)

        # Update monitoring during execution (in a separate thread for better tracking)
        def monitoring_thread():
            """Background thread to monitor resource usage."""
            while True:
                monitor.update_monitoring()
                time.sleep(0.1)  # Update every 100ms
                # Stop monitoring when execution completes (this is approximate)

        monitor_thread = threading.Thread(target=monitoring_thread, daemon=True)
        monitor_thread.start()

        # Wait for execution to complete
        time.sleep(result.get("execution_time", 0) + 0.1)

        # Get final resource usage
        resource_usage = monitor.get_resource_usage()

        # Merge resource usage into result
        result.update({
            "resource_usage": resource_usage,
            "limits_applied": {
                "time_limit_seconds": limits.time_limit,
                "memory_limit_mb": limits.memory_limit,
                "cpu_limit_cores": limits.cpu_limit,
                "max_output_chars": limits.max_output_chars,
            }
        })

        return result


def sandbox_process_isolation(
    language: str,
    code: str,
    limits: ExecutionLimits,
    stdin: str | None = None,
) -> dict[str, Any]:
    """
    Execute code in a completely isolated process environment.

    This function creates a subprocess with its own resource limits,
    completely separate from the main process.

    Args:
        language: Programming language of the code
        code: Source code to execute
        limits: ExecutionLimits configuration
        stdin: Standard input to provide to the program

    Returns:
        Dictionary with execution results
    """
    def execute_in_subprocess(queue):
        """Execute code in a subprocess with resource limits."""
        try:
            # Set resource limits in the subprocess
            resource.setrlimit(resource.RLIMIT_CPU, (limits.time_limit, limits.time_limit + 10))
            memory_bytes = limits.memory_limit * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

            # Execute the code
            from ..execution.executor import execute_code
            result = execute_code(language, code, stdin, limits.time_limit)

            # Cap output size
            if len(result.get("stdout", "")) > limits.max_output_chars:
                result["stdout"] = result["stdout"][:limits.max_output_chars] + "\n... [Output truncated]"
            if len(result.get("stderr", "")) > limits.max_output_chars:
                result["stderr"] = result["stderr"][:limits.max_output_chars] + "\n... [Error output truncated]"

            queue.put(("success", result))

        except Exception as e:
            queue.put(("error", str(e)))

    # Create a queue for communication
    queue = multiprocessing.Queue()

    # Create and start the subprocess
    process = multiprocessing.Process(target=execute_in_subprocess, args=(queue,))
    process.start()

    # Wait for completion with timeout
    process.join(timeout=limits.time_limit + 5)  # Extra 5 seconds for cleanup

    if process.is_alive():
        # Process is still running (timeout exceeded)
        process.terminate()
        process.join(timeout=2)
        if process.is_alive():
            process.kill()

        return {
            "stdout": "",
            "stderr": f"Execution timeout exceeded ({limits.time_limit} seconds)",
            "exit_code": -1,
            "execution_time": limits.time_limit,
            "status": "timeout",
            "error_message": f"Process terminated due to timeout ({limits.time_limit}s)",
            "resource_usage": {
                "execution_time_seconds": limits.time_limit,
                "memory_start_mb": 0,
                "memory_peak_mb": 0,
                "cpu_samples": 0,
                "cpu_average_percent": 0,
                "cpu_peak_percent": 0,
            },
            "limits_applied": {
                "time_limit_seconds": limits.time_limit,
                "memory_limit_mb": limits.memory_limit,
                "cpu_limit_cores": limits.cpu_limit,
                "max_output_chars": limits.max_output_chars,
            }
        }

    # Get the result from the subprocess
    if not queue.empty():
        status, data = queue.get()
        if status == "success":
            # Add resource usage information
            data.update({
                "resource_usage": {
                    "execution_time_seconds": data.get("execution_time", 0),
                    "memory_start_mb": 0,  # Not available in subprocess
                    "memory_peak_mb": 0,   # Not available in subprocess
                    "cpu_samples": 0,
                    "cpu_average_percent": 0,
                    "cpu_peak_percent": 0,
                },
                "limits_applied": {
                    "time_limit_seconds": limits.time_limit,
                    "memory_limit_mb": limits.memory_limit,
                    "cpu_limit_cores": limits.cpu_limit,
                    "max_output_chars": limits.max_output_chars,
                }
            })
            return data
        else:
            return {
                "stdout": "",
                "stderr": f"Subprocess error: {data}",
                "exit_code": -1,
                "execution_time": 0,
                "status": "subprocess_error",
                "error_message": f"Execution failed in subprocess: {data}",
                "resource_usage": {
                    "execution_time_seconds": 0,
                    "memory_start_mb": 0,
                    "memory_peak_mb": 0,
                    "cpu_samples": 0,
                    "cpu_average_percent": 0,
                    "cpu_peak_percent": 0,
                },
                "limits_applied": {
                    "time_limit_seconds": limits.time_limit,
                    "memory_limit_mb": limits.memory_limit,
                    "cpu_limit_cores": limits.cpu_limit,
                    "max_output_chars": limits.max_output_chars,
                }
            }

    # Queue was empty (unexpected)
    return {
        "stdout": "",
        "stderr": "Unexpected error: no result from subprocess",
        "exit_code": -1,
        "execution_time": 0,
        "status": "communication_error",
        "error_message": "Failed to communicate with execution subprocess",
        "resource_usage": {
            "execution_time_seconds": 0,
            "memory_start_mb": 0,
            "memory_peak_mb": 0,
            "cpu_samples": 0,
            "cpu_average_percent": 0,
            "cpu_peak_percent": 0,
        },
        "limits_applied": {
            "time_limit_seconds": limits.time_limit,
            "memory_limit_mb": limits.memory_limit,
            "cpu_limit_cores": limits.cpu_limit,
            "max_output_chars": limits.max_output_chars,
        }
    }

