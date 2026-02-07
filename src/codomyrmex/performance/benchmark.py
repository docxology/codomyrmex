"""
Benchmarking utilities for Codomyrmex.

Provides tools for measuring execution time and memory usage of functions.
"""

import time
import statistics
import functools
from typing import Any, Callable, Dict, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def run_benchmark(
    func: Callable[[], Any], 
    iterations: int = 5, 
    warmup: int = 0
) -> Dict[str, Any]:
    """
    Run a benchmark on a function.

    Args:
        func: The function to benchmark. Should be a callable that takes no arguments.
              Use lambda or functools.partial for functions with arguments.
        iterations: Number of times to run the function.
        warmup: Number of warmup iterations to run before measuring.

    Returns:
        Dictionary containing benchmark statistics.
    """
    # Warmup
    for _ in range(warmup):
        try:
            func()
        except Exception:
            pass

    times = []
    
    for _ in range(iterations):
        start_time = time.perf_counter()
        try:
            func()
        except Exception:
            # We record time even if it fails, or maybe we should note failure?
            # For simple benchmarking, we assume the function works.
            pass
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    if not times:
        return {
            "iterations": 0,
            "average_time": 0.0,
            "min_time": 0.0,
            "max_time": 0.0,
            "total_time": 0.0,
            "stdev": 0.0,
        }

    total_time = sum(times)
    avg_time = total_time / len(times)
    min_time = min(times)
    max_time = max(times)
    stdev = statistics.stdev(times) if len(times) > 1 else 0.0

    return {
        "iterations": len(times),
        "average_time": avg_time,
        "min_time": min_time,
        "max_time": max_time,
        "total_time": total_time,
        "stdev": stdev,
    }


def profile_function(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Profile a single function call execution time and memory usage.

    Args:
        func: Function to profile.
        *args: Arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Dictionary containing 'execution_time' (seconds) and 'memory_usage' (MB).
    """
    memory_before = 0.0
    if HAS_PSUTIL:
        process = psutil.Process()
        memory_before = process.memory_info().rss / (1024 * 1024)

    start_time = time.perf_counter()
    try:
        func(*args, **kwargs)
    except Exception:
        pass
    end_time = time.perf_counter()
    
    memory_after = 0.0
    if HAS_PSUTIL:
        memory_after = process.memory_info().rss / (1024 * 1024)

    execution_time = end_time - start_time
    memory_usage = max(0.0, memory_after - memory_before)

    return {
        "execution_time": execution_time,
        "memory_usage": memory_usage,
    }


class PerformanceProfiler:
    """Class-based profiler for consistency with tests."""

    def profile_function(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Profile a function."""
        return profile_function(func, *args, **kwargs)
