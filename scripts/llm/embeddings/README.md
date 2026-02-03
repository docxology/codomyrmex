# Embeddings Scripts

**Module**: scripts/llm/embeddings  
**Status**: Active

## Overview

Scripts for text embedding generation and semantic similarity search.

## Scripts

| Script | API Required | Description |
|--------|-------------|-------------|
| `embeddings_demo.py` | No | Simulated embeddings and similarity demo |
| `openrouter_free_example.py` | Yes | LLM-based semantic similarity with OpenRouter |

## Quick Start

```bash
# Demo (no API key required)
python embeddings_demo.py

# Live example (requires API key)
export OPENROUTER_API_KEY='your-key-here'
python openrouter_free_example.py
```

## Features Demonstrated

- Pseudo-embedding generation (hash-based)
- Cosine similarity calculation
- Semantic search with ranking
- Embedding caching patterns
- LLM-based similarity scoring

## Navigation

- **Parent**: [scripts/llm](../README.md)
