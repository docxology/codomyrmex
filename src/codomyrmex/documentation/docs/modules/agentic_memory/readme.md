# Agentic Memory

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Agentic Memory module provides persistent, structured memory for AI agents, enabling learning across sessions, context continuity, and experience-based decision making. It sits at the Foundation-to-Core boundary of the codomyrmex architecture, serving as the primary storage mechanism for agent knowledge, conversation history, and learned patterns. The module supports multiple storage backends (in-memory and JSON file-backed), typed memory models with importance levels, semantic search, and an integrated rules subsystem for coding governance via `.cursorrules` files.

## Architecture Overview

The module is organized around a layered memory abstraction: models define the data structures, stores provide backend persistence, and memory classes compose stores with domain-specific logic (conversations, knowledge bases, vector-backed retrieval). A separate `rules/` subpackage implements hierarchy-aware coding governance rule loading and resolution.

```
agentic_memory/
├── __init__.py              # Public API exports (19 classes/enums)
├── memory.py                # Core memory classes (AgentMemory, ConversationMemory, KnowledgeMemory, VectorStoreMemory)
├── models.py                # Data models (Memory, MemoryType, MemoryImportance, RetrievalResult)
├── stores.py                # Storage backends (InMemoryStore, JSONFileStore)
├── user_profile.py          # UserProfile tracking for per-user memory contexts
├── consolidation.py         # Memory consolidation and deduplication logic
├── cognilayer_bridge.py     # CogniLayer integration bridge
├── mcp_tools.py             # MCP tool definitions (memory_put, memory_get, memory_search)
├── rules/                   # Coding governance rules subsystem
│   ├── engine.py            # RuleEngine — hierarchy-aware rule resolution
│   ├── loader.py            # RuleLoader — parses .cursorrules files
│   ├── registry.py          # RuleRegistry — indexed access by module/extension
│   ├── models.py            # Rule, RuleSet, RulePriority, RuleSection
│   ├── mcp_tools.py         # rules_list_modules, rules_get_module_rule, rules_get_applicable
│   ├── general.cursorrules  # Global coding rules
│   ├── modules/             # 60 module-specific rule files
│   ├── cross-module/        # 8 cross-cutting rule files
│   └── file-specific/       # 6 file-type rule files
├── obsidian/                # Obsidian vault integration
└── tests/                   # Unit tests (Zero-Mock policy)
```

## PAI Integration

### Algorithm Phase Mapping

| Algorithm Phase | Role | Key Operations |
|----------------|------|---------------|
| OBSERVE | Retrieve past context, prior decisions, and learned patterns | `memory_search`, `memory_get` |
| THINK | Load architecture context and prior reasoning traces for decision support | `memory_search` |
| LEARN | Store new patterns, outcomes, and knowledge for future sessions | `memory_put` |

PAI's LEARN phase is primarily implemented via this module. `memory_put` stores insights after each Algorithm cycle; `memory_search` retrieves relevant prior context during OBSERVE and THINK phases. The Engineer subagent has full CRUD access; all agents use `memory_search` for context retrieval.

## Key Classes and Functions

### Core Classes

**`AgentMemory`** -- Primary memory store for AI agents with store, recall, and search capabilities.

```python
from codomyrmex.agentic_memory import AgentMemory, InMemoryStore

store = InMemoryStore()
memory = AgentMemory(store=store)

# Store a memory with importance and type
memory.store("User prefers concise responses", importance="high")

# Retrieve relevant memories by semantic search
results = memory.retrieve("user preferences", top_k=5)
```

**`ConversationMemory`** -- Conversation history with sliding window retention.

**`KnowledgeMemory`** -- Semantic knowledge base with structured retrieval for domain facts.

**`VectorStoreMemory`** -- Vector embedding-backed memory store for similarity-based retrieval.

**`InMemoryStore`** -- In-process volatile memory backend for session-scoped data.

**`JSONFileStore`** -- JSON file-backed persistent memory that survives process restarts.

### Data Models

**`Memory`** -- Base memory abstraction with content, type, importance, and timestamps.

**`MemoryType`** -- Enum categorizing memories: `EPISODIC`, `SEMANTIC`, `PROCEDURAL`, `WORKING`.

**`MemoryImportance`** -- Enum for importance levels: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.

**`RetrievalResult`** -- Memory retrieval result wrapping a Memory with relevance and combined scores.

### Rules Subsystem

**`RuleEngine`** -- Hierarchy-aware rule resolution engine that merges global, cross-module, module-specific, and file-specific rules.

**`RuleLoader`** -- Parser for `.cursorrules` files, extracting structured rule definitions.

**`RuleRegistry`** -- Indexed access to rules by module name or file extension.

**`UserProfile`** -- User-specific memory profile for personalized agent behavior.

## MCP Tools Reference

| Tool | Description | Parameters | Trust Level |
|------|-------------|------------|-------------|
| `memory_put` | Store a new memory entry with content, type, and importance | `content: str`, `memory_type: str = "episodic"`, `importance: str = "medium"` | Safe |
| `memory_get` | Retrieve a memory by its unique ID | `memory_id: str` | Safe |
| `memory_search` | Search memories by text query, returns ranked results | `query: str`, `k: int = 5` | Safe |

## Configuration

```bash
# No specific environment variables required for in-memory usage
# For persistent storage, JSONFileStore uses a configurable path:
export CODOMYRMEX_MEMORY_PATH="~/.codomyrmex/memory/"  # Default storage location
```

## Usage Examples

### Example 1: Session-Scoped Agent Memory

```python
from codomyrmex.agentic_memory import AgentMemory, InMemoryStore

store = InMemoryStore()
memory = AgentMemory(store=store)

# Store observations
memory.store("The user prefers concise responses", importance="high")
memory.store("Project uses Python 3.12 with uv", importance="medium")

# Search for relevant context
results = memory.retrieve("user preferences", top_k=5)
for result in results:
    print(f"[{result.importance}] {result.content} (score: {result.relevance_score:.2f})")
```

### Example 2: Persistent File-Backed Memory

```python
from codomyrmex.agentic_memory import AgentMemory, JSONFileStore

# Persistent across sessions
persistent_store = JSONFileStore(path="~/.codomyrmex/memory/")
memory = AgentMemory(store=persistent_store)

memory.store("Architecture decision: use event-driven pattern", importance="critical")
```

### Example 3: Coding Rules Resolution

```python
from codomyrmex.agentic_memory.rules import RuleEngine

engine = RuleEngine()
rules = engine.resolve("agents", file_extension=".py")
for rule in rules:
    print(f"[{rule.priority.name}] {rule.section}: {rule.content}")
```

## Error Handling

- `KeyError` raised when `memory_get` is called with a non-existent memory ID
- `ValueError` raised for invalid `MemoryType` or `MemoryImportance` values
- Storage backends raise `OSError` or `IOError` for file system access failures (JSONFileStore)

## Related Modules

- [`agents`](../agents/readme.md) -- Agent framework that consumes memory for context continuity
- [`cerebrum`](../cerebrum/readme.md) -- Case-based reasoning that complements memory with knowledge retrieval
- [`logging_monitoring`](../logging_monitoring/readme.md) -- Structured logging used by memory operations

## Navigation

- **Source**: [src/codomyrmex/agentic_memory/](../../../../src/codomyrmex/agentic_memory/)
- **API Spec**: [API_SPECIFICATION.md](../../../../src/codomyrmex/agentic_memory/API_SPECIFICATION.md)
- **Parent**: [All Modules](../README.md)
