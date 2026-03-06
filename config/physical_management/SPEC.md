# Physical Management Configuration Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Physical infrastructure and hardware management. Provides device inventory, sensor monitoring, and physical resource tracking for IoT and edge deployments. This specification documents the configuration schema and constraints.

## Configuration Schema

The physical_management module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Device registry and sensor polling intervals are configured per-device. Hardware profiles are defined through the management API. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Device registry and sensor polling intervals are configured per-device. Hardware profiles are defined through the management API.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/physical_management/SPEC.md)
