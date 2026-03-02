# Codomyrmex Agents -- src/codomyrmex/meme/rhizome

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Purpose

Models distributed, non-hierarchical network structures inspired by Deleuze and Guattari's rhizome concept. Provides graph construction with configurable topologies (random Erdos-Renyi, scale-free Barabasi-Albert), degree centrality analysis, resilience estimation, and influencer identification.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `engine.py` | `RhizomeEngine` | Orchestrator: initialize network, analyze resilience, find influencers |
| `network.py` | `build_graph` | Construct graph with Erdos-Renyi (p=0.1) or Barabasi-Albert (m=2) model |
| `network.py` | `calculate_centrality` | Compute degree centrality for all nodes |
| `models.py` | `Node` | A node with ID, content, type, capacity, and connections |
| `models.py` | `Edge` | A weighted connection between two nodes |
| `models.py` | `Graph` | Graph structure with `add_node` and `add_edge` methods |
| `models.py` | `NetworkTopology` | RANDOM, SCALE_FREE, SMALL_WORLD, LATTICE, FULLY_CONNECTED |

## Operating Contracts

- Only RANDOM and SCALE_FREE topologies are implemented; others default to RANDOM.
- Graph algorithms can be O(N^2); exercise caution with networks exceeding ~10k nodes.
- Resilience is a heuristic (average degree / 10.0); no actual node removal simulation.
- Edge IDs are deterministic for undirected edges (sorted source/target joined by dash).
- `find_influencers` ranks by degree centrality (connections / (N-1)).
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: None (standard library only: `uuid`, `random`, `dataclasses`)
- **Used by**: `meme.swarm` (swarm agents traverse rhizome edges), `meme.ideoscape` (rhizome defines paths, ideoscape defines terrain), `meme.contagion` (network-based simulation expansion)

## Navigation

- **Parent**: [meme](../README.md)
- **Root**: [Root](../../../../README.md)
