# Performance Configuration Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Benchmark comparison, regression detection, and performance profiling. Provides performance_check_regression and performance_compare_benchmarks for quantitative analysis. This specification documents the configuration schema and constraints.

## Configuration Schema

The performance module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Benchmark storage path and regression thresholds are configurable. Profiling depth and sampling rate are set per-session. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Benchmark storage path and regression thresholds are configurable. Profiling depth and sampling rate are set per-session.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/performance/SPEC.md)
