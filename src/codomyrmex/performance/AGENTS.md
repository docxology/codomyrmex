# Codomyrmex Agents — src/codomyrmex/performance

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Performance Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core module providing performance optimization and monitoring capabilities for the Codomyrmex platform. This module enables lazy loading, caching, resource tracking, and performance profiling to optimize startup time and runtime performance across all platform components.

The performance module serves as the optimization layer, ensuring efficient resource usage and providing visibility into system performance characteristics.

## Module Overview

### Key Capabilities
- **Lazy Loading**: Deferred module imports to improve startup time
- **Caching System**: Function result caching with configurable policies
- **Performance Monitoring**: Function execution timing and profiling
- **Resource Tracking**: Memory and CPU usage monitoring
- **Benchmarking**: Automated performance testing and comparison

### Key Features
- Decorator-based performance monitoring
- Configurable caching with TTL and size limits
- Lazy import system for faster application startup
- System resource monitoring and alerting
- Performance metrics collection and reporting

## Function Signatures

### Lazy Loading Functions

```python
def lazy_import(module_name: str, package: Optional[str] = None) -> LazyLoader
```

Create a lazy loader for a module that defers import until first access.

**Parameters:**
- `module_name` (str): Name of the module to import
- `package` (Optional[str]): Package name for relative imports

**Returns:** `LazyLoader` - Lazy loader object that imports on first attribute access

**Example:**
```python
# Instead of: import expensive_module
# Use: expensive_module = lazy_import('expensive_module')
```

```python
def get_lazy_loader(module_name: str, package: Optional[str] = None) -> LazyLoader
```

Get or create a lazy loader for a module, with caching to avoid duplicate loaders.

**Parameters:**
- `module_name` (str): Name of the module to import
- `package` (Optional[str]): Package name for relative imports

**Returns:** `LazyLoader` - Lazy loader object

### Caching Functions

```python
def cached_function(
    ttl: int = 300,
    max_size: int = 1000,
    key_function: Optional[Callable] = None,
    cache_manager: Optional[CacheManager] = None
) -> Callable
```

Decorator for caching function results to improve performance.

**Parameters:**
- `ttl` (int): Time-to-live for cache entries in seconds. Defaults to 300
- `max_size` (int): Maximum number of cached results. Defaults to 1000
- `key_function` (Optional[Callable]): Custom function to generate cache keys
- `cache_manager` (Optional[CacheManager]): Cache manager instance to use

**Returns:** `Callable` - Decorated function with caching enabled

**Example:**
```python
@cached_function(ttl=600, max_size=500)
def expensive_api_call(user_id: str) -> Dict:
    # This function's results will be cached
    return api_call(user_id)
```

```python
def clear_cache() -> None
```

Clear all cached function results.

**Returns:** None

```python
def get_cache_stats() -> dict[str, Any]
```

Get statistics about cache usage and performance.

**Returns:** `dict[str, Any]` - Cache statistics including hits, misses, size, etc.

### Performance Monitoring Functions

```python
def monitor_performance(
    function_name: Optional[str] = None, monitor: Optional[PerformanceMonitor] = None
) -> Callable
```

Decorator for monitoring function performance metrics.

**Parameters:**
- `function_name` (Optional[str]): Name to use for monitoring. Defaults to function name
- `monitor` (Optional[PerformanceMonitor]): Performance monitor instance. Defaults to global instance

**Returns:** `Callable` - Decorated function with performance monitoring

**Example:**
```python
@monitor_performance()
def slow_function():
    time.sleep(1)
    return "done"
```

```python
def performance_context(name: str, monitor: Optional[PerformanceMonitor] = None) -> ContextManager
```

Context manager for monitoring performance of code blocks.

**Parameters:**
- `name` (str): Name for the performance context
- `monitor` (Optional[PerformanceMonitor]): Performance monitor instance

**Returns:** Context manager for performance monitoring

**Example:**
```python
with performance_context("database_operation"):
    # Code to monitor
    result = db.query("SELECT * FROM users")
```

```python
def get_performance_stats(function_name: Optional[str] = None) -> dict[str, Any]
```

Get performance statistics for monitored functions.

**Parameters:**
- `function_name` (Optional[str]): Specific function name. If None, returns all stats

**Returns:** `dict[str, Any]` - Performance metrics including execution times, call counts, etc.

```python
def clear_performance_metrics() -> None
```

Clear all collected performance metrics.

**Returns:** None

```python
def export_performance_metrics(file_path: Union[str, Path]) -> None
```

Export performance metrics to a file.

**Parameters:**
- `file_path` (Union[str, Path]): Path to export metrics to

**Returns:** None

### System Monitoring Functions

```python
def monitor_system_resources(interval: float = 1.0) -> Iterator[dict[str, Any]]
```

Monitor system resource usage over time.

**Parameters:**
- `interval` (float): Monitoring interval in seconds. Defaults to 1.0

**Returns:** `Iterator[dict[str, Any]]` - Iterator yielding resource usage data

```python
def profile_memory_usage(func: Callable) -> Callable
```

Decorator for profiling memory usage of functions.

**Parameters:**
- `func` (Callable): Function to profile

**Returns:** `Callable` - Decorated function with memory profiling

```python
def get_system_metrics() -> dict[str, Any]
```

Get current system resource metrics.

**Returns:** `dict[str, Any]` - Current CPU, memory, disk, and network usage

### Resource Tracking Functions

```python
def track_memory_usage(func: Callable) -> Callable
```

Decorator for tracking memory usage of functions.

**Parameters:**
- `func` (Callable): Function to track

**Returns:** `Callable` - Decorated function with memory tracking

```python
def create_resource_report(results: List[ResourceTrackingResult]) -> Dict[str, Any]
```

Create a resource usage report from tracking results.

**Parameters:**
- `results` (List[ResourceTrackingResult]): Resource tracking results

**Returns:** `Dict[str, Any]` - Formatted resource usage report

```python
def benchmark_resource_usage(
    func: Callable,
    iterations: int = 10,
    *args,
    **kwargs
) -> Dict[str, Any]
```

Benchmark resource usage of a function over multiple iterations.

**Parameters:**
- `func` (Callable): Function to benchmark
- `iterations` (int): Number of benchmark iterations. Defaults to 10
- `*args`: Positional arguments to pass to function
- `**kwargs`: Keyword arguments to pass to function

**Returns:** `Dict[str, Any]` - Benchmark results with resource usage statistics

```python
def track_resource_usage(operation: str) -> ContextManager
```

Context manager for tracking resource usage of operations.

**Parameters:**
- `operation` (str): Name of the operation being tracked

**Returns:** Context manager for resource tracking

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `lazy_loader.py` – Lazy import system implementation
- `cache_manager.py` – Caching system with TTL and size management
- `performance_monitor.py` – Performance monitoring and profiling
- `resource_tracker.py` – System resource tracking utilities

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for performance monitoring
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Module dependencies (psutil, cachetools, etc.)

## Operating Contracts

### Universal Performance Protocols

All performance optimization within the Codomyrmex platform must:

1. **Minimize Overhead** - Performance monitoring should not significantly impact application performance
2. **Provide Value** - Optimizations must deliver measurable performance improvements
3. **Maintain Accuracy** - Performance metrics must accurately reflect system behavior
4. **Support Configuration** - Performance features should be configurable for different environments
5. **Enable Debugging** - Performance data should aid in identifying and resolving bottlenecks

### Module-Specific Guidelines

#### Lazy Loading
- Use lazy loading for optional or rarely-used modules
- Ensure lazy-loaded modules work transparently once imported
- Provide clear error messages for import failures
- Document lazy loading behavior for developers

#### Caching
- Configure appropriate TTL values based on data freshness requirements
- Set reasonable cache size limits to prevent memory issues
- Use appropriate cache keys for function result identification
- Clear caches when underlying data changes

#### Performance Monitoring
- Monitor critical paths and performance-sensitive operations
- Use appropriate sampling rates for resource monitoring
- Aggregate metrics for trend analysis and alerting
- Provide mechanisms to disable monitoring in production if needed

#### Resource Tracking
- Track resources for operations that may have performance impacts
- Set appropriate thresholds for resource usage alerts
- Provide both real-time and historical resource data
- Ensure resource tracking doesn't interfere with normal operations

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification (if applicable)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation