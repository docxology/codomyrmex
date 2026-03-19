# Codomyrmex Agents — src/codomyrmex/agentic_memory

**Version**: v1.4.0 | **Status**: Active | **Last Updated**: March 2026 (Sprint 34)

## Purpose

Agent memory systems with SQLite persistence, Obsidian integration, and memory consolidation. Sprint 34 extends `KnowledgeMemory` with `store / recall / merge_duplicates` methods and adds `KnowledgeItemIndex` — a dep-free incremental TF-IDF index. `KnowledgeMemory.recall` now supports an optional Ollama embedding re-ranking fallback (`nomic-embed-text`) for richer semantic search.

## Active Components

- `API_SPECIFICATION.md` — API reference
- `MCP_TOOL_SPECIFICATION.md` — MCP tool definitions
- `PAI.md` — Public API Interface
- `README.md` — Module overview
- `SPEC.md` — Module specification
- `__init__.py` — Package entry point (exports `KnowledgeItemIndex`)
- `cognilayer_bridge.py` — CogniLayer bridge
- `consolidation.py` — Memory consolidation
- `ki_index.py` — **NEW Sprint 34**: `KnowledgeItemIndex` incremental TF-IDF (add/remove/search/snippet)
- `mcp_tools.py` — MCP tool implementations
- `memory.py` — `AgentMemory`, `KnowledgeMemory` (Sprint 34: store/recall/merge_duplicates + Ollama re-rank)
- `models.py` — Data models: `Memory`, `MemoryType`, `RetrievalResult`
- `obsidian/` — Obsidian 19-module dual-mode integration
- `obsidian_bridge.py` — ObsidianMemoryBridge
- `py.typed` — PEP 561 marker
- `rules/` — `.cursorrules` governance system
- `sqlite_store.py` — `SQLiteStore` backing
- `stores.py` — `InMemoryStore`, `JSONFileStore`
- `user_profile.py` — Cross-session user profile

## Key Interfaces

- `memory.py` — `KnowledgeMemory`:
  - `store(title, body, tags, source_session_id)` → persists a structured KI
  - `recall(query, k, use_ollama, ollama_model)` → ranked semantic results (token-overlap + optional Ollama embedding)
  - `merge_duplicates(threshold)` → fold near-duplicates into older entries
- `ki_index.py` — `KnowledgeItemIndex`:
  - `add(memory_id, content)` → incremental TF-IDF update
  - `search(query, limit)` → scored `(memory_id, score)` list
  - `snippet(memory_id, length)` → short content preview
- `sqlite_store.py` — `SQLiteStore(path)` with CRUD and FTS5

## Agent Workflow Guidance (Sprint 34)

- Use `KnowledgeMemory.store(title, body, tags)` to persist any structured insight as a KI.
- Use `KnowledgeMemory.recall(query, k, use_ollama=True)` for semantic search; Ollama re-ranking is used when the local server is reachable, falls back silently.
- Use `KnowledgeItemIndex` as a lightweight pre-filter before embedding-based re-ranking for large knowledge bases.
- Use `KnowledgeMemory.merge_duplicates(threshold=0.85)` periodically to keep the KI store clean.
- Prefer `use_ollama=False` in unit tests to avoid network dependency.

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- **Zero-Mock Policy**: all tests use real `SQLiteStore` and real `KnowledgeMemory`. No mocks.

## Key Files

- `AGENTS.md` — This document
- `ki_index.py` — KnowledgeItemIndex (Sprint 34)
- `memory.py` — KnowledgeMemory with Ollama fallback
- `sqlite_store.py` — SQLiteStore backing
- `mcp_tools.py` — MCP tools

## Dependencies

Inherits dependencies from the parent module. See `pyproject.toml` for global dependencies.

## Development Guidelines

- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links

- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [../../../README.md](../../../README.md) - Main project documentation
