# Relations -- Specification

**Version**: v1.0.2 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Relations module provides CRM contact management, social network analysis, and Universal Object Reference (UOR) capabilities. It is an Application-Layer module with no upward dependants.

## Architecture

```
relations/
  __init__.py            # Re-exports all public types
  mcp_tools.py           # MCP tool: relations_score_strength
  visualization.py       # CRM visualization and export functions
  crm/
    crm.py               # Contact, ContactManager, Interaction
  network_analysis/
    __init__.py           # Exports SocialGraph, GraphMetrics
    graph.py              # Undirected weighted graph with metrics
  uor/
    __init__.py           # Exports UOR types
    engine.py             # PrismEngine, TriadicCoordinate
    entities.py           # UOREntity, UORRelationship (content-addressed)
```

Dependencies flow upward only. The module has no circular imports and avoids importing `data_visualization` directly.

## Functional Requirements

### CRM Subsystem

| Interface | Signature | Description |
|-----------|-----------|-------------|
| `Contact(name, email, ...)` | Constructor | Create a contact record with tags and interaction history |
| `ContactManager.add(contact)` | `-> None` | Register a contact |
| `ContactManager.search(query)` | `-> list[Contact]` | Case-insensitive search by name or email |
| `Interaction(type, notes, timestamp)` | Constructor | Record a communication event |

### Network Analysis Subsystem

| Interface | Signature | Description |
|-----------|-----------|-------------|
| `SocialGraph()` | Constructor | Create an empty undirected weighted graph |
| `graph.add_node(id, attributes)` | `-> None` | Add a node with optional metadata |
| `graph.add_edge(source, target, weight)` | `-> None` | Add undirected edge (default weight 1.0) |
| `graph.find_communities()` | `-> list[set[str]]` | Label-propagation community detection |
| `graph.calculate_centrality()` | `-> dict[str, float]` | Degree centrality scores in [0, 1] |
| `graph.shortest_path(source, target)` | `-> list[str]` | BFS shortest path; empty list if no path |
| `graph.get_influence_score(node_id)` | `-> float` | Weighted influence score in [0, 1] |
| `graph.neighbors(node_id)` | `-> dict[str, float]` | Neighbor IDs with edge weights |
| `graph.node_count` | `-> int` | Number of nodes (property) |
| `graph.edge_count` | `-> int` | Number of undirected edges (property) |
| `GraphMetrics.density(graph)` | `-> float` | Ratio of actual to possible edges |
| `GraphMetrics.clustering_coefficient(graph)` | `-> float` | Average local clustering coefficient |
| `GraphMetrics.degree_distribution(graph)` | `-> dict[int, int]` | Degree value to node count |

### UOR Subsystem

| Interface | Signature | Description |
|-----------|-----------|-------------|
| `PrismEngine(quantum)` | Constructor | Create engine at quantum level (0 = 8-bit, 1 = 16-bit, etc.) |
| `engine.triad(n)` | `-> TriadicCoordinate` | Compute datum, stratum, spectrum |
| `engine.correlate(a, b)` | `-> dict` | XOR-stratum Hamming distance and fidelity |
| `engine.fidelity(a, b)` | `-> float` | Shorthand fidelity in [0.0, 1.0] |
| `engine.verify()` | `-> bool` | Exhaustive algebraic coherence check |
| `engine.neg/bnot/xor/band/bor` | Primitive ops | Modular ring operations |
| `engine.succ/pred` | Derived ops | Increment/decrement via composed primitives |
| `UOREntity(name, entity_type, attributes)` | Dataclass | Content-addressed entity with SHA256 hash |
| `entity.set_attribute(key, value)` | `-> None` | Set attribute and recompute hash |
| `entity.similarity_score(other)` | `-> float` | Attribute overlap score in [0, 1] |
| `entity.to_dict()` | `-> dict` | Serialization including triadic coordinates |
| `UORRelationship(source_id, target_id, ...)` | Dataclass | Content-addressed relationship edge |
| `relationship.inverse()` | `-> UORRelationship` | Create the inverse relationship |

## Interface Contract (Module Exports)

All public types are re-exported from `__init__.py`:

```python
from codomyrmex.relations import (
    Contact, ContactManager, Interaction,          # CRM
    SocialGraph, GraphMetrics,                     # Network analysis
    UOREntity, UORRelationship, UORGraph,          # UOR entities
    PrismEngine, TriadicCoordinate,                # PRISM engine
    EntityManager, DerivationRecord, DerivationTracker,  # UOR management
)
```

## MCP Tool Specification

**Tool**: `relations_score_strength`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | `str` | Yes | -- | First entity ID |
| `target` | `str` | Yes | -- | Second entity ID |
| `interactions` | `list[dict]` | Yes | -- | Dicts with keys: type, timestamp, weight |
| `decay_function` | `str` | No | `"exponential"` | One of: exponential, linear, step, none |
| `half_life_days` | `float` | No | `30.0` | Half-life in days for exponential decay |

**Returns**: `{"status": "ok", "source": str, "target": str, "raw_score": float, "interaction_count": int}` on success, or `{"status": "error", "error": str}` on failure.

## Data Models

- **SocialGraph**: In-memory adjacency list (`dict[str, dict[str, float]]`). All edges are undirected (stored symmetrically).
- **UOREntity**: Content-addressed via SHA256 of `{name, entity_type, attributes}`. Hash auto-recomputes on mutation.
- **TriadicCoordinate**: Frozen dataclass with `datum` (byte tuple), `stratum` (popcount per byte), `spectrum` (active bit positions per byte).
- **PrismEngine**: Operates over Z/(2^(8*(quantum+1)))Z. Critical identity: `neg(bnot(x)) = x + 1 mod 2^n`.

## Error Handling

- `SocialGraph.shortest_path()` returns an empty list for missing nodes or unreachable targets. It does not raise.
- `PrismEngine.verify()` raises `RuntimeError` if any algebraic law is violated.
- `PrismEngine.__init__` raises `ValueError` for negative quantum levels.
- The MCP tool `relations_score_strength` catches all exceptions and returns an error dict rather than propagating.

## Performance

- Community detection (`find_communities`) uses label propagation capped at 50 iterations.
- `PrismEngine.verify()` at Q0 iterates all 256 states exhaustively; higher levels sample boundary and representative values.
- `SocialGraph.shortest_path()` uses BFS (O(V + E) time).

## Dependencies

- **Standard library only**: No external packages required.
- **Internal**: The `visualization.py` submodule imports from `crm.crm.ContactManager`.

## Testing Requirements

- All tests use real `SocialGraph`, `PrismEngine`, and `ContactManager` instances.
- **Zero-Mock Policy**: No mocking of graph operations, hash computations, or storage.
- Test location: `src/codomyrmex/tests/unit/relations/`
- Run: `uv run pytest src/codomyrmex/tests/unit/relations/ -v`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../SPEC.md)
