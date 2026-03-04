# Tree Sitter Configuration Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Tree-sitter based code parsing and AST analysis. Provides language-agnostic syntax tree construction, node querying, and code structure extraction. This specification documents the configuration schema and constraints.

## Configuration Schema

The tree_sitter module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Language grammars are loaded on demand. Parser timeout and maximum file size are configurable. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Language grammars are loaded on demand. Parser timeout and maximum file size are configurable.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/tree_sitter/SPEC.md)
