# FPF Configuration Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Fetch-Parse-Format pipeline for extracting, parsing, and exporting content from URLs. Supports multiple output formats and content transformation. This specification documents the configuration schema and constraints.

## Configuration Schema

The fpf module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | URL fetching uses configurable timeout and retry settings. Output format (JSON, Markdown, plain text) is selected per-operation. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- URL fetching uses configurable timeout and retry settings. Output format (JSON, Markdown, plain text) is selected per-operation.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/fpf/SPEC.md)
