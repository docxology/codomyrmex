# Dependency Injection Configuration Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Lightweight, thread-safe Inversion of Control (IoC) container for managing service lifetimes and constructor-based dependency injection. Foundation layer with no external dependencies. This specification documents the configuration schema and constraints.

## Configuration Schema

The dependency_injection module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Service lifetimes (SINGLETON, TRANSIENT, SCOPED) are set via @injectable decorator. Container is configured programmatically with no external config files. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Service lifetimes (SINGLETON, TRANSIENT, SCOPED) are set via @injectable decorator. Container is configured programmatically with no external config files.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/dependency_injection/SPEC.md)
