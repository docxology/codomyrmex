# Personal AI Infrastructure — Performance Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Performance module provides PAI integration for profiling and optimization.

## PAI Capabilities

### Profiling

Profile code:

```python
from codomyrmex.performance import profile

@profile
def slow_operation():
    return compute()
```

### Benchmarking

Benchmark functions:

```python
from codomyrmex.performance import benchmark

@benchmark(iterations=100)
def operation_to_test():
    return process()
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `profile` | Profile code |
| `benchmark` | Benchmark |
| `MemoryTracker` | Memory usage |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
