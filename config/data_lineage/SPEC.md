# Data Lineage Configuration Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Data lineage tracking through transformations with graph-based analysis. Provides LineageGraph for dependency visualization and ImpactAnalyzer for change impact assessment. This specification documents the configuration schema and constraints.

## Configuration Schema

The data_lineage module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Lineage graphs are built incrementally as data flows through transformations. Storage is in-memory by default. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Lineage graphs are built incrementally as data flows through transformations. Storage is in-memory by default.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/data_lineage/SPEC.md)
