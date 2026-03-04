# Privacy Configuration Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Privacy protection including data anonymization, PII detection, consent management, and privacy-preserving data processing. This specification documents the configuration schema and constraints.

## Configuration Schema

The privacy module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | PII detection patterns and anonymization strategies are configurable. Consent management rules are set per-data-category. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- PII detection patterns and anonymization strategies are configurable. Consent management rules are set per-data-category.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/privacy/SPEC.md)
