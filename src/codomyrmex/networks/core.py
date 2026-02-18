"""Network module for Codomyrmex.

This module provides the core graph structure for representing and
manipulating networks in the system.
"""

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class Node(Generic[T]):
    """A node in the network."""
    id: str
    data: T
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    """An edge between two nodes."""
    source: str
    target: str
    weight: float = 1.0
    attributes: dict[str, Any] = field(default_factory=dict)


class Network:
    """Core network/graph structure."""

    def __init__(self, name: str = "default_network"):
        """Initialize the network."""
        self.name = name
        self.nodes: dict[str, Node[Any]] = {}
        self.edges: list[Edge] = []
        logger.info(f"Network initialized: {self.name}")

    def add_node(self, node_id: str, data: Any = None, **attributes: Any) -> None:
        """Add a node to the network."""
        if node_id in self.nodes:
            logger.warning(f"Node {node_id} already exists in network {self.name}")
            return
        
        self.nodes[node_id] = Node(id=node_id, data=data, attributes=attributes)
        logger.debug(f"Added node {node_id} to network {self.name}")

    def add_edge(
        self, source: str, target: str, weight: float = 1.0, **attributes: Any
    ) -> None:
        """Add an edge between two nodes."""
        if source not in self.nodes:
            raise ValueError(f"Source node {source} does not exist")
        if target not in self.nodes:
            raise ValueError(f"Target node {target} does not exist")

        edge = Edge(source=source, target=target, weight=weight, attributes=attributes)
        self.edges.append(edge)
        logger.debug(f"Added edge {source}->{target} to network {self.name}")

    def get_neighbors(self, node_id: str) -> list[str]:
        """Get neighbors of a node."""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist")
        
        return [e.target for e in self.edges if e.source == node_id] + \
               [e.source for e in self.edges if e.target == node_id]
