from pathlib import Path
from typing import Dict, Any, Generator
import math
import os
import random
import shutil
import tempfile
import time

import pytest

from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger






"""
Shared fixtures and configuration for performance tests.
"""


try:
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False


@pytest.fixture(scope="session", autouse=True)
def setup_performance_logging():
    """Set up logging for performance tests."""
    if LOGGING_AVAILABLE and hasattr(setup_logging, '__call__'):
        try:
            setup_logging()
        except Exception:
            pass


@pytest.fixture
def temp_performance_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for performance test files."""
    temp_dir = tempfile.mkdtemp(prefix="perf_test_")
    yield Path(temp_dir)

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_code_files(temp_performance_dir: Path) -> Dict[str, Path]:
    """Create sample code files for performance testing."""
    files = {}

    # Small Python file
    small_file = temp_performance_dir / "small.py"
    small_file.write_text('''
def add_numbers(a, b):
    return a + b

result = add_numbers(5, 3)
print(result)
''')

    # Medium Python file with more complexity
    medium_file = temp_performance_dir / "medium.py"
    medium_file.write_text('''

def calculate_statistics(numbers):
    """Calculate basic statistics for a list of numbers."""
    if not numbers:
        return {"mean": 0, "median": 0, "std_dev": 0}

    mean = sum(numbers) / len(numbers)
    sorted_nums = sorted(numbers)
    median = sorted_nums[len(sorted_nums) // 2]

    variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
    std_dev = math.sqrt(variance)

    return {
        "mean": mean,
        "median": median,
        "std_dev": std_dev
    }

# Test with sample data
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
stats = calculate_statistics(data)
print(f"Statistics: {stats}")
''')

    # Large Python file with algorithms
    large_file = temp_performance_dir / "large.py"
    large_content = '''

def bubble_sort(arr):
    """Bubble sort implementation."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def quick_sort(arr):
    """Quick sort implementation."""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def fibonacci_recursive(n):
    """Calculate nth Fibonacci number recursively."""
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)

def fibonacci_iterative(n):
    """Calculate nth Fibonacci number iteratively."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# Performance comparison
print("Performance Comparison Test")
print("=" * 50)

# Generate test data
data_size = 100
test_data = [random.randint(0, 1000) for _ in range(data_size)]

# Test sorting algorithms
print(f"Sorting {data_size} elements...")

start_time = time.time()
bubble_result = bubble_sort(test_data.copy())
bubble_time = time.time() - start_time

start_time = time.time()
quick_result = quick_sort(test_data.copy())
quick_time = time.time() - start_time

print(f"Bubble sort: {bubble_time:.4f} seconds")
print(f"Quick sort:  {quick_time:.4f} seconds")
print(f"Speedup: {bubble_time / quick_time:.2f}x")

# Test Fibonacci calculations
fib_n = 25
print(f"\nCalculating Fibonacci({fib_n})...")

start_time = time.time()
fib_recursive = fibonacci_recursive(fib_n)
recursive_time = time.time() - start_time

start_time = time.time()
fib_iterative = fibonacci_iterative(fib_n)
iterative_time = time.time() - start_time

print(f"Recursive: {fib_recursive} ({recursive_time:.4f} seconds)")
print(f"Iterative: {fib_iterative} ({iterative_time:.4f} seconds)")
print(f"Speedup: {recursive_time / iterative_time:.2f}x")
'''

    large_file = temp_performance_dir / "large.py"
    large_file.write_text(large_content)

    files["small"] = small_file
    files["medium"] = medium_file
    files["large"] = large_file

    return files


@pytest.fixture
def performance_baseline_data() -> Dict[str, Any]:
    """Provide baseline performance data for comparison."""
    return {
        "module_performance_baselines": {
            "code.execute_code": {
                "small_script": 0.5,  # seconds
                "medium_script": 1.0,
                "large_script": 2.0
            },
            "static_analysis.analyze_file": {
                "small_file": 0.1,
                "medium_file": 0.5,
                "large_file": 2.0
            },
            "security_audit.analyze_file_security": {
                "small_file": 0.2,
                "medium_file": 1.0,
                "large_file": 3.0
            }
        },
        "system_requirements": {
            "min_execution_time": 0.001,  # seconds
            "max_memory_usage": 500,  # MB
            "max_cpu_usage": 80.0  # percent
        },
        "regression_thresholds": {
            "performance_degradation": 1.5,  # Max 50% slowdown
            "memory_increase": 1.2,  # Max 20% memory increase
        }
    }


@pytest.fixture
def mock_performance_logger():
    """Mock performance logger for testing."""
    class MockPerformanceLogger:
        def __init__(self, name="mock"):
            self.name = name
            self.operations = []

        def start_timer(self, operation, context=None):
            self.operations.append({
                "operation": operation,
                "type": "start",
                "context": context,
                "timestamp": time.time()
            })

        def end_timer(self, operation, context=None):
            self.operations.append({
                "operation": operation,
                "type": "end",
                "context": context,
                "timestamp": time.time()
            })

        def log_metric(self, name, value, unit=None, context=None):
            self.operations.append({
                "type": "metric",
                "name": name,
                "value": value,
                "unit": unit,
                "context": context,
                "timestamp": time.time()
            })

    return MockPerformanceLogger()


@pytest.fixture
def performance_test_config() -> Dict[str, Any]:
    """Configuration for performance tests."""
    return {
        "iterations": 5,
        "warmup_iterations": 2,
        "timeout": 60,  # seconds
        "memory_limit": 512,  # MB
        "cpu_limit": 0.8,  # 80% of CPU
        "output_dir": None,  # Will be set by temp dir
        "baseline_comparison": True,
        "regression_detection": True,
        "detailed_reporting": True,
    }
