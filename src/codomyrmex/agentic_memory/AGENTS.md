# AI Agent Guidelines - Agentic Memory

**Module**: `codomyrmex.agentic_memory`  
**Version**: v0.1.0  
**Status**: Active

## Purpose

Long-term agent memory systems for stateful, persistent agent interactions

## Agent Instructions

When working with this module:

### Key Patterns

1. **Import Convention**:

   ```python
   from codomyrmex.agentic_memory import AgentMemory, MemoryType
   ```

2. **Persistence**: Favor `JSONFileStore` for long-running agents.
3. **Hierarchy**: Use `EPISODIC` for specific events and `SEMANTIC` for general knowledge.

### Common Operations

- **Recall**: Retrieve memories via keyword or (if enabled) embedding search.
- **Pruning**: Automatically handles eviction when `max_memories` is reached.
- **Specialized**: Use `ConversationMemory` for human-ai dialogue tracking.

### Integration Points

- Integrates with: `None` (parent module)
- Dependencies: Listed in `__init__.py`

## File Reference

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports and initialization |
| `README.md` | User documentation |
| `SPEC.md` | Technical specification |

## Troubleshooting

Common issues and solutions:

1. **Issue**: Description
   **Solution**: Resolution steps
