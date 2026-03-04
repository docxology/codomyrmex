# Graph RAG Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Graph-based Retrieval Augmented Generation combining knowledge graphs with LLM retrieval for enhanced question answering and knowledge exploration.

## Configuration Options

The graph_rag module operates with sensible defaults and does not require environment variable configuration. Graph storage and retrieval parameters are configured per-instance. Embedding model and similarity threshold are adjustable.

## PAI Integration

PAI agents interact with graph_rag through direct Python imports. Graph storage and retrieval parameters are configured per-instance. Embedding model and similarity threshold are adjustable.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep graph_rag

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/graph_rag/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
