# Dark Configuration Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

PDF dark mode utilities providing inversion, brightness, contrast, and sepia filters for PDF documents. Supports preset modes and custom filter chains. This specification documents the configuration schema and constraints.

## Configuration Schema

The dark module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Requires optional dependencies: `uv sync --extra dark`. Filter parameters (inversion level, brightness, contrast) are set per-document. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Requires optional dependencies: `uv sync --extra dark`. Filter parameters (inversion level, brightness, contrast) are set per-document.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/dark/SPEC.md)
