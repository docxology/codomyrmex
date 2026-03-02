# Network Analysis -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides an undirected weighted graph data structure (`SocialGraph`) with
community detection, centrality analysis, shortest-path search, influence
scoring, and aggregate graph metrics via `GraphMetrics`.

## Architecture

Uses an adjacency-list representation backed by `defaultdict(dict)`.
Community detection relies on the label-propagation algorithm; shortest-path
search uses breadth-first search (BFS); all centrality and influence measures
are computed from the adjacency structure without external graph libraries.

## Key Classes

### `SocialGraph`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_node` | `id: str, attributes: dict \| None` | `None` | Add or update a node with optional metadata |
| `add_edge` | `source: str, target: str, weight: float` | `None` | Add an undirected weighted edge (auto-creates nodes) |
| `find_communities` | -- | `list[set[str]]` | Detect communities via label propagation (max 50 iterations) |
| `calculate_centrality` | -- | `dict[str, float]` | Degree centrality normalised to [0, 1] |
| `shortest_path` | `source: str, target: str` | `list[str]` | BFS shortest path; empty list if unreachable |
| `get_influence_score` | `node_id: str` | `float` | Weighted influence in [0, 1] |
| `neighbors` | `node_id: str` | `dict[str, float]` | Neighbor IDs mapped to edge weights |

Properties: `node_count`, `edge_count`, `nodes`.

### `GraphMetrics`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `density` | `graph: SocialGraph` | `float` | Ratio of actual to possible edges |
| `clustering_coefficient` | `graph: SocialGraph` | `float` | Average local clustering coefficient |
| `degree_distribution` | `graph: SocialGraph` | `dict[int, int]` | Degree value to node count mapping |

## Dependencies

- **Internal**: None (self-contained submodule)
- **External**: Python standard library only (`collections.defaultdict`, `collections.deque`, `random`)

## Constraints

- Label propagation shuffles node order each iteration for convergence stability.
- `edge_count` divides total adjacency entries by 2 to avoid double-counting.
- All methods are synchronous and not thread-safe.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `shortest_path` returns `[]` for missing nodes rather than raising.
- `get_influence_score` returns `0.0` for absent nodes.
- All errors logged before propagation.
