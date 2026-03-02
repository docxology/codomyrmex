# Codomyrmex Agents -- src/codomyrmex/relations/network_analysis

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Implements an undirected weighted social graph with community detection
(label propagation), degree centrality, shortest-path search (BFS),
influence scoring, and aggregate graph metrics such as density, clustering
coefficient, and degree distribution.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `graph.py` | `SocialGraph` | Undirected weighted graph -- nodes, edges, community detection, centrality, shortest path, influence |
| `graph.py` | `GraphMetrics` | Static utility for density, clustering coefficient, and degree distribution |

## Operating Contracts

- `SocialGraph` is undirected: `add_edge(a, b)` creates edges in both directions.
- `add_edge` auto-creates missing nodes; explicit `add_node` is optional.
- `find_communities` uses label propagation with up to 50 iterations and weighted neighbor labels.
- `calculate_centrality` returns degree centrality normalised to `[0, 1]` (degree / (N-1)).
- `shortest_path` uses unweighted BFS and returns an empty list when no path exists.
- `get_influence_score` returns the fraction of total edge weight incident to the node.
- `GraphMetrics.clustering_coefficient` computes the average local clustering coefficient.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Python standard library (`collections`, `random`)
- **Used by**: `relations` parent module, relationship strength scoring, agent social-graph workflows

## Navigation

- **Parent**: [relations](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
