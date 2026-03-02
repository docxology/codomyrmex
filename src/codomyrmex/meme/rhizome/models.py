"""Data models for rhizomatic networks."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import StrEnum


class NetworkTopology(StrEnum):
    """Network structure types."""
    RANDOM = "random"
    SCALE_FREE = "scale_free"
    SMALL_WORLD = "small_world"
    LATTICE = "lattice"
    FULLY_CONNECTED = "fully_connected"


@dataclass
class Node:
    """A node in the rhizome network (can be an agent, meme, or concept).

    Attributes:
        id: Unique identifier.
        content: Payload (e.g. meme content).
        node_type: Classification.
        connections: Set of connected node IDs.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    content: str = ""
    node_type: str = "generic"
    capacity: float = 1.0
    connections: set[str] = field(default_factory=set)
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class Edge:
    """A connection between two nodes.

    Attributes:
        source: Source Node ID.
        target: Target Node ID.
        weight: Connection strength (0-1).
        edge_type: Relationship type.
    """
    source: str
    target: str
    weight: float = 1.0
    edge_type: str = "undirected"
    id: str = field(default="")

    def __post_init__(self):
        if not self.id:
            # Deterministic ID for undirected edge check
            s, t = sorted([self.source, self.target])
            self.id = f"{s}-{t}"


@dataclass
class Graph:
    """A graph structure representing the network.

    Attributes:
        nodes: Map of ID to Node.
        edges: List of Edges.
    """
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    topology: NetworkTopology = NetworkTopology.RANDOM

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge):
        self.edges.append(edge)
        if edge.source in self.nodes:
            self.nodes[edge.source].connections.add(edge.target)
        if edge.target in self.nodes:
            # Assuming undirected for connectivity tracking simple case
            self.nodes[edge.target].connections.add(edge.source)
