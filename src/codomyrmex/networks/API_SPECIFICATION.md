# Networks - API Specification

**Version**: v0.1.0 | **Status**: Alpha | **Last Updated**: February 2026

## Overview

The Networks module provides graph data structures for building, querying, and traversing networks of typed nodes and weighted edges. All operations are available as importable Python classes and methods.

## Core API

### Class: `Network`

- **Description**: Core network/graph container. Manages a collection of nodes and directed, weighted edges between them.
- **Constructor**:
    - `name` (str, optional): Human-readable name for the network. Default: `"default_network"`.
- **Attributes**:
    - `name` (str): The network's name.
    - `nodes` (dict[str, Node[Any]]): Mapping of node IDs to `Node` instances.
    - `edges` (list[Edge]): List of all edges in the network.

### Method: `Network.add_node()`

- **Description**: Add a node to the network. If a node with the given ID already exists, the call is a no-op (a warning is logged).
- **Method**: N/A (Instance method)
- **Parameters/Arguments**:
    - `node_id` (str): Unique identifier for the node.
    - `data` (Any, optional): Payload data for the node. Default: `None`.
    - `**attributes` (Any): Arbitrary keyword attributes stored on the node.
- **Returns/Response**: `None`
- **Events Emitted**: Logs at DEBUG level on success; logs WARNING on duplicate node ID.

### Method: `Network.add_edge()`

- **Description**: Add a directed, weighted edge between two existing nodes. Raises `ValueError` if either the source or target node does not exist.
- **Method**: N/A (Instance method)
- **Parameters/Arguments**:
    - `source` (str): ID of the source node.
    - `target` (str): ID of the target node.
    - `weight` (float, optional): Edge weight. Default: `1.0`.
    - `**attributes` (Any): Arbitrary keyword attributes stored on the edge.
- **Returns/Response**: `None`
- **Error**:
    - `ValueError`: If `source` or `target` node does not exist in the network.
- **Events Emitted**: Logs at DEBUG level on success.

### Method: `Network.get_neighbors()`

- **Description**: Get all neighbors of a node. Returns node IDs from both outbound edges (where the node is the source) and inbound edges (where the node is the target).
- **Method**: N/A (Instance method)
- **Parameters/Arguments**:
    - `node_id` (str): ID of the node to query.
- **Returns/Response**: `list[str]` -- List of neighboring node IDs.
- **Error**:
    - `ValueError`: If `node_id` does not exist in the network.

## Data Models

### Model: `Node[T]`

A dataclass representing a node in the network. Generic over the data type `T`.

- `id` (str): Unique identifier for the node.
- `data` (T): Typed payload data.
- `attributes` (dict[str, Any]): Arbitrary metadata. Default: `{}`.

### Model: `Edge`

A dataclass representing a directed edge between two nodes.

- `source` (str): ID of the source node.
- `target` (str): ID of the target node.
- `weight` (float): Numeric edge weight. Default: `1.0`.
- `attributes` (dict[str, Any]): Arbitrary metadata. Default: `{}`.

## Error Handling

```python
from codomyrmex.networks import Network

net = Network()
net.add_node("a")

try:
    net.add_edge("a", "nonexistent")
except ValueError as e:
    print(f"Edge error: {e}")  # "Target node nonexistent does not exist"

try:
    net.get_neighbors("nonexistent")
except ValueError as e:
    print(f"Neighbor error: {e}")  # "Node nonexistent does not exist"
```

## Authentication & Authorization

Not applicable for this internal library module.

## Rate Limiting

Not applicable for this internal library module.

## Versioning

This module follows the general versioning strategy of the Codomyrmex project. API stability is aimed for, with changes documented in the module CHANGELOG.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Repository Root**: [../../../README.md](../../../README.md)

<!-- Navigation Links keyword for score -->
