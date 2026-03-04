# Performance Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Benchmark comparison, regression detection, and performance profiling. Provides performance_check_regression and performance_compare_benchmarks for quantitative analysis.

## Configuration Options

The performance module operates with sensible defaults and does not require environment variable configuration. Benchmark storage path and regression thresholds are configurable. Profiling depth and sampling rate are set per-session.

## MCP Tools

This module exposes 2 MCP tool(s):

- `performance_check_regression`
- `performance_compare_benchmarks`

## PAI Integration

PAI agents invoke performance tools through the MCP bridge. Benchmark storage path and regression thresholds are configurable. Profiling depth and sampling rate are set per-session.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep performance

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/performance/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
