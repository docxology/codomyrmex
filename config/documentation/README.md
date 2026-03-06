# Documentation Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Documentation management, quality auditing, and website generation. Provides RASP compliance auditing, consistency checking, quality assessment, and static site building.

## Quick Configuration

```bash
export DOCS_PORT="3000"    # Port for documentation dev server
export DOCS_HOST="localhost"    # Host for documentation dev server
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `DOCS_PORT` | str | `3000` | Port for documentation dev server |
| `DOCS_HOST` | str | `localhost` | Host for documentation dev server |

## MCP Tools

This module exposes 2 MCP tool(s):

- `generate_module_docs`
- `audit_rasp_compliance`

## PAI Integration

PAI agents invoke documentation tools through the MCP bridge. Documentation website runs on configurable host and port. Quality thresholds for RASP compliance can be adjusted in audit configuration.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep documentation

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/documentation/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
