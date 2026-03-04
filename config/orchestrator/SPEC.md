# Orchestrator Configuration Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Workflow execution and scheduling orchestrator. Provides workflow dependency analysis, scheduler metrics, and execution engine for multi-step task automation. This specification documents the configuration schema and constraints.

## Configuration Schema

The orchestrator module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Workflow definitions use YAML or programmatic construction. Scheduler concurrency and retry policies are configurable. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Workflow definitions use YAML or programmatic construction. Scheduler concurrency and retry policies are configurable.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/orchestrator/SPEC.md)
