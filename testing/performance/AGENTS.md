# testing/performance - Performance Testing Suite

## Signposting
- **Parent**: [Parent](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This directory contains performance testing suites for measuring and validating the performance characteristics of Codomyrmex modules. It provides benchmarking, load testing, and performance regression detection.

## Directory Structure

### Performance Tests
- `test_benchmarking.py` - General benchmarking tests
- `test_module_performance.py` - Module-specific performance tests

### Test Infrastructure
- `conftest.py` - Pytest configuration for performance testing

## Agent Coordination

### Performance Testing Agents

**BenchmarkRunner**
- **Purpose**: Executes performance benchmarks and collects metrics
- **Inputs**: Test functions, configuration parameters, performance thresholds
- **Outputs**: Benchmark results, performance metrics, comparison reports
- **Key Functions**:
  - `run_benchmark(test_func: callable, iterations: int) -> BenchmarkResult` - Execute benchmark
  - `measure_performance(func: callable, **kwargs) -> PerformanceMetrics` - Performance measurement
  - `compare_baselines(current: dict, baseline: dict) -> ComparisonReport` - Performance comparison

**PerformanceAnalyzer**
- **Purpose**: Analyzes performance test results and identifies issues
- **Inputs**: Performance metrics, historical data, performance requirements
- **Outputs**: Performance reports, bottleneck analysis, optimization recommendations
- **Key Functions**:
  - `analyze_bottlenecks(metrics: dict) -> BottleneckReport` - Identify performance issues
  - `detect_regressions(current: dict, historical: list) -> RegressionReport` - Performance regression detection
  - `generate_performance_report(results: list) -> PerformanceSummary` - Comprehensive performance analysis

**LoadTester**
- **Purpose**: Performs load testing and stress testing
- **Inputs**: Load scenarios, system limits, test parameters
- **Outputs**: Load test results, capacity analysis, scalability reports
- **Key Functions**:
  - `execute_load_test(scenario: dict) -> LoadTestResult` - Run load test
  - `measure_system_limits(parameters: dict) -> CapacityReport` - Capacity testing
  - `analyze_scalability(metrics: list) -> ScalabilityReport` - Scalability analysis

## Operating Contracts

### Performance Testing Rules
1. **Controlled Environment**: Tests should run in controlled, reproducible environments
2. **Statistical Significance**: Results should be statistically significant
3. **Baseline Comparison**: Compare against established performance baselines
4. **Resource Monitoring**: Monitor system resources during testing

### Agent Communication
1. **Metric Collection**: Consistent metric collection and reporting formats
2. **Threshold Management**: Configurable performance thresholds and alerts
3. **Historical Tracking**: Maintain historical performance data for trend analysis

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

- **Testing Root**: [../README.md](../README.md) - Testing suite documentation
- **Testing Agents**: [../AGENTS.md](../AGENTS.md) - Test coordination
- **Performance Module**: [../../src/codomyrmex/performance/README.md](../../src/codomyrmex/performance/README.md) - Performance monitoring module

## Related Documentation

- **[AGENTS Root](../../AGENTS.md)** - Repository-level agent coordination
- **[Performance Module](../../src/codomyrmex/performance/AGENTS.md)** - Performance monitoring coordination