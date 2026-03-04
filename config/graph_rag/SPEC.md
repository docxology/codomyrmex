# Graph RAG Configuration Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Graph-based Retrieval Augmented Generation combining knowledge graphs with LLM retrieval for enhanced question answering and knowledge exploration. This specification documents the configuration schema and constraints.

## Configuration Schema

The graph_rag module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Graph storage and retrieval parameters are configured per-instance. Embedding model and similarity threshold are adjustable. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Graph storage and retrieval parameters are configured per-instance. Embedding model and similarity threshold are adjustable.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/graph_rag/SPEC.md)
