# RAG Scripts

**Module**: scripts/llm/rag  
**Status**: Active

## Overview

Scripts for Retrieval-Augmented Generation (RAG) pipelines.

## Scripts

| Script | API Required | Description |
|--------|-------------|-------------|
| `rag_demo.py` | No | Complete RAG pipeline demo |
| `openrouter_free_example.py` | Yes | Real RAG with OpenRouter |

## Quick Start

```bash
# Demo (no API key required)
python rag_demo.py

# Live example (requires API key)
export OPENROUTER_API_KEY='your-key-here'
python openrouter_free_example.py
```

## Features Demonstrated

- Document chunking
- Simple vector store
- Similarity search
- Context retrieval
- Augmented prompt construction
- Citation generation

## Navigation

- **Parent**: [scripts/llm](../README.md)
