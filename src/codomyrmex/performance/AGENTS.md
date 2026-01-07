# Codomyrmex Agents — src/codomyrmex/performance

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Performance optimization utilities including lazy loading, intelligent caching, and comprehensive performance monitoring. Manages resource usage, caching, and lazy loading to ensure system responsiveness with execution time tracking, memory usage monitoring, and CPU profiling.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `cache_manager.py` – Function caching and memoization
- `lazy_loader.py` – Lazy module loading utilities
- `performance_monitor.py` – Performance monitoring and profiling
- `requirements.txt` – Project file
- `resource_tracker.py` – Resource usage tracking

## Key Classes and Functions

### PerformanceMonitor (`performance_monitor.py`)
- `PerformanceMonitor()` – Performance monitor tracking execution times and resource usage
- `monitor(func: Callable) -> Callable` – Decorator for monitoring function performance
- `track_execution(func: Callable, *args, **kwargs) -> tuple[Any, PerformanceMetrics]` – Track execution and return metrics
- `get_metrics() -> List[PerformanceMetrics]` – Get all collected performance metrics
- `export_metrics(file_path: Path, format: str = "json") -> None` – Export metrics to file
- `clear_metrics() -> None` – Clear all collected metrics

### PerformanceMetrics (`performance_monitor.py`)
- `PerformanceMetrics` (dataclass) – Container for performance metrics:
  - `function_name: str` – Name of the function
  - `execution_time: float` – Execution time in seconds
  - `memory_usage_mb: float` – Memory usage in MB
  - `cpu_percent: float` – CPU usage percentage
  - `timestamp: float` – Timestamp
  - `metadata: dict[str, Any]` – Additional metadata

### LazyLoader (`lazy_loader.py`)
- `LazyLoader(module_name: str, package: Optional[str] = None)` – Lazy loader for importing modules on-demand
- `__getattr__(name: str) -> Any` – Access module attributes, triggering import if needed
- `is_loaded() -> bool` – Check if module is loaded
- `load() -> Any` – Explicitly load the module

### Module Functions (`lazy_loader.py`)
- `lazy_import(module_name: str, package: Optional[str] = None) -> LazyLoader` – Create a lazy loader for a module

### CacheManager (`cache_manager.py`)
- `CacheManager(ttl_seconds: int = 300, max_size: int = 128)` – Manager for function caching
- `cached_function(ttl_seconds: int = 300, max_size: int = 128, **kwargs) -> Callable` – Decorator that adds caching to functions

### Module Functions (`__init__.py`)
- `lazy_import(module_name: str, package: Optional[str] = None) -> LazyLoader` – Create lazy loader
- `cached_function(ttl_seconds: int = 300, max_size: int = 128, **kwargs) -> Callable` – Function caching decorator

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation