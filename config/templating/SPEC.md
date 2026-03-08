# Templating Configuration Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Template engines for code and document generation. Provides Jinja2-based templating with custom filters, template inheritance, and dynamic template resolution. This specification documents the configuration schema and constraints.

## Configuration Schema

The templating module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Template directories and Jinja2 environment settings are configurable. Custom filters and extensions can be registered per-environment. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Template directories and Jinja2 environment settings are configurable. Custom filters and extensions can be registered per-environment.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/templating/SPEC.md)
