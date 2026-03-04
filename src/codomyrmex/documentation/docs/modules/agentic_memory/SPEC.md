# Agentic Memory -- Technical Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Memory Storage
- The system shall support storing memory entries with content (str), type (MemoryType enum), and importance (MemoryImportance enum).
- Each memory entry shall receive a unique identifier upon creation.
- Memory entries shall include creation and last-accessed timestamps.

### FR-2: Memory Retrieval
- The system shall support retrieval of individual memories by unique ID.
- The system shall support semantic search across all stored memories, returning results ranked by relevance.
- Search results shall include relevance scores and combined scores.

### FR-3: Storage Backends
- The system shall provide an in-memory (volatile) storage backend for session-scoped data.
- The system shall provide a JSON file-backed (persistent) storage backend that survives process restarts.
- All backends shall implement a common interface: `get()`, `set()`, `delete()`, `search()`.

### FR-4: Memory Types
- The system shall support four memory types: EPISODIC (event-based), SEMANTIC (factual knowledge), PROCEDURAL (how-to), and WORKING (temporary scratch).

### FR-5: Importance Levels
- The system shall support four importance levels: LOW, MEDIUM, HIGH, CRITICAL.
- Importance levels shall influence retrieval ranking.

### FR-6: Rules Subsystem
- The system shall load and parse `.cursorrules` files from a hierarchical directory structure.
- Rule resolution shall follow priority: file-specific > module-specific > cross-module > general.
- Rules shall be indexable by module name and file extension.

## Interface Contracts

### Memory Model

```python
class Memory:
    id: str                    # UUID
    content: str               # Memory content text
    memory_type: MemoryType    # EPISODIC | SEMANTIC | PROCEDURAL | WORKING
    importance: MemoryImportance  # LOW | MEDIUM | HIGH | CRITICAL
    created_at: datetime
    last_accessed: datetime
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]: ...
```

### RetrievalResult Model

```python
class RetrievalResult:
    memory: Memory
    relevance_score: float     # 0.0 to 1.0
    combined_score: float      # Weighted combination of relevance and importance
```

### Store Interface

```python
class Store(Protocol):
    def get(self, key: str) -> Memory | None: ...
    def set(self, key: str, memory: Memory) -> None: ...
    def delete(self, key: str) -> bool: ...
    def search(self, query: str, k: int = 5) -> list[RetrievalResult]: ...
```

### MCP Tool Signatures

```python
def memory_put(content: str, memory_type: str = "episodic", importance: str = "medium") -> dict[str, Any]
def memory_get(memory_id: str) -> dict[str, Any] | None
def memory_search(query: str, k: int = 5) -> list[dict[str, Any]]
```

## Non-Functional Requirements

### NFR-1: Performance
- In-memory store operations shall complete in O(1) for get/set/delete.
- Search operations shall complete in O(n) where n is the number of stored memories.
- JSONFileStore shall cache data in memory and flush to disk asynchronously.

### NFR-2: Reliability
- JSONFileStore shall handle concurrent access gracefully (file locking).
- Memory data shall not be corrupted on unexpected process termination.

### NFR-3: Extensibility
- New storage backends shall be addable by implementing the Store protocol.
- New memory types and importance levels shall be addable via enum extension.

## Testing Requirements

- All tests follow the Zero-Mock policy -- no unittest.mock, MagicMock, or monkeypatch.
- Tests use real InMemoryStore and JSONFileStore instances.
- Minimum test coverage: memory CRUD operations, search ranking, rules resolution hierarchy.

## Navigation

- **Source**: [src/codomyrmex/agentic_memory/](../../../../src/codomyrmex/agentic_memory/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
