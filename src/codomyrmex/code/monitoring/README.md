# Code Monitoring Submodule

## Signposting
- **Parent**: [Code Module](../README.md)
- **Siblings**: [execution](../execution/), [sandbox](../sandbox/), [review](../review/)
- **Key Artifacts**: [AGENTS.md](AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

The monitoring submodule provides execution monitoring, resource tracking, and metrics collection for code execution operations.

## Key Components

### execution_monitor.py
Real-time monitoring of code execution progress and status.

### resource_tracker.py
System resource tracking during code execution (CPU, memory, I/O).

### metrics_collector.py
Metrics aggregation and reporting for execution statistics.

## Usage

```python
from codomyrmex.code.monitoring import ResourceMonitor, ExecutionMonitor

# Monitor resource usage
monitor = ResourceMonitor()
with monitor.track("code_execution"):
    # Execute code...
    pass

# Get execution metrics
metrics = monitor.get_metrics()
```

## Navigation Links

- **Parent**: [Code Module](../README.md)
- **Code AGENTS**: [../AGENTS.md](../AGENTS.md)
- **Source Root**: [src/codomyrmex](../../README.md)
