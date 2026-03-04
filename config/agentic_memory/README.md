# Agentic Memory Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Persistent, searchable agent memory with typed retrieval. Provides Memory models, in-memory and file-backed stores, agent-level search/recall, and Obsidian vault integration.

## Configuration Options

The agentic_memory module operates with sensible defaults and does not require environment variable configuration. Memory storage defaults to in-memory. For persistent storage, configure a JSONFileStore with a file path. Obsidian vault integration requires a vault directory path.

## MCP Tools

This module exposes 3 MCP tool(s):

- `memory_put`
- `memory_get`
- `memory_search`

## PAI Integration

PAI agents invoke agentic_memory tools through the MCP bridge. Memory storage defaults to in-memory. For persistent storage, configure a JSONFileStore with a file path. Obsidian vault integration requires a vault directory path.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep agentic_memory

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/agentic_memory/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
