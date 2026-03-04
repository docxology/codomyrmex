# Static Analysis Configuration Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Code quality analysis, linting, and security scanning. Provides AST-based analysis, style checking, and vulnerability detection across Python source files. This specification documents the configuration schema and constraints.

## Configuration Schema

The static_analysis module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Analysis rules and severity thresholds are configurable. Linting integrates with ruff and black for formatting checks. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Analysis rules and severity thresholds are configurable. Linting integrates with ruff and black for formatting checks.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/static_analysis/SPEC.md)
