# Git Analysis Configuration Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Git history analysis, contributor statistics, and commit pattern detection. Provides 16 analysis tools for repository insights including hotspot detection and code churn. This specification documents the configuration schema and constraints.

## Configuration Schema

The git_analysis module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Analysis operates on the current git repository by default. Date ranges and file filters can be set per-analysis call. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Analysis operates on the current git repository by default. Date ranges and file filters can be set per-analysis call.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/git_analysis/SPEC.md)
