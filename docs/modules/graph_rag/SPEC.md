# Graph RAG — Functional Specification

**Module**: `codomyrmex.graph_rag`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Knowledge graph-enhanced RAG with entity relationships.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `EntityType` | Class | Types of entities in the knowledge graph. |
| `RelationType` | Class | Types of relationships in the knowledge graph. |
| `Entity` | Class | An entity in the knowledge graph. |
| `Relationship` | Class | A relationship between entities. |
| `GraphContext` | Class | Context retrieved from the knowledge graph. |
| `KnowledgeGraph` | Class | In-memory knowledge graph for entity and relationship storage. |
| `GraphRAGPipeline` | Class | RAG pipeline enhanced with knowledge graph context. |
| `key()` | Function | Get unique key for this entity. |
| `to_dict()` | Function | Convert to dictionary. |
| `key()` | Function | Get unique key for this relationship. |
| `to_dict()` | Function | Convert to dictionary. |
| `entity_names()` | Function | Get names of all entities. |

## 3. Dependencies

See `src/codomyrmex/graph_rag/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.graph_rag import EntityType, RelationType, Entity, Relationship, GraphContext
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k graph_rag -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/graph_rag/)
