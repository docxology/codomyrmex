# Docs Gen Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Documentation generation from Python source code. Provides API documentation extraction, searchable in-memory indices, and static documentation site configuration.

## Configuration Options

The docs_gen module operates with sensible defaults and does not require environment variable configuration. SiteGenerator output directory and template settings are configurable. SearchIndex rebuilds automatically when new modules are extracted.

## MCP Tools

This module exposes 2 MCP tool(s):

- `docs_gen_extract`
- `docs_gen_search`

## PAI Integration

PAI agents invoke docs_gen tools through the MCP bridge. SiteGenerator output directory and template settings are configurable. SearchIndex rebuilds automatically when new modules are extracted.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep docs_gen

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/docs_gen/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
