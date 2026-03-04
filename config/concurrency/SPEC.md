# Concurrency Configuration Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Distributed locks, semaphores, and synchronization primitives. Provides local locks, Redis-backed distributed locks, read-write locks, and dead letter queues. This specification documents the configuration schema and constraints.

## Configuration Schema

The concurrency module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Redis-backed locks require `redis` package (`uv sync --extra concurrency`). Local locks use threading primitives. Lock timeout and retry parameters are set per-lock. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Redis-backed locks require `redis` package (`uv sync --extra concurrency`). Local locks use threading primitives. Lock timeout and retry parameters are set per-lock.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/concurrency/SPEC.md)
