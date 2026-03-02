# Codomyrmex Agents — src/codomyrmex/collaboration/knowledge

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides a namespace-isolated shared knowledge store (`SharedMemoryPool`) with ACL-gated access, configurable conflict resolution, and expertise-based query routing (`KnowledgeRouter`). Agents contribute domain-tagged knowledge entries and the router scores queries using tag overlap, domain match, and recency weighting.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `KnowledgeEntry` | Dataclass for knowledge items with agent provenance, domain, tags, and citation count |
| `models.py` | `ExpertiseProfile` | Agent expertise: domains with confidence scores, tags, and last-active timestamp |
| `models.py` | `QueryResult` | Query result container with entries, routing info, and search timing |
| `models.py` | `NamespaceACL` | Access control with owner/read/write/admin permission checks |
| `models.py` | `AccessLevel` | Enum: READ, WRITE, ADMIN |
| `models.py` | `ConflictStrategy` | Enum: LAST_WRITE_WINS, HIGHEST_CITATION, MERGE |
| `shared_pool.py` | `SharedMemoryPool` | Multi-namespace knowledge store with ACL enforcement and cross-namespace search |
| `shared_pool.py` | `NamespaceStats` | Per-namespace statistics: entry count, domain counts, total citations |
| `knowledge_router.py` | `KnowledgeRouter` | Routes queries to best-matching expert using composite scoring |

## Operating Contracts

- Namespaces must be created via `SharedMemoryPool.create_namespace()` before writing entries.
- `SharedMemoryPool.put()` returns `False` (not an exception) when the ACL denies write access.
- `SharedMemoryPool.get()` increments citation count on each successful read.
- `KnowledgeRouter.route()` returns `("", 0.0)` when no experts are registered.
- Conflict resolution applies `ConflictStrategy` on key collision: LAST_WRITE_WINS preserves citation count, HIGHEST_CITATION keeps the more-cited entry, MERGE combines tags.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library only (`time`, `dataclasses`, `enum`)
- **Used by**: `collaboration.swarm`, `collaboration.coordination`, higher-level orchestration agents

## Navigation

- **Parent**: [collaboration](../README.md)
- **Root**: [Root](../../../../README.md)
