# Codomyrmex Agents — src/codomyrmex/performance

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Performance module provides comprehensive performance optimization utilities for Codomyrmex, including lazy loading to improve startup time, persistent caching to avoid redundant computations, performance monitoring to track execution metrics, and resource tracking for memory and CPU analysis. It enables fine-grained control over application performance through decorators, context managers, and utility classes.

## Active Components

### Performance Monitoring

- `performance_monitor.py` - Performance monitoring and profiling
  - Key Classes: `PerformanceMonitor`, `PerformanceMetrics`, `SystemMonitor`, `SystemMetrics`
  - Key Functions: `monitor_performance()`, `profile_function()`, `profile_memory_usage()`, `get_system_metrics()`, `track_resource_usage()`

### Caching

- `cache_manager.py` - In-memory and disk-based caching with TTL support
  - Key Classes: `CacheManager`
  - Key Functions: `cached_function()`, `clear_cache()`, `get_cache_stats()`

### Lazy Loading

- `lazy_loader.py` - Deferred module imports for improved startup time
  - Key Classes: `LazyLoader`
  - Key Functions: `lazy_import()`, `get_lazy_loader()`, `lazy_function()`
  - Pre-configured: `matplotlib`, `numpy`, `pandas`, `seaborn`, `plotly`, `openai`, `anthropic`, `google_genai`, `docker`, `git`

### Resource Tracking

- `resource_tracker.py` - Detailed resource usage monitoring
  - Key Classes: `ResourceTracker`, `ResourceSnapshot`, `ResourceTrackingResult`
  - Key Functions: `track_memory_usage()`, `create_resource_report()`, `benchmark_resource_usage()`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `PerformanceMonitor` | performance_monitor | Track execution times and resource usage |
| `PerformanceMetrics` | performance_monitor | Container for performance metrics data |
| `SystemMonitor` | performance_monitor | System-level resource monitoring |
| `SystemMetrics` | performance_monitor | System metrics dataclass |
| `monitor_performance()` | performance_monitor | Decorator for monitoring function performance |
| `profile_function()` | performance_monitor | Alias for monitor_performance |
| `profile_memory_usage()` | performance_monitor | Decorator to profile memory usage |
| `get_system_metrics()` | performance_monitor | Get comprehensive system metrics |
| `track_resource_usage()` | performance_monitor | Context manager for resource tracking |
| `CacheManager` | cache_manager | Persistent caching with memory and disk storage |
| `cached_function()` | cache_manager | Decorator for caching function results |
| `clear_cache()` | cache_manager | Clear the global cache |
| `get_cache_stats()` | cache_manager | Get cache statistics |
| `LazyLoader` | lazy_loader | Deferred module import class |
| `lazy_import()` | lazy_loader | Create a lazy loader for a module |
| `get_lazy_loader()` | lazy_loader | Get or create a lazy loader (singleton pattern) |
| `lazy_function()` | lazy_loader | Create a lazy-loaded function |
| `ResourceTracker` | resource_tracker | Advanced resource tracking with sampling |
| `ResourceSnapshot` | resource_tracker | Point-in-time resource usage snapshot |
| `ResourceTrackingResult` | resource_tracker | Complete tracking result with statistics |
| `create_resource_report()` | resource_tracker | Create comprehensive resource report |
| `benchmark_resource_usage()` | resource_tracker | Benchmark function over multiple iterations |

## Operating Contracts

1. **Logging**: All components use `logging_monitoring` for structured logging
2. **psutil Dependency**: Resource monitoring requires `psutil`; graceful fallback if unavailable
3. **Cache Storage**: Caches stored in memory with LRU eviction and persistent disk backup
4. **Cache TTL**: Default time-to-live is 3600 seconds (1 hour), configurable per function
5. **Thread Safety**: ResourceTracker uses threading locks for concurrent access
6. **Decorator Patterns**: Performance decorators preserve function signatures via `@functools.wraps`
7. **Global Instances**: Module provides global instances (`_performance_monitor`, `_cache_manager`) for convenience

## Integration Points

- **logging_monitoring** - All performance functions log via centralized logger
- **data_visualization** - Uses `@monitor_performance` decorator on plotting functions
- **agents** - Performance monitoring for agent operations
- **llm** - Caching for expensive LLM API calls
- **All modules** - Lazy loading available for deferred imports

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| logging_monitoring | [../logging_monitoring/AGENTS.md](../logging_monitoring/AGENTS.md) | Logging infrastructure |
| cache | [../cache/AGENTS.md](../cache/AGENTS.md) | Additional caching utilities |
| metrics | [../metrics/AGENTS.md](../metrics/AGENTS.md) | Metrics collection |
| telemetry | [../telemetry/AGENTS.md](../telemetry/AGENTS.md) | Telemetry and observability |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tool specifications
