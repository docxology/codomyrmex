# Personal AI Infrastructure -- Networks Module

**Version**: v0.1.0 | **Status**: Alpha | **Last Updated**: February 2026

## Overview

The Networks module provides **graph data structures** for the codomyrmex ecosystem. It offers typed nodes, weighted edges, and neighbor queries. PAI agents use this module to represent dependency graphs, communication topologies, and relational structures during planning and analysis phases.

## PAI Capabilities

### Graph Construction

```python
from codomyrmex.networks import Network, Node, Edge

# Create a network for module dependencies
net = Network(name="module_deps")

# Add typed nodes
net.add_node("logging", data="Foundation", layer=1)
net.add_node("agents", data="Core", layer=2)
net.add_node("orchestrator", data="Service", layer=3)

# Connect with weighted edges
net.add_edge("agents", "logging", weight=1.0, relation="depends_on")
net.add_edge("orchestrator", "agents", weight=1.0, relation="depends_on")
```

### Neighbor Queries

```python
# Find all neighbors of a node (both directions)
neighbors = net.get_neighbors("agents")  # ["logging", "orchestrator"]
```

### Direct Access

```python
# Access node data and attributes
node = net.nodes["agents"]
print(node.id, node.data, node.attributes)

# Access edge list
for edge in net.edges:
    print(f"{edge.source} -> {edge.target} (weight={edge.weight})")
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Network` | Class | Core graph container with node/edge management |
| `Node[T]` | Dataclass | Generic typed node with id, data, and attributes |
| `Edge` | Dataclass | Directed weighted edge with source, target, weight, and attributes |

## PAI Algorithm Phase Mapping

| Phase | Networks Module Contribution |
|-------|------------------------------|
| **OBSERVE** | `get_neighbors`, `net.nodes`, `net.edges` -- inspect graph structure |
| **PLAN** | `Network()`, `add_node`, `add_edge` -- model dependency and communication graphs |
| **BUILD** | Construct networks representing code architecture or agent topologies |
| **VERIFY** | Query neighbors to validate graph invariants (e.g., no orphan nodes, correct dependencies) |

## Architecture Role

**Core Layer** -- Depends on `logging_monitoring` (Foundation). Provides graph primitives consumed by higher-layer modules such as `orchestrator` and `agents` for representing workflows and agent topologies.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
