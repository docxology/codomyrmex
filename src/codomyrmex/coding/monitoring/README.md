# monitoring

## Signposting
- **Parent**: [coding](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Code execution monitoring including execution monitoring, metrics collection, and resource tracking. Provides comprehensive monitoring capabilities for code execution in sandboxed environments.

## Directory Contents
- `README.md` – File
- `__init__.py` – File
- `execution_monitor.py` – File
- `metrics_collector.py` – File
- `resource_tracker.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [coding](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.coding.monitoring import (
    ExecutionMonitor,
    MetricsCollector,
    ResourceMonitor,
)

# Monitor code execution
monitor = ExecutionMonitor()
with monitor.track_execution("my_function"):
    result = my_function()

# Collect metrics
collector = MetricsCollector()
metrics = collector.collect_metrics()
print(f"Execution time: {metrics.execution_time}s")
print(f"Memory usage: {metrics.memory_usage_mb}MB")

# Monitor resources
resource_monitor = ResourceMonitor()
snapshot = resource_monitor.get_snapshot()
print(f"CPU: {snapshot.cpu_percent}%")
print(f"Memory: {snapshot.memory_mb}MB")
```

