# performance - API Specification

## Introduction

This document provides the complete API specification for the `performance` module.

## Module Overview

The `performance` module provides utilities for optimizing application execution, including lazy loading, intelligent caching, and comprehensive performance monitoring.

## Public API

### Main Functions

#### `function_name()`

**Description**: Executes a specific operation with performance tracking.

**Parameters**:
- `param1` (type): Description
- `param2` (type, optional): Description

**Returns**: Return type and description

**Example**:
```python
from codomyrmex.performance import function_name

result = function_name(param1="value")
```

## Classes

### `ClassName`

**Description**: Base class for performance-optimized components.

**Methods**:
- `method1()`: Description
- `method2(param)`: Description

## Constants

- `CONSTANT_NAME`: Description

## Exceptions

- `ModuleException`: Description

## Related Documentation

- [Module README](./README.md)
- [Usage Examples](../README.md#usage-examples) (See README for examples)
- [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md) (if applicable)

---

## Functions

### Function: `lazy_import(module_name: str, **kwargs) -> LazyLoader`

- **Description**: Creates a lazy loader for importing modules on-demand to improve startup performance.
- **Parameters**:
    - `module_name`: Name of the module to lazy load.
    - `**kwargs`: Additional configuration options.
- **Return Value**: LazyLoader object that imports the module when first accessed.
- **Errors**: Raises `ImportError` if the module cannot be found when accessed.

### Function: `cached_function(ttl_seconds: int = 300, max_size: int = 128, **kwargs) -> Callable`

- **Description**: Decorator that adds caching to functions to improve performance for expensive operations.
- **Parameters**:
    - `ttl_seconds`: Time-to-live for cached results (default: 300 seconds).
    - `max_size`: Maximum number of cached results (default: 128).
    - `**kwargs`: Additional cache configuration options.
- **Return Value**: Decorated function with caching capability.
- **Errors**: Raises `CacheError` for cache configuration issues.

## Classes

### CacheManager

**Description**: Manages multiple cache instances with intelligent invalidation and memory management.

#### Methods

**`__init__(default_ttl: int = 300, max_memory_mb: int = 100, **kwargs)`**
- Initialize cache manager with default settings.
- **Parameters**: `default_ttl`, `max_memory_mb`, cache configuration options.
- **Errors**: Raises `CacheError` for invalid configuration.

**`get_cache(name: str) -> Cache`**
- Retrieve or create a named cache instance.
- **Parameters**: `name`, cache identifier.
- **Return Value**: Cache instance for the given name.

**`clear_cache(name: str = None)`**
- Clear specific cache or all caches.
- **Parameters**: `name`, optional cache name (clears all if None).

**`get_stats() -> Dict`**
- Get cache performance statistics.
- **Return Value**: Dictionary with hit rates, memory usage, and performance metrics.

### LazyLoader

**Description**: Provides on-demand loading of modules and resources to improve application startup time.

#### Methods

**`__init__(loader: Callable, **kwargs)`**
- Initialize lazy loader with loading function.
- **Parameters**: `loader`, function that performs the actual loading.

**`load() -> Any`**
- Perform the actual loading operation.
- **Return Value**: Loaded resource or module.

**`is_loaded() -> bool`**
- Check if the resource has been loaded.
- **Return Value**: True if loaded, False otherwise.

### PerformanceMonitor (Optional)

**Description**: Monitors application performance metrics (requires psutil).

#### Methods

**`start_monitoring(interval_seconds: float = 1.0)`**
- Start performance monitoring with specified interval.
- **Parameters**: `interval_seconds`, monitoring frequency.

**`stop_monitoring()`**
- Stop performance monitoring.

**`get_metrics() -> Dict`**
- Get current performance metrics.
- **Return Value**: Dictionary with CPU, memory, disk, and network metrics.

**`get_report() -> str`**
- Generate performance report.
- **Return Value**: Formatted performance report string.

## Data Structures

### CacheConfig
Configuration for cache instances:
```python
{
    "ttl_seconds": <int>,
    "max_size": <int>,
    "eviction_policy": "lru|lfu|random",
    "compression": <bool>,
    "persistent": <bool>
}
```

### PerformanceMetrics
Performance monitoring data:
```python
{
    "timestamp": <datetime>,
    "cpu_percent": <float>,
    "memory_percent": <float>,
    "memory_mb": <float>,
    "disk_read_mb": <float>,
    "disk_write_mb": <float>,
    "network_rx_mb": <float>,
    "network_tx_mb": <float>
}
```

## Integration Examples

### Lazy Loading for Heavy Imports
```python
from codomyrmex.performance import lazy_import

# Lazy load heavy ML libraries
torch = lazy_import("torch")
transformers = lazy_import("transformers")

# Libraries are only imported when first accessed
model = torch.load("model.pth")  # Imports torch here
```

### Function Caching
```python
from codomyrmex.performance import cached_function

@cached_function(ttl_seconds=600, max_size=50)
def expensive_api_call(user_id: str) -> Dict:
    # Expensive database or API operation
    return get_user_data(user_id)

# First call performs operation and caches result
data1 = expensive_api_call("user123")

# Subsequent calls return cached result
data2 = expensive_api_call("user123")  # Returns cached data
```

### Performance Monitoring
```python
from codomyrmex.performance import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.start_monitoring(interval_seconds=5.0)

# Run performance-critical code
perform_expensive_operation()

# Get performance report
report = monitor.get_report()
print(report)

monitor.stop_monitoring()
```

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
