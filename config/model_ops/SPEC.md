# Model Ops Configuration Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

ML model operations including versioning, deployment, monitoring, and feature store integration. Provides model lifecycle management and experiment tracking. This specification documents the configuration schema and constraints.

## Configuration Schema

The model_ops module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Model registry storage path and experiment tracking backend are configurable. Feature store integration requires feature_store module. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Model registry storage path and experiment tracking backend are configurable. Feature store integration requires feature_store module.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/model_ops/SPEC.md)
