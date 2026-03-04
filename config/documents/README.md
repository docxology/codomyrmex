# Documents Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Document I/O operations for multiple formats including markdown, JSON, PDF, YAML, XML, CSV, HTML, and plain text. Provides read, write, parse, validate, convert, merge, and split operations.

## Quick Configuration

```bash
export CODOMYRMEX_CACHE_DIR=""    # Directory for document cache storage (required)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `CODOMYRMEX_CACHE_DIR` | str | None | Directory for document cache storage |

## MCP Tools

This module exposes 3 MCP tool(s):

- `documents_read`
- `documents_write`
- `documents_convert`

## PAI Integration

PAI agents invoke documents tools through the MCP bridge. Cache directory defaults to system temp. Document format detection is automatic based on file extension.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep documents

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/documents/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
