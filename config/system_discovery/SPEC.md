# System Discovery Configuration Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Module discovery and health monitoring. Provides health_check, list_modules, and dependency_tree tools for understanding system state and module availability. This specification documents the configuration schema and constraints.

## Configuration Schema

The system_discovery module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Module discovery scans src/codomyrmex/ automatically. CI environment detection (GitHub Actions, Travis, Kubernetes) is automatic via environment variables. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Module discovery scans src/codomyrmex/ automatically. CI environment detection (GitHub Actions, Travis, Kubernetes) is automatic via environment variables.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/system_discovery/SPEC.md)
