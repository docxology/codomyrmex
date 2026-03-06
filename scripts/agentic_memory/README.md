# Agentic Memory Scripts

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Demo and utility scripts for the `agentic_memory` module, which provides persistent memory storage, retrieval, and semantic search for autonomous agents within the Codomyrmex ecosystem.

## Purpose

These scripts demonstrate agent memory lifecycle operations including storing context, retrieving memories by key, and performing semantic search across stored agent knowledge.

## Contents

| File | Description |
|------|-------------|
| `agentic_memory_demo.py` | Demonstrates memory put, get, and semantic search operations |

## Usage

**Prerequisites:**
```bash
uv sync
```

**Run:**
```bash
uv run python scripts/agentic_memory/agentic_memory_demo.py
```

## Agent Usage

Agents operating in this directory should understand the agentic memory storage model (key-value with semantic embeddings). The demo script exercises the `memory_put`, `memory_get`, and `memory_search` MCP tools.

## Related Module

- Source: `src/codomyrmex/agentic_memory/`
- MCP Tools: `memory_put`, `memory_get`, `memory_search`

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Parent: scripts/](../README.md)
