# Performance Examples

Demonstrates performance monitoring and profiling using the Codomyrmex Performance module.

## Overview

The Performance module provides comprehensive performance monitoring including function profiling, benchmark execution, system resource tracking, and performance analysis.

## Examples

### Basic Usage (`example_basic.py`)

- Profile function execution time and memory usage
- Run performance benchmarks with multiple iterations
- Monitor system resource usage (CPU, memory, disk)
- Track memory allocations and resource consumption

**Tested Methods:**
- `profile_function()` - Function profiling (from `test_performance_comprehensive.py`)
- `run_benchmark()` - Benchmark execution (from `test_performance_comprehensive.py`)
- `get_system_metrics()` - System monitoring (from `test_performance.py`)

## Configuration

```yaml
performance:
  functions_to_profile:
    - name: sample_function
      args: [100]
    - name: fibonacci_recursive
      args: [20]

  benchmarks:
    - name: fibonacci_benchmark
      iterations: 3

  monitoring:
    enable_system_metrics: true
    enable_memory_tracking: true

profiling:
  memory:
    track_peak_usage: true
  sampling:
    interval_ms: 10
```

## Running

```bash
cd examples/performance
python example_basic.py
```

## Expected Output

The example will:
1. Profile specified functions for execution time and memory usage
2. Run performance benchmarks with statistical analysis
3. Collect current system resource metrics
4. Track resource usage during operations
5. Generate performance summary with recommendations
6. Save detailed profiling data to JSON file

## Performance Metrics

- **Execution Time**: Function and benchmark timing
- **Memory Usage**: Peak and average memory consumption
- **CPU Usage**: Processor utilization during execution
- **System Resources**: Overall system performance metrics
- **Benchmark Statistics**: Min, max, average, percentiles

## Use Cases

- **Code Optimization**: Identify performance bottlenecks
- **Benchmarking**: Compare algorithm implementations
- **Resource Monitoring**: Track system resource usage
- **Performance Regression**: Detect performance degradation
- **Capacity Planning**: Understand resource requirements

## Integration with Other Modules

The performance module integrates with:
- **Logging**: Performance event logging
- **Data Visualization**: Performance charts and graphs
- **CI/CD**: Automated performance testing
- **System Discovery**: Hardware performance profiling
- **Containerization**: Container resource monitoring

## Performance Profiling Features

- **Function Profiling**: Detailed function execution analysis
- **Memory Tracking**: Memory allocation and garbage collection monitoring
- **CPU Profiling**: Processor usage and hotspot identification
- **Benchmark Suite**: Standardized performance testing
- **Statistical Analysis**: Performance variability analysis

## Related Documentation

- [Module README](../../src/codomyrmex/performance/README.md)
- [Comprehensive Tests](../../testing/unit/test_performance_comprehensive.py)
- [Unit Tests](../../testing/unit/test_performance.py)

