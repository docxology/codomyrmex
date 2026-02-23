# Networks Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Networks module provides graph-based network modeling with nodes, edges, and graph algorithms. It supports directed and undirected graphs, weighted edges, and common graph operations for modeling relationships, dependencies, and communication topologies.

## Installation

```bash
uv add codomyrmex
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Network` | Class | Graph container with nodes and edges |
| `Node` | Class | Graph vertex with attributes |
| `Edge` | Class | Graph connection with weight and metadata |

## Quick Start

```python
from codomyrmex.networks import Network, Node, Edge

net = Network()
a = Node(id="auth", label="Auth Module")
b = Node(id="agents", label="Agents Module")
net.add_node(a)
net.add_node(b)
net.add_edge(Edge(source="agents", target="auth", weight=1.0))

# Graph operations
neighbors = net.neighbors("agents")
shortest = net.shortest_path("auth", "agents")
```

## Architecture

```
networks/
├── __init__.py   # Exports: Network, Node, Edge
├── core.py       # Network, Node, Edge implementations
└── tests/        # Zero-Mock tests
```

## Navigation

- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
