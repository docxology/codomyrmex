# Graph RAG Scripts

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Demo scripts for the `graph_rag` module, which provides graph-based retrieval-augmented generation combining knowledge graph traversal with LLM-powered query answering.

## Purpose

These scripts demonstrate graph RAG operations including knowledge graph construction, entity extraction, relationship mapping, and graph-augmented retrieval for improved LLM responses.

## Contents

| File | Description |
|------|-------------|
| `graph_rag_demo.py` | Demonstrates graph-based RAG pipeline with knowledge graph traversal |

## Usage

**Prerequisites:**
```bash
uv sync
```

**Run:**
```bash
uv run python scripts/graph_rag/graph_rag_demo.py
```

## Agent Usage

Agents building RAG pipelines should review this demo for the graph-augmented retrieval pattern. The script exercises knowledge graph construction and query-time graph traversal.

## Related Module

- Source: `src/codomyrmex/graph_rag/`

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Parent: scripts/](../README.md)
