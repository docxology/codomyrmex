# Networks Module

**Version**: v0.1.7 | **Status**: Alpha

Graph data structures for representing and manipulating networks of nodes and edges. Provides a generic, typed API for building, querying, and traversing network topologies within the Codomyrmex ecosystem.

## Key Exports

### Classes

- **`Network`** -- Core network/graph structure supporting directed and weighted edges.
- **`Node(Generic[T])`** -- A typed node in the network with arbitrary data and attributes.
- **`Edge`** -- A weighted, directed edge between two nodes with arbitrary attributes.

### Network Methods

- **`add_node(node_id, data, **attributes)`** -- Add a node to the network.
- **`add_edge(source, target, weight, **attributes)`** -- Add a weighted edge between two existing nodes.
- **`get_neighbors(node_id)`** -- Get all neighbors of a node (both inbound and outbound).

## Quick Start

```python
from codomyrmex.networks import Network, Node, Edge

# Create a network
net = Network(name="my_graph")

# Add nodes
net.add_node("a", data={"label": "Start"})
net.add_node("b", data={"label": "End"})

# Add an edge
net.add_edge("a", "b", weight=2.5)

# Query neighbors
neighbors = net.get_neighbors("a")  # ["b"]
```

## Directory Contents

- `core.py` -- Core graph primitives: `Network`, `Node`, `Edge`
- `__init__.py` -- Package exports

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k networks -v
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
- [API Specification](API_SPECIFICATION.md) | [MCP Tools](MCP_TOOL_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
