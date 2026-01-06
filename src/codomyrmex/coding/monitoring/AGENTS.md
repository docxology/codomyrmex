# Codomyrmex Agents — code/monitoring

## Signposting
- **Parent**: [Code Module](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Siblings**: [execution](../execution/AGENTS.md), [sandbox](../sandbox/AGENTS.md), [review](../review/AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Monitoring submodule providing execution monitoring, resource tracking, and metrics collection for code execution operations.

## Key Components

- `execution_monitor.py` – Real-time execution monitoring
- `resource_tracker.py` – System resource tracking
- `metrics_collector.py` – Metrics aggregation and reporting

## Function Signatures

```python
def track(operation_name: str) -> ContextManager
def get_metrics() -> dict
```


## Active Components

### Core Files
- `__init__.py` – Package initialization
- Other module-specific implementation files

## Operating Contracts

### Universal Execution Protocols
1. **Non-Intrusive** - Monitoring should not affect execution performance
2. **Comprehensive** - Track all relevant metrics
3. **Structured Data** - Return metrics in consistent format
4. **Real-Time** - Provide real-time monitoring when needed

## Navigation Links
- **Parent**: [Code AGENTS](../AGENTS.md)
- **Human Documentation**: [README.md](README.md)
