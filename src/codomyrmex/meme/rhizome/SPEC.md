# Rhizome -- Technical Specification

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Overview

Models distributed, non-hierarchical network structures inspired by Deleuze and Guattari's rhizome concept. Provides graph construction with configurable topologies (random Erdos-Renyi, scale-free Barabasi-Albert), degree centrality analysis, resilience estimation, and influencer identification.

## Architecture

Graph-based network analysis pattern. `RhizomeEngine` wraps a `Graph` of `Node` and `Edge` objects. `build_graph` constructs networks with specified topology and size. Resilience is estimated via average-degree heuristic. Influencers are ranked by degree centrality.

## Key Classes

### `RhizomeEngine`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `initialize_network` | `size: int, topology: str` | `None` | Build internal graph with specified topology ("random" or "scale_free") |
| `analyze_resilience` | none | `float` | Estimate resilience from average degree (capped at 1.0) |
| `find_influencers` | `top_n: int` | `list[str]` | Return top-N node IDs ranked by degree centrality |

### Data Models

| Class | Fields | Purpose |
|-------|--------|---------|
| `Node` | `id, content, node_type, capacity, connections: set[str], metadata` | A node in the rhizome network |
| `Edge` | `source, target, weight, edge_type, id` | A connection between two nodes |
| `Graph` | `nodes: dict[str, Node], edges: list[Edge], topology` | Graph structure with `add_node` and `add_edge` methods |
| `NetworkTopology` | `RANDOM, SCALE_FREE, SMALL_WORLD, LATTICE, FULLY_CONNECTED` | Network structure type enum |

### Module Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `build_graph` | `num_nodes: int, topology: NetworkTopology` | `Graph` | Construct graph with Erdos-Renyi (p=0.1) or Barabasi-Albert (m=2) model |
| `calculate_centrality` | `graph: Graph` | `dict[str, float]` | Compute degree centrality for all nodes (degree / (N-1)) |

## Dependencies

- **Internal**: None (self-contained within `meme` package)
- **External**: Standard library only (`uuid`, `random`, `dataclasses`, `enum`)

## Constraints

- Erdos-Renyi uses fixed p=0.1 connection probability; not configurable.
- Barabasi-Albert uses m=2 edges per new node with simplified preferential attachment (random sample approximation).
- Only `RANDOM` and `SCALE_FREE` topologies are implemented; others default to `RANDOM`.
- Resilience is a heuristic (average degree / 10.0); no actual node removal simulation.
- Edge IDs are deterministic for undirected edges (`sorted(source, target)` joined).
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `analyze_resilience` returns 0.0 for empty graphs.
- `calculate_centrality` returns 0.0 for all nodes when graph has 0 or 1 nodes.
