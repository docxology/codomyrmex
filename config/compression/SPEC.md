# Compression Configuration Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Data compression utilities and archive handling supporting gzip, zlib, ZIP, and Zstandard formats. Provides configurable compression levels, stream-based compression, and parallel compression. This specification documents the configuration schema and constraints.

## Configuration Schema

The compression module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Compression level (1-9 for gzip/zlib, 1-22 for zstd) and algorithm are set per-operation. ParallelCompressor uses system CPU count by default. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Compression level (1-9 for gzip/zlib, 1-22 for zstd) and algorithm are set per-operation. ParallelCompressor uses system CPU count by default.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/compression/SPEC.md)
