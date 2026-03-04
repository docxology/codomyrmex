# Data Visualization Configuration Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Chart and dashboard generation supporting bar, line, scatter, heatmap, histogram, pie, area, and box plot chart types. Includes report generators, Mermaid diagrams, and HTML export. This specification documents the configuration schema and constraints.

## Configuration Schema

The data_visualization module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Visual themes are configurable. Chart output formats include PNG, SVG, and HTML. Dashboard export produces self-contained HTML files. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Visual themes are configurable. Chart output formats include PNG, SVG, and HTML. Dashboard export produces self-contained HTML files.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/data_visualization/SPEC.md)
