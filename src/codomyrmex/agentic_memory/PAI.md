# Personal AI Infrastructure -- Agentic Memory Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Agentic Memory module provides persistent, structured memory for AI agents -- enabling learning across sessions, context continuity, and experience-based decision making. It is the primary module for the PAI Algorithm's LEARN phase, capturing work outcomes, state snapshots, and accumulated knowledge.

## PAI Capabilities

### Memory Operations

```python
from codomyrmex.agentic_memory import AgentMemory, MemoryType, MemoryImportance

agent = AgentMemory()

# Store a learning
mem = agent.remember(
    content="extract_method refactoring improved readability in large_function",
    memory_type=MemoryType.EPISODIC,
    importance=MemoryImportance.HIGH,
    metadata={"pattern": "extract_method", "confidence": 0.92}
)

# Recall relevant memories by query (ranked by relevance, recency, importance)
results = agent.recall("refactoring patterns", k=10)

# Search memories (public API)
results = agent.search("extract_method", k=5)

# Get formatted context string for prompt injection
context = agent.get_context("refactoring approaches", k=5)

# Forget a specific memory
agent.forget(memory_id=mem.id)
```

### Storage Backends

```python
from codomyrmex.agentic_memory.stores import InMemoryStore, JSONFileStore

# In-memory store for session-scoped memory
session_store = InMemoryStore()

# File-backed store for persistent memory across sessions
persistent_store = JSONFileStore(path="~/.codomyrmex/memory/")
```

### Specialised Memory Types

```python
from codomyrmex.agentic_memory import ConversationMemory, KnowledgeMemory, VectorStoreMemory

# Conversation memory tracks dialogue turns
convo = ConversationMemory()
convo.add_turn(role="user", content="Refactor this function", turn_number=1)
convo.add_turn(role="assistant", content="Here is the refactored version", turn_number=2)

# Knowledge memory stores verified facts
knowledge = KnowledgeMemory()
knowledge.add_fact("Python 3.12 supports type parameter syntax", source="PEP 695")

# Vector store memory with pluggable backend
vector = VectorStoreMemory()
vector.add("Important architectural decision about caching")
results = vector.search("caching strategy", k=3)
```

### Obsidian Vault Integration

```python
from codomyrmex.agentic_memory.obsidian import ObsidianVault

vault = ObsidianVault("~/Documents/MyVault")
note = vault.get_note("Architecture Decisions")
metadata = vault.metadata  # note_count, tag_count, link_count
tags = vault.get_all_tags()
```

### User Profile

```python
from codomyrmex.agentic_memory import UserProfile

profile = UserProfile()
# Tracks user preferences, coding style, and interaction patterns
# Informs agent behavior customization
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `AgentMemory` | Class | Primary memory interface with remember/recall/forget/search |
| `ConversationMemory` | Class | Specialised memory for dialogue turns |
| `KnowledgeMemory` | Class | Specialised memory for verified facts |
| `VectorStoreMemory` | Class | Memory with pluggable store backend |
| `InMemoryStore` | Class | Session-scoped in-memory storage |
| `JSONFileStore` | Class | Persistent file-backed storage |
| `UserProfile` | Class | User preference and behavior tracking |
| `Memory` | Model | Core memory data model |
| `MemoryType` | Enum | `episodic`, `semantic`, `procedural` |
| `MemoryImportance` | Enum | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `RetrievalResult` | Model | Search result with relevance, recency, importance scores |

## PAI Algorithm Phase Mapping

| Phase | Agentic Memory Contribution |
|-------|------------------------------|
| **OBSERVE** | `memory_search` MCP tool retrieves relevant past experiences for current context; `ObsidianVault` scans knowledge base notes |
| **THINK** | `recall()` returns ranked past outcomes to inform reasoning about approach selection; `RetrievalResult.combined_score` weights relevance, recency, and importance |
| **PLAN** | `get_context()` injects relevant memory into planning prompts; `KnowledgeMemory` provides verified facts for constraint-aware planning |
| **BUILD** | `ConversationMemory.add_turn()` captures build-phase dialogue for context continuity across multi-step construction |
| **EXECUTE** | `remember()` persists intermediate state during long-running agent workflows; `InMemoryStore` holds session-scoped execution context |
| **VERIFY** | `memory_search` retrieves past failure patterns to inform verification focus areas; known issues surface via importance ranking |
| **LEARN** | `memory_put` MCP tool captures work outcomes, patterns discovered, and lessons learned; `KnowledgeMemory.add_fact()` stores verified findings |

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `memory_put` | Store a new memory entry with content, optional type (episodic/semantic/procedural), and importance level | Safe |
| `memory_get` | Retrieve a specific memory by its unique ID | Safe |
| `memory_search` | Search memories by text query; returns top-k results ranked by combined relevance/recency/importance score | Safe |
| `rules_list_modules` | List all Codomyrmex module names that have a defined coding rule | Safe |
| `rules_get_module_rule` | Get the full coding rule (sections, raw content) for a specific module | Safe |
| `rules_get_applicable` | Get all applicable coding rules for a file path and/or module, ordered FILE_SPECIFIC → GENERAL | Safe |

## Agent Capabilities

| Agent Type | Agentic Memory Role |
|------------|---------------------|
| **Engineer** | Stores and retrieves refactoring patterns, build outcomes, and error resolutions |
| **Architect** | Persists architectural decisions and retrieves past design rationale via `KnowledgeMemory` |
| **QATester** | Recalls past failure patterns and regression history to focus verification effort |
| **Explore** | Searches memory for prior research findings and knowledge graph connections |

## Architecture Role

**Core Layer** -- Central memory infrastructure. Consumed by all agent modules. Uses `serialization/` for data persistence and integrates with `logging_monitoring/` for memory operation auditing. The Obsidian submodule provides read-only access to external knowledge bases.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Related**: [../logging_monitoring/PAI.md](../logging_monitoring/PAI.md) -- Operation auditing | [../serialization/PAI.md](../serialization/PAI.md) -- Data persistence
