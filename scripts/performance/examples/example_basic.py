#!/usr/bin/env python3
"""
Example: Performance - Code Performance Monitoring

This example demonstrates:
- Profiling function execution time and memory usage
- Running performance benchmarks
- Monitoring system resources
- Generating performance reports

Tested Methods:
- profile_function() - Verified in test_performance_comprehensive.py::TestPerformance::test_profile_function
- run_benchmark() - Verified in test_performance_comprehensive.py::TestPerformance::test_run_benchmark
- get_system_metrics() - Verified in test_performance.py::TestPerformance::test_get_system_metrics
"""

import sys
import time
from pathlib import Path

# Add src to path
# Setup paths
root_dir = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / "scripts"))

from codomyrmex.performance.performance_monitor import profile_function, get_system_metrics
from codomyrmex.performance.resource_tracker import ResourceTracker
from _common.config_loader import load_config
from _common.example_runner import ExampleRunner
from _common.utils import print_section, print_results

def sample_function(n):
    """Sample function to profile."""
    result = 0
    for i in range(n):
        result += i ** 2
        time.sleep(0.001)  # Simulate some work
    return result

def fibonacci_recursive(n):
    """Recursive Fibonacci for benchmarking."""
    if n <= 1:
        return n
    return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)

def main():
    """Run the performance example."""
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        print_section("Performance Monitoring Example")

        # Get performance settings
        perf_config = config.get('performance', {})

        results = {
            'functions_profiled': 0,
            'benchmarks_run': 0,
            'metrics_collected': 0,
            'memory_tracked': 0
        }

        # Profile function execution
        print("Profiling function execution...")
        functions_to_profile = perf_config.get('functions_to_profile', [])

        for func_config in functions_to_profile:
            try:
                func_name = func_config.get('name', 'unknown')
                func_args = func_config.get('args', [])
                func_kwargs = func_config.get('kwargs', {})

                # Get the function
                if func_name == 'sample_function':
                    func = sample_function
                elif func_name == 'fibonacci_recursive':
                    func = fibonacci_recursive
                else:
                    continue

                # Profile the function
                profile_result = profile_function(func, *func_args, **func_kwargs)

                if profile_result:
                    execution_time = profile_result.get('execution_time', 0)
                    memory_usage = profile_result.get('memory_usage_mb', 0)

                    print(f"✓ Profiled {func_name}: {execution_time:.3f}s, "
                          f"{memory_usage:.2f} MB memory")

                    results['functions_profiled'] += 1
                else:
                    print(f"✗ Failed to profile {func_name}")

            except Exception as e:
                print(f"✗ Error profiling {func_name}: {e}")

        # Run performance benchmarks
        print("\nRunning performance benchmarks...")
        benchmarks = perf_config.get('benchmarks', [])

        for benchmark in benchmarks:
            try:
                benchmark_name = benchmark.get('name', 'unknown')
                iterations = benchmark.get('iterations', 1)

                if benchmark_name == 'fibonacci_benchmark':
                    # Benchmark Fibonacci calculation
                    benchmark_func = lambda: fibonacci_recursive(25)
                    benchmark_result = None

                    # Run multiple iterations
                    for i in range(iterations):
                        result = profile_function(benchmark_func)
                        if result:
                            if benchmark_result is None:
                                benchmark_result = result
                            else:
                                # Average the results
                                benchmark_result['execution_time'] = (
                                    benchmark_result['execution_time'] + result['execution_time']
                                ) / 2

                    if benchmark_result:
                        avg_time = benchmark_result['execution_time']
                        print(f"✓ Benchmark {benchmark_name}: {avg_time:.3f}s average "
                              f"({iterations} iterations)")
                        results['benchmarks_run'] += 1

            except Exception as e:
                print(f"✗ Error in benchmark {benchmark_name}: {e}")

        # Collect system metrics
        print("\nCollecting system metrics...")
        try:
            metrics = get_system_metrics()

            if metrics:
                cpu_percent = metrics.get('cpu_percent', 0)
                memory_percent = metrics.get('memory_percent', 0)
                disk_usage = metrics.get('disk_usage_percent', 0)

                print(f"✓ System metrics: CPU {cpu_percent:.1f}%, "
                      f"Memory {memory_percent:.1f}%, Disk {disk_usage:.1f}%")

                results['metrics_collected'] = 1
                results['system_metrics'] = metrics
            else:
                print("✗ Failed to collect system metrics")

        except Exception as e:
            print(f"✗ Error collecting system metrics: {e}")

        # Resource tracking
        print("\nTracking resource usage...")
        tracker = ResourceTracker()

        try:
            tracker.start_tracking("example_operation")

            # Simulate some work
            for i in range(1000):
                _ = i ** 2

            tracker.stop_tracking("example_operation")

            summary = tracker.get_summary()
            if summary:
                total_memory = summary.get('total_memory_mb', 0)
                peak_memory = summary.get('peak_memory_mb', 0)

                print(f"✓ Resource tracking: {total_memory:.2f} MB total, "
                      f"{peak_memory:.2f} MB peak memory")

                results['memory_tracked'] = 1
                results['resource_summary'] = summary

        except Exception as e:
            print(f"✗ Error in resource tracking: {e}")

        # Generate performance summary
        results['summary'] = {
            'total_operations': (results['functions_profiled'] +
                               results['benchmarks_run'] +
                               results['metrics_collected'] +
                               results['memory_tracked']),
            'performance_score': 'good' if results['functions_profiled'] > 0 else 'unknown',
            'monitoring_active': results['metrics_collected'] > 0
        }

        print_section("Performance Results")
        print_results(results['summary'], "Performance Monitoring Summary")

        runner.validate_results(results)
        runner.save_results(results)

        runner.complete("Performance monitoring example completed successfully")

    except Exception as e:
        runner.error("Example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

