# Agent Guidelines - Networks

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Graph data structures for building, querying, and traversing networks of typed nodes and weighted edges.

## Key Classes

- **`Network`** -- Core graph container with node/edge management
- **`Node(Generic[T])`** -- Typed node with id, data, and attributes
- **`Edge`** -- Directed edge with source, target, weight, and attributes

## Agent Instructions

1. **Add nodes before edges** -- Both source and target nodes must exist before creating an edge
2. **Use unique node IDs** -- Duplicate node IDs are silently ignored with a warning
3. **Leverage generics** -- `Node[T]` supports any data type for node payloads
4. **Check neighbors symmetrically** -- `get_neighbors()` returns both inbound and outbound connections
5. **Use attributes for metadata** -- Both nodes and edges accept arbitrary keyword attributes

## Common Patterns

```python
from codomyrmex.networks import Network, Node, Edge

# Build a network
net = Network(name="dependency_graph")

# Add nodes with typed data
net.add_node("logging", data="Foundation", layer=1)
net.add_node("agents", data="Core", layer=2)
net.add_node("cli", data="Application", layer=4)

# Connect them
net.add_edge("agents", "logging", weight=1.0, relation="depends_on")
net.add_edge("cli", "agents", weight=1.0, relation="depends_on")

# Query
neighbors = net.get_neighbors("agents")  # ["logging", "cli"]

# Access node data directly
node = net.nodes["logging"]
print(node.id, node.data, node.attributes)  # "logging" "Foundation" {"layer": 1}

# Access edge properties
edge = net.edges[0]
print(edge.source, edge.target, edge.weight)  # "agents" "logging" 1.0
```

## Testing Patterns

```python
from codomyrmex.networks import Network

# Verify network creation
net = Network("test")
assert net.name == "test"
assert len(net.nodes) == 0
assert len(net.edges) == 0

# Verify node addition
net.add_node("n1", data="hello")
assert "n1" in net.nodes
assert net.nodes["n1"].data == "hello"

# Verify edge addition
net.add_node("n2", data="world")
net.add_edge("n1", "n2", weight=0.5)
assert len(net.edges) == 1
assert net.edges[0].weight == 0.5

# Verify neighbor lookup
assert "n2" in net.get_neighbors("n1")
assert "n1" in net.get_neighbors("n2")
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
