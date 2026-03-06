# Release Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Release management including versioning, changelog generation, and release packaging. Provides automated release workflows with semantic versioning.

## Configuration Options

The release module operates with sensible defaults and does not require environment variable configuration. Version bump strategy (major, minor, patch) is set per-release. Changelog format and commit message parsing rules are configurable.

## PAI Integration

PAI agents interact with release through direct Python imports. Version bump strategy (major, minor, patch) is set per-release. Changelog format and commit message parsing rules are configurable.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep release

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/release/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
