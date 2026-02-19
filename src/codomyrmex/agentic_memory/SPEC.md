# Technical Specification - Agentic Memory

**Module**: `codomyrmex.agentic_memory`  
**Version**: v0.1.7  
**Last Updated**: 2026-01-29

## 1. Purpose

Long-term agent memory systems for stateful, persistent agent interactions

## 2. Architecture

### 2.1 Components

```
agentic_memory/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `codomyrmex`

## 3. Interfaces

### 3.1 Public API

```python
# Core Classes
from codomyrmex.agentic_memory import (
    AgentMemory,       # Main memory system
    Memory,            # Single memory unit
    MemoryType,        # EPISODIC, SEMANTIC, PROCEDURAL, WORKING
    MemoryImportance,  # LOW, MEDIUM, HIGH, CRITICAL
    InMemoryStore,     # Default storage
    JSONFileStore,     # Persistent storage
)

# Implementation details
# Each memory has recency_score, importance_score, and combined_score.
# AgentMemory.recall(query, k=5) provides the ranking logic.
```

### 3.2 Configuration

Environment variables:

- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Decision 1**: Rationale

### 4.2 Limitations

- Known limitation 1
- Known limitation 2

## 5. Testing

```bash
# Run tests for this module
pytest tests/agentic_memory/
```

## 6. Future Considerations

### Common Operations

- **Storage**: Choose between `InMemoryStore` (volatile) or `JSONFileStore` (persistent).
- **Remembering**: Use `memory.remember(content, ...)` to store information.
- **Recalling**: Use `memory.recall(query, k=N)` to retrieve the top N relevant memories.
- **LLM Context**: Use `memory.get_context(query)` to get a pre-formatted string for LLM prompts.

- Enhancement 1
- Enhancement 2
