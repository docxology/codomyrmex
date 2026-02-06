# Performance Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Performance profiling, benchmarking, and optimization.

## Key Features

- **Profiling** — CPU/memory profiling
- **Benchmarks** — Benchmark utilities
- **Timing** — Execution timing
- **Optimization** — Performance tips

## Quick Start

```python
from codomyrmex.performance import profile, benchmark

@profile
def slow_operation():
    return compute()

@benchmark(iterations=100)
def operation_to_test():
    return process()
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/performance/](../../../src/codomyrmex/performance/)
- **Parent**: [Modules](../README.md)
