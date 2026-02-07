# Data Lineage Module — Agent Coordination

## Purpose

Data provenance and lineage tracking.

## Key Capabilities

- **NodeType**: Types of lineage nodes.
- **EdgeType**: Types of lineage edges.
- **LineageNode**: A node in the lineage graph.
- **LineageEdge**: An edge connecting two nodes.
- **DataAsset**: A data asset with lineage information.
- `key()`: Get unique key.
- `to_dict()`: Convert to dictionary.
- `key()`: Get unique key.

## Agent Usage Patterns

```python
from codomyrmex.data_lineage import NodeType

# Agent initializes data lineage
instance = NodeType()
```

## Integration Points

- **Source**: [src/codomyrmex/data_lineage/](../../../src/codomyrmex/data_lineage/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k data_lineage -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
