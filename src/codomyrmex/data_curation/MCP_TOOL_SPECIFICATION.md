# Data Curation — MCP Tool Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `data_curation` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

The data curation module provides MinHash-based deduplication capabilities,
allowing AI agents to deduplicate text corpora and estimate document similarity.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `data_curation` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `data_curation_deduplicate`

**Description**: Deduplicate a list of texts using MinHash + LSH.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `texts` | `list` | Yes | -- | List of text strings to deduplicate |
| `threshold` | `float` | No | `0.8` | Jaccard similarity threshold (0.0-1.0) for considering two documents as near-duplicates |

**Returns**: `dict` — Dictionary with `unique_texts` (list of deduplicated strings) and `stats` (dict with `total_documents`, `unique_documents`, `duplicates_removed`, `duplicate_pairs_found`, `deduplication_ratio`).

**Example**:
```python
from codomyrmex.data_curation.mcp_tools import data_curation_deduplicate

result = data_curation_deduplicate(
    texts=["Hello world", "Hello world!", "Goodbye world"],
    threshold=0.8
)
```

---

### `data_curation_similarity`

**Description**: Estimate Jaccard similarity between two texts using MinHash.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text_a` | `str` | Yes | -- | First text document |
| `text_b` | `str` | Yes | -- | Second text document |

**Returns**: `dict` — Dictionary with `similarity` (float, rounded to 4 decimal places) and `are_similar` (bool, true if similarity >= 0.8).

**Example**:
```python
from codomyrmex.data_curation.mcp_tools import data_curation_similarity

result = data_curation_similarity(
    text_a="The quick brown fox jumps over the lazy dog",
    text_b="The quick brown fox leaps over the lazy dog"
)
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe — no trust check required
- **PAI Phases**: OBSERVE (assess corpus quality), THINK (evaluate data overlap)
- **Dependencies**: `data_curation.minhash.DataCurator`, `data_curation.minhash.MinHash`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
