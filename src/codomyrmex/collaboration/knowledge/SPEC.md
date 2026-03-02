# Knowledge Sharing — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides namespace-isolated knowledge storage with ACL enforcement, configurable conflict resolution, and expertise-based query routing for multi-agent collaboration. Each agent operates in its own namespace; cross-namespace access is controlled via `NamespaceACL`.

## Architecture

Three layers: (1) `models.py` defines value types (`KnowledgeEntry`, `ExpertiseProfile`, `QueryResult`, `NamespaceACL`), (2) `SharedMemoryPool` manages per-agent namespaces with ACL-gated CRUD and global search, and (3) `KnowledgeRouter` wraps the pool with expertise scoring to route queries to the most relevant agent.

## Key Classes

### `SharedMemoryPool`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_namespace` | `agent_id: str, permissions: dict` | `None` | Create isolated namespace with ACL |
| `put` | `agent_id, key, value, domain, tags` | `bool` | Store entry; returns False on ACL denial |
| `get` | `agent_id, key, namespace` | `KnowledgeEntry or None` | Read with ACL check; increments citation count |
| `delete` | `agent_id, key` | `bool` | Remove entry from own namespace |
| `search_global` | `query_terms, domains, requesting_agent` | `list[KnowledgeEntry]` | Cross-namespace search sorted by citation count |
| `grant_access` | `owner, target_agent, level: AccessLevel` | `bool` | Grant read/write/admin to another agent |
| `namespace_stats` | `agent_id` | `NamespaceStats or None` | Entry count, domain distribution, total citations |

### `KnowledgeRouter`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register_expert` | `profile: ExpertiseProfile` | `None` | Register or update an agent's expertise |
| `route` | `query: str` | `(str, float)` | Best expert agent_id with confidence score |
| `query` | `question: str, domains: list` | `QueryResult` | Route and search in one call |
| `suggest_experts` | `query: str, n: int` | `list[(str, float)]` | Top-N experts ranked by composite score |

### `KnowledgeEntry`

| Field | Type | Description |
|-------|------|-------------|
| `key` | `str` | Unique knowledge identifier |
| `value` | `Any` | Knowledge content |
| `source_agent` | `str` | Contributing agent ID |
| `domain` | `str` | Knowledge domain |
| `tags` | `list[str]` | Searchable tags |
| `citation_count` | `int` | Reference count from other agents |

## Dependencies

- **Internal**: `collaboration.knowledge.models` (all data types)
- **External**: Standard library only (`time`, `dataclasses`, `enum`, `uuid`)

## Constraints

- `NamespaceACL.can_read()` always returns True for the namespace owner.
- `NamespaceACL.can_write()` requires WRITE or ADMIN level for non-owners.
- Router scoring: `tag_overlap * 0.4 + domain_score * 0.4 + recency * recency_weight`.
- Recency decay: `1 / (1 + age_hours / 24)` with configurable `recency_weight` (default 0.2).
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- ACL denial returns `False` / `None` (not exceptions) for graceful handling.
- `KnowledgeRouter.route()` returns `("", 0.0)` when no experts registered.
- All errors logged before propagation.
