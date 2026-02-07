# Graph RAG Module — Agent Coordination

## Purpose

Knowledge graph-enhanced RAG with entity relationships.

## Key Capabilities

- **EntityType**: Types of entities in the knowledge graph.
- **RelationType**: Types of relationships in the knowledge graph.
- **Entity**: An entity in the knowledge graph.
- **Relationship**: A relationship between entities.
- **GraphContext**: Context retrieved from the knowledge graph.
- `key()`: Get unique key for this entity.
- `to_dict()`: Convert to dictionary.
- `key()`: Get unique key for this relationship.

## Agent Usage Patterns

```python
from codomyrmex.graph_rag import EntityType

# Agent initializes graph rag
instance = EntityType()
```

## Integration Points

- **Source**: [src/codomyrmex/graph_rag/](../../../src/codomyrmex/graph_rag/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k graph_rag -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
