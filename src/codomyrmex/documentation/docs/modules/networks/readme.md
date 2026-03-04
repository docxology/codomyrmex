# Networks Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Networks module provides lightweight, dependency-free graph data structures for
representing and analyzing networks within the codomyrmex ecosystem. It offers two
complementary graph implementations:

- **`Network`** (in `core.py`) -- An undirected graph with BFS/DFS traversal,
  connected-component detection, degree centrality, density metrics, and
  JSON-round-trip serialization.
- **`NetworkGraph`** (in `graph.py`) -- A directed graph with Dijkstra shortest-path
  search, auto-creating nodes on edge insertion, and an `@mcp_tool`-decorated
  `shortest_path` method for PAI integration.

Both implementations use generic-typed nodes (`Node[T]`) so callers can attach
arbitrary domain data to vertices without subclassing.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **THINK** | Analyze graph structure and compute centrality | Direct Python import |
| **OBSERVE** | Query network topology and shortest paths | Direct Python import |
| **BUILD** | Construct graph models for dependency analysis | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. The Architect agent imports `Network` and `NetworkGraph` during THINK to analyze module dependency graphs and identify critical paths.

## Installation

```bash
uv add codomyrmex          # networks is part of the core package
```

No optional extras are required. The module depends only on `logging_monitoring`
(Foundation layer) and the `model_context_protocol` decorator.

## Key Exports

The public API is re-exported from `__init__.py`:

| Export | Source | Type | Purpose |
|--------|--------|------|---------|
| `Network` | `core.py` | Class | Undirected graph with traversal and centrality |
| `Node` | `core.py` | Dataclass | Mutable node with `id`, generic `data`, and `attributes` dict |
| `Edge` | `core.py` | Dataclass | Undirected edge with `source`, `target`, `weight`, and `attributes` |

`graph.py` provides additional classes that are imported directly when needed:

| Export | Source | Type | Purpose |
|--------|--------|------|---------|
| `NetworkGraph` | `graph.py` | Class | Directed graph with Dijkstra shortest path |
| `Node` | `graph.py` | Frozen dataclass | Immutable, hashable node for directed graphs |
| `Edge` | `graph.py` | Frozen dataclass | Immutable directed edge with `data` dict |

## Quick Start

### Undirected graph with `Network`

```python
from codomyrmex.networks import Network

net = Network(name="module_deps")
net.add_node("logging", data="Foundation", layer=1)
net.add_node("agents", data="Core", layer=2)
net.add_node("orchestrator", data="Service", layer=3)

net.add_edge("agents", "logging", weight=1.0)
net.add_edge("orchestrator", "agents", weight=1.0)

# Traversal
print(net.bfs("logging"))           # ['logging', 'agents', 'orchestrator']
print(net.dfs("logging"))           # ['logging', 'agents', 'orchestrator']

# Connectivity
print(net.is_connected())           # True
print(net.connected_components())   # [{'logging', 'agents', 'orchestrator'}]
print(net.has_path("logging", "orchestrator"))  # True

# Metrics
print(net.degree_centrality())      # {'logging': 0.5, 'agents': 1.0, 'orchestrator': 0.5}
print(net.density)                  # 0.666...

# Serialization round-trip
data = net.to_dict()
restored = Network.from_dict(data)
assert restored.node_count == 3
```

### Directed graph with `NetworkGraph`

```python
from codomyrmex.networks.graph import NetworkGraph

g = NetworkGraph()
g.add_edge("A", "B", weight=2.0)
g.add_edge("B", "C", weight=3.0)
g.add_edge("A", "C", weight=10.0)

path = g.shortest_path("A", "C")   # [Node(A), Node(B), Node(C)] via Dijkstra
print(g.node_count)                 # 3
print(g.edge_count)                 # 3
```

## Network vs. NetworkGraph

| Feature | `Network` (`core.py`) | `NetworkGraph` (`graph.py`) |
|---------|----------------------|----------------------------|
| Directionality | Undirected (edges stored in both directions) | Directed (edges stored source-to-target only) |
| Node type | Mutable `Node[T]` with `attributes` dict | Frozen (hashable) `Node[T]` |
| Auto-create nodes | No -- raises `ValueError` on missing node | Yes -- `add_edge` creates missing nodes |
| Traversal | BFS, DFS, `has_path` | Dijkstra shortest path |
| Centrality | Degree centrality, density | Not provided |
| Components | `connected_components`, `is_connected` | Not provided |
| Serialization | `to_dict` / `from_dict` JSON round-trip | Not provided |
| MCP tool | None | `shortest_path` decorated with `@mcp_tool` |

## Relationship to the `relations` Module

The `networks` module provides **generic graph primitives** (nodes, edges, traversal,
shortest path). The `relations` module builds on higher-level domain concepts:

- **CRM contacts** (`Contact`, `ContactManager`, `Interaction`)
- **Social network analysis** (`SocialGraph`, `GraphMetrics`)
- **UOR entities** (`UOREntity`, `UORGraph`, `UORRelationship`, `PrismEngine`)

Use `networks` when you need a plain graph structure. Use `relations` when you need
domain-specific relationship management, CRM features, or UOR integration.

## Module Structure

```
networks/
  __init__.py        # Re-exports: Network, Node, Edge (from core.py)
  core.py            # Network class -- undirected graph with traversal and metrics
  graph.py           # NetworkGraph class -- directed graph with Dijkstra shortest path
  PAI.md             # PAI Algorithm integration guide
  AGENTS.md          # AI agent operational guide
  SPEC.md            # Technical specification
  README.md          # This file
```

## Dependencies

| Dependency | Layer | Purpose |
|-----------|-------|---------|
| `logging_monitoring` | Foundation | Structured logging via `get_logger` |
| `model_context_protocol` | Foundation | `@mcp_tool` decorator on `NetworkGraph.shortest_path` |

No external (pip) dependencies are required.

## Navigation

- **Extended Docs**: [docs/modules/networks/](../../../docs/modules/networks/)
- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
