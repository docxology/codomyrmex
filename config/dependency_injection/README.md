# Dependency Injection Configuration

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Lightweight, thread-safe Inversion of Control (IoC) container for managing service lifetimes and constructor-based dependency injection. Foundation layer with no external dependencies.

## Configuration Options

The dependency_injection module operates with sensible defaults and does not require environment variable configuration. Service lifetimes (SINGLETON, TRANSIENT, SCOPED) are set via @injectable decorator. Container is configured programmatically with no external config files.

## PAI Integration

PAI agents interact with dependency_injection through direct Python imports. Service lifetimes (SINGLETON, TRANSIENT, SCOPED) are set via @injectable decorator. Container is configured programmatically with no external config files.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep dependency_injection

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/dependency_injection/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
