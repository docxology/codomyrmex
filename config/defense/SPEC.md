# Defense Configuration Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Threat detection, rate limiting, and response engine. Provides ActiveDefense for exploit detection, RabbitHole for attacker engagement, and Defense for orchestrating security responses. This specification documents the configuration schema and constraints.

## Configuration Schema

The defense module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Detection rules and response actions are configured through DetectionRule and ResponseAction models. Severity levels control escalation behavior. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Detection rules and response actions are configured through DetectionRule and ResponseAction models. Severity levels control escalation behavior.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/defense/SPEC.md)
