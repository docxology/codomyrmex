# Technical Specification - Graph Rag

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.graph_rag`  
**Last Updated**: 2026-01-29

## 1. Purpose

Knowledge graph integration with RAG for structured knowledge retrieval and reasoning

## 2. Architecture

### 2.1 Components

```
graph_rag/
├── __init__.py          # Module exports and cli_commands()
├── models.py            # EntityType, RelationType, Entity, Relationship, GraphContext
├── graph.py             # KnowledgeGraph in-memory store
├── pipeline.py          # GraphRAGPipeline retrieval pipeline
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
└── PAI.md               # Personal AI context
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `codomyrmex`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.graph_rag
from codomyrmex.graph_rag import (
    EntityType,          # Enum: PERSON, ORGANIZATION, LOCATION, CONCEPT, EVENT, DOCUMENT, CUSTOM
    RelationType,        # Enum: IS_A, PART_OF, RELATED_TO, AUTHORED_BY, LOCATED_IN, OCCURRED_ON, REFERENCES, CUSTOM
    Entity,              # Dataclass: id, name, entity_type, properties, embedding
    Relationship,        # Dataclass: source_id, target_id, relation_type, properties, weight
    GraphContext,        # Dataclass: query, entities, relationships, paths, confidence
    KnowledgeGraph,      # In-memory graph store with entity/relationship CRUD and search
    GraphRAGPipeline,    # RAG pipeline enhanced with knowledge graph context retrieval
    cli_commands,        # Returns CLI command dict with "stats" and "query" subcommands
)

# Key files:
#   models.py   - EntityType, RelationType, Entity, Relationship, GraphContext
#   graph.py    - KnowledgeGraph
#   pipeline.py - GraphRAGPipeline

# Key class signatures:
class KnowledgeGraph:
    def add_entity(self, entity: Entity) -> None: ...
    def get_entity(self, entity_id: str) -> Entity | None: ...
    def add_relationship(self, relationship: Relationship) -> None: ...
    def get_neighbors(self, entity_id: str, direction: str = "both") -> list[Entity]: ...
    def get_relationships(self, entity_id: str, direction: str = "both") -> list[Relationship]: ...
    def find_path(self, start_id: str, end_id: str, max_depth: int = 5) -> list[str] | None: ...
    def subgraph(self, entity_ids: list[str], include_neighbors: bool = True) -> KnowledgeGraph: ...
    def search_entities(self, query: str, entity_type: EntityType | None = None, limit: int = 10) -> list[Entity]: ...

class GraphRAGPipeline:
    def __init__(self, graph: KnowledgeGraph, embedding_fn: Callable | None = None): ...
    def extract_entities(self, query: str) -> list[str]: ...
    def retrieve(self, query: str, max_entities: int = 10, include_neighbors: bool = True, max_depth: int = 2) -> GraphContext: ...
    def combine_context(self, graph_context: GraphContext, text_context: str) -> str: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Three-file split**: Models, graph store, and pipeline are separated into `models.py`, `graph.py`, and `pipeline.py` to allow independent use of the data layer without the pipeline dependency.
2. **In-memory graph**: `KnowledgeGraph` stores all entities and relationships in dictionaries and lists with `threading.Lock` for thread safety. No external graph database required.
3. **Simple text search**: `search_entities` uses substring matching (`in`) rather than embedding-based similarity, keeping the module dependency-free.

### 4.2 Limitations

- Search is substring-based only; embedding-based similarity search requires a user-supplied `embedding_fn` passed to `GraphRAGPipeline`
- `find_path` uses BFS with a configurable `max_depth` (default 5); very large graphs may need depth limits
- The `cli_commands` function references `graph.search(query)` which should be `graph.search_entities(query)`

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/graph_rag/
```

## 6. Future Considerations

- Pluggable persistence backends (e.g., Neo4j, NetworkX) behind the `KnowledgeGraph` interface
- Embedding-based nearest-neighbor entity search when `embedding_fn` is provided
- Weighted path finding (Dijkstra) using `Relationship.weight`
