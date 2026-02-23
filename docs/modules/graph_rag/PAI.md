# Personal AI Infrastructure — Graph RAG Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Graph RAG module implements Graph-based Retrieval Augmented Generation — combining knowledge graph construction with LLM-powered retrieval to provide contextually rich, relationship-aware information to AI agents. It enables the PAI Algorithm's THINK phase with structured knowledge that goes beyond flat vector search.

## PAI Capabilities

### Knowledge Graph Construction

```python
from codomyrmex.graph_rag import KnowledgeGraph

graph = KnowledgeGraph()
# Build knowledge graphs from documents, code, and structured data
# Entities and relationships are extracted and stored
# Supports incremental updates as codebase evolves
```

### Graph RAG Pipeline

```python
from codomyrmex.graph_rag import GraphRAGPipeline

pipeline = GraphRAGPipeline()
# Retrieve context using graph traversal + vector similarity
# Combines structural relationships with semantic similarity
# Returns ranked, relationship-annotated context for LLM consumption
```

### Data Models

```python
from codomyrmex.graph_rag.models import Entity, Relationship, GraphDocument
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `KnowledgeGraph` | Class | Graph storage and traversal engine |
| `GraphRAGPipeline` | Class | End-to-end graph-based retrieval pipeline |
| `Entity` | Model | Node in the knowledge graph |
| `Relationship` | Model | Edge between entities |
| `GraphDocument` | Model | Document with extracted graph structure |

## PAI Algorithm Phase Mapping

| Phase | Graph RAG Contribution |
|-------|------------------------|
| **OBSERVE** | Extract entities and relationships from codebase and documentation |
| **THINK** | Traverse knowledge graph to find contextually relevant information for reasoning |
| **PLAN** | Use relationship data to understand module dependencies and plan changes |
| **LEARN** | Update knowledge graph with new entities and relationships discovered during work |

## Architecture Role

**Core Layer** — Central knowledge infrastructure consumed by `cerebrum/` (reasoning), `agents/` (context retrieval), `search/` (augmented search), and `agentic_memory/` (structured memory).

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
