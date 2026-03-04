# Static Analysis Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Code quality analysis, linting, and security scanning. Provides AST-based analysis, style checking, and vulnerability detection across Python source files.

## Configuration Options

The static_analysis module operates with sensible defaults and does not require environment variable configuration. Analysis rules and severity thresholds are configurable. Linting integrates with ruff and black for formatting checks.

## PAI Integration

PAI agents interact with static_analysis through direct Python imports. Analysis rules and severity thresholds are configurable. Linting integrates with ruff and black for formatting checks.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep static_analysis

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/static_analysis/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
