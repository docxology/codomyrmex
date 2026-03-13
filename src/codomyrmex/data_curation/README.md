# data_curation

**Version**: v1.2.2 | **Status**: Active | **Last Updated**: March 2026

## Overview

MinHash-based near-duplicate detection and deduplication for text corpora. Implements the Broder (1997) MinHash algorithm with Locality-Sensitive Hashing (LSH) for sub-quadratic similarity search. Pure Python + NumPy, no external NLP dependencies.

## Key Components

| Component | File | Description |
| :--- | :--- | :--- |
| `MinHash` | `minhash.py` | MinHash signature generator (universal hashing, character n-gram shingling) |
| `LSHIndex` | `minhash.py` | LSH index for fast candidate pair generation via banding |
| `DataCurator` | `minhash.py` | End-to-end deduplication pipeline (hash → index → deduplicate) |

## Quick Start

```python
from codomyrmex.data_curation import DataCurator

curator = DataCurator(similarity_threshold=0.8)
unique_texts, stats = curator.deduplicate([
    "The quick brown fox jumps over the lazy dog",
    "The quick brown fox leaps over the lazy dog",  # near-duplicate
    "Completely different text about machine learning",
])
print(f"Kept {stats['unique_documents']}/{stats['total_documents']}")
```

## MCP Tools

| Tool | Description |
| :--- | :--- |
| `data_curation_deduplicate` | Deduplicate a text list using MinHash + LSH |
| `data_curation_similarity` | Estimate Jaccard similarity between two texts |

## Directory Contents

| File | Purpose |
| :--- | :--- |
| `minhash.py` | Core MinHash, LSHIndex, and DataCurator implementations (182 lines) |
| `mcp_tools.py` | MCP tool definitions (2 tools) |
| `__init__.py` | Public exports: `DataCurator`, `LSHIndex`, `MinHash` |

## Navigation

- **Parent Directory**: [codomyrmex](../README.md)
- **Documentation**: [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md) | [PAI.md](PAI.md) | [AGENTS.md](AGENTS.md) | [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Project Root**: [../../../README.md](../../../README.md)
