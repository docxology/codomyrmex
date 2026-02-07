# Agentic Memory Module — Agent Coordination

## Purpose

Long-term agent memory with retrieval and persistence.

## Key Capabilities

- **MemoryType**: Types of agent memory.
- **MemoryImportance**: Importance levels for memories.
- **Memory**: A single memory unit.
- **RetrievalResult**: Result of memory retrieval.
- **MemoryStore**: Base class for memory storage backends.
- `age_hours()`: Get memory age in hours.
- `recency_score()`: Get recency score (decays over time).
- `access()`: Record an access to this memory.

## Agent Usage Patterns

```python
from codomyrmex.agentic_memory import MemoryType

# Agent initializes agentic memory
instance = MemoryType()
```

## Integration Points

- **Source**: [src/codomyrmex/agentic_memory/](../../../src/codomyrmex/agentic_memory/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k agentic_memory -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
