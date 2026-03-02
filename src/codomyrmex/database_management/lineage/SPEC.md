# Lineage — Functional Specification

## Overview

The lineage submodule implements a directed graph for tracking data provenance across datasets, transformations, models, and artifacts. It supports upstream/downstream traversal, path finding, and impact analysis with risk classification.

## Architecture

```
lineage/
  models.py   -- NodeType, EdgeType, LineageNode, LineageEdge, DataAsset
  graph.py    -- LineageGraph (thread-safe directed graph with DFS traversal)
  tracker.py  -- LineageTracker (high-level registration API), ImpactAnalyzer
  __init__.py -- Re-exports
```

The module follows a layered design: `models.py` defines data structures, `graph.py` provides the graph engine, and `tracker.py` offers domain-specific operations on top.

## Key Classes

### LineageGraph

| Method | Signature | Behaviour |
|--------|-----------|-----------|
| `__init__` | `()` | Initialises empty node/edge dictionaries with `threading.Lock` |
| `add_node` | `(node: LineageNode) -> None` | Registers a node by ID; thread-safe |
| `add_edge` | `(edge: LineageEdge) -> None` | Adds a directed edge; appends to adjacency lists; thread-safe |
| `get_node` | `(node_id: str) -> LineageNode \| None` | Looks up node by ID |
| `get_upstream` | `(node_id: str, max_depth: int \| None) -> list[LineageNode]` | DFS traversal of reverse edges; returns all ancestor nodes within optional depth bound |
| `get_downstream` | `(node_id: str, max_depth: int \| None) -> list[LineageNode]` | DFS traversal of forward edges; returns all descendant nodes within optional depth bound |
| `get_path` | `(from_id: str, to_id: str) -> list[LineageNode]` | Finds a path between two nodes using DFS; returns empty list if no path exists |
| `to_dict` | `() -> dict` | Serializes nodes and edges to a dictionary |

### LineageTracker

| Method | Signature | Behaviour |
|--------|-----------|-----------|
| `__init__` | `(graph: LineageGraph \| None)` | Wraps or creates a `LineageGraph` |
| `register_dataset` | `(id, name, location, metadata) -> LineageNode` | Creates a `DATASET` node with location in metadata |
| `register_transformation` | `(id, name, inputs, outputs, metadata) -> LineageNode` | Creates a `TRANSFORMATION` node; adds `INPUT_TO` edges from each input and `PRODUCED_BY` edges to each output |
| `get_origin` | `(node_id: str) -> list[LineageNode]` | Returns root datasets (datasets with no upstream) reachable from the given node |
| `get_impact` | `(node_id: str) -> list[LineageNode]` | Delegates to `graph.get_downstream` |

### ImpactAnalyzer

| Method | Signature | Behaviour |
|--------|-----------|-----------|
| `__init__` | `(graph: LineageGraph)` | Stores graph reference |
| `analyze_change` | `(node_id: str) -> dict` | Returns `source_node`, `total_affected`, lists of affected dataset/model/transformation IDs, and `risk_level` (`"high"` / `"medium"` / `"low"`) |

## Data Models

### NodeType (Enum)

`DATASET`, `TRANSFORMATION`, `MODEL`, `ARTIFACT`, `EXTERNAL`

### EdgeType (Enum)

`DERIVED_FROM`, `PRODUCED_BY`, `USED_BY`, `INPUT_TO`

### LineageNode

Fields: `id` (str), `name` (str), `node_type` (NodeType), `metadata` (dict, default empty), `created_at` (datetime).

### LineageEdge

Fields: `source_id` (str), `target_id` (str), `edge_type` (EdgeType), `metadata` (dict, default empty).

### DataAsset

Fields: `name` (str), `location` (str), `schema` (dict, default empty), `tags` (list[str], default empty), `created_at` (datetime).

## Dependencies

- **Standard library**: `threading`, `datetime`, `dataclasses`, `enum`
- No external dependencies.

## Constraints

- Graph traversals use DFS and will visit all reachable nodes; very large graphs may require `max_depth` to bound traversal.
- No built-in persistence; `to_dict` enables serialization but loading must be handled externally.
- Thread safety covers add operations only; concurrent traversals during mutation are safe due to the GIL but not explicitly locked.

## Error Handling

- `get_node` returns `None` for unknown IDs rather than raising.
- `get_path` returns an empty list when no path exists.
- `get_upstream` / `get_downstream` return empty lists for unknown node IDs.
