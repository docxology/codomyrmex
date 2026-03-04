# Testing Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Testing infrastructure and utilities for the Codomyrmex test suite. Provides test runners, fixtures, and testing helper functions.

## Quick Configuration

```bash
export CODOMYRMEX_TEST_MODE="true"    # Enables test mode for safe execution
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `CODOMYRMEX_TEST_MODE` | str | `true` | Enables test mode for safe execution |

## PAI Integration

PAI agents interact with testing through direct Python imports. Test mode is automatically enabled when running under pytest. Test markers (unit, integration, slow, etc.) are defined in pytest.ini.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep testing

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/testing/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
