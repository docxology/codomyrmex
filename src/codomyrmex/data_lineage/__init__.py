"""
Data Lineage Module

Data provenance and lineage tracking.
"""

__version__ = "0.1.0"

import json
import hashlib
import threading
from typing import Optional, List, Dict, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod


class NodeType(Enum):
    """Types of lineage nodes."""
    DATASET = "dataset"
    TRANSFORMATION = "transformation"
    MODEL = "model"
    ARTIFACT = "artifact"
    EXTERNAL = "external"


class EdgeType(Enum):
    """Types of lineage edges."""
    DERIVED_FROM = "derived_from"
    PRODUCED_BY = "produced_by"
    USED_BY = "used_by"
    INPUT_TO = "input_to"


@dataclass
class LineageNode:
    """A node in the lineage graph."""
    id: str
    name: str
    node_type: NodeType
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def key(self) -> str:
        """Get unique key."""
        return f"{self.node_type.value}:{self.id}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.node_type.value,
            "version": self.version,
            "metadata": self.metadata,
        }


@dataclass
class LineageEdge:
    """An edge connecting two nodes."""
    source_id: str
    target_id: str
    edge_type: EdgeType
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def key(self) -> str:
        """Get unique key."""
        return f"{self.source_id}->{self.target_id}:{self.edge_type.value}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.edge_type.value,
        }


@dataclass
class DataAsset:
    """A data asset with lineage information."""
    id: str
    name: str
    location: str
    schema: Optional[Dict[str, str]] = None
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def compute_checksum(self, data: bytes) -> str:
        """Compute checksum of data."""
        self.checksum = hashlib.sha256(data).hexdigest()
        return self.checksum


class LineageGraph:
    """
    Graph of data lineage relationships.
    
    Usage:
        graph = LineageGraph()
        
        # Add nodes
        graph.add_node(LineageNode(id="raw_data", name="Raw Data", node_type=NodeType.DATASET))
        graph.add_node(LineageNode(id="model", name="ML Model", node_type=NodeType.MODEL))
        
        # Add edges
        graph.add_edge(LineageEdge("raw_data", "model", EdgeType.INPUT_TO))
        
        # Query lineage
        upstream = graph.get_upstream("model")
    """
    
    def __init__(self):
        self._nodes: Dict[str, LineageNode] = {}
        self._edges: List[LineageEdge] = []
        self._lock = threading.Lock()
    
    def add_node(self, node: LineageNode) -> None:
        """Add a node to the graph."""
        with self._lock:
            self._nodes[node.id] = node
    
    def get_node(self, node_id: str) -> Optional[LineageNode]:
        """Get a node by ID."""
        return self._nodes.get(node_id)
    
    def add_edge(self, edge: LineageEdge) -> None:
        """Add an edge to the graph."""
        with self._lock:
            self._edges.append(edge)
    
    def get_edges(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
    ) -> List[LineageEdge]:
        """Get edges matching criteria."""
        results = []
        for edge in self._edges:
            if source_id and edge.source_id != source_id:
                continue
            if target_id and edge.target_id != target_id:
                continue
            results.append(edge)
        return results
    
    def get_upstream(self, node_id: str, max_depth: int = 10) -> List[LineageNode]:
        """Get all upstream nodes (ancestors)."""
        visited: Set[str] = set()
        result = []
        
        def dfs(current_id: str, depth: int):
            if depth > max_depth or current_id in visited:
                return
            visited.add(current_id)
            
            # Find edges where this node is the target
            for edge in self._edges:
                if edge.target_id == current_id:
                    source_node = self.get_node(edge.source_id)
                    if source_node and source_node.id not in visited:
                        result.append(source_node)
                        dfs(source_node.id, depth + 1)
        
        dfs(node_id, 0)
        return result
    
    def get_downstream(self, node_id: str, max_depth: int = 10) -> List[LineageNode]:
        """Get all downstream nodes (descendants)."""
        visited: Set[str] = set()
        result = []
        
        def dfs(current_id: str, depth: int):
            if depth > max_depth or current_id in visited:
                return
            visited.add(current_id)
            
            # Find edges where this node is the source
            for edge in self._edges:
                if edge.source_id == current_id:
                    target_node = self.get_node(edge.target_id)
                    if target_node and target_node.id not in visited:
                        result.append(target_node)
                        dfs(target_node.id, depth + 1)
        
        dfs(node_id, 0)
        return result
    
    def get_path(self, source_id: str, target_id: str) -> List[str]:
        """Find path between two nodes."""
        visited: Set[str] = set()
        
        def dfs(current: str, path: List[str]) -> Optional[List[str]]:
            if current == target_id:
                return path + [current]
            
            if current in visited:
                return None
            
            visited.add(current)
            
            for edge in self._edges:
                if edge.source_id == current:
                    result = dfs(edge.target_id, path + [current])
                    if result:
                        return result
            
            return None
        
        return dfs(source_id, []) or []
    
    @property
    def node_count(self) -> int:
        """Get number of nodes."""
        return len(self._nodes)
    
    @property
    def edge_count(self) -> int:
        """Get number of edges."""
        return len(self._edges)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [e.to_dict() for e in self._edges],
        }


class LineageTracker:
    """
    Tracks data lineage through transformations.
    
    Usage:
        tracker = LineageTracker()
        
        # Track transformation
        with tracker.track("transform_1", "Clean Data") as t:
            t.add_input("raw_data")
            # perform transformation
            t.add_output("clean_data")
    """
    
    def __init__(self, graph: Optional[LineageGraph] = None):
        self.graph = graph or LineageGraph()
        self._current_transform: Optional[str] = None
    
    def register_dataset(
        self,
        id: str,
        name: str,
        location: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> LineageNode:
        """Register a dataset."""
        node = LineageNode(
            id=id,
            name=name,
            node_type=NodeType.DATASET,
            metadata={"location": location, **(metadata or {})},
        )
        self.graph.add_node(node)
        return node
    
    def register_transformation(
        self,
        id: str,
        name: str,
        inputs: List[str],
        outputs: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> LineageNode:
        """Register a transformation with inputs and outputs."""
        # Add transformation node
        transform_node = LineageNode(
            id=id,
            name=name,
            node_type=NodeType.TRANSFORMATION,
            metadata=metadata or {},
        )
        self.graph.add_node(transform_node)
        
        # Add edges from inputs to transformation
        for input_id in inputs:
            self.graph.add_edge(LineageEdge(
                source_id=input_id,
                target_id=id,
                edge_type=EdgeType.INPUT_TO,
            ))
        
        # Add edges from transformation to outputs
        for output_id in outputs:
            self.graph.add_edge(LineageEdge(
                source_id=id,
                target_id=output_id,
                edge_type=EdgeType.PRODUCED_BY,
            ))
        
        return transform_node
    
    def get_origin(self, node_id: str) -> List[LineageNode]:
        """Get the original source data for a node."""
        upstream = self.graph.get_upstream(node_id)
        return [n for n in upstream if n.node_type == NodeType.DATASET and not self.graph.get_upstream(n.id)]
    
    def get_impact(self, node_id: str) -> List[LineageNode]:
        """Get all nodes affected by changes to this node."""
        return self.graph.get_downstream(node_id)


class ImpactAnalyzer:
    """
    Analyzes impact of data changes.
    
    Usage:
        analyzer = ImpactAnalyzer(tracker.graph)
        
        # Check impact of changing a dataset
        impact = analyzer.analyze_change("raw_data")
        print(f"Affects {len(impact.affected_nodes)} nodes")
    """
    
    def __init__(self, graph: LineageGraph):
        self.graph = graph
    
    def analyze_change(self, node_id: str) -> Dict[str, Any]:
        """Analyze impact of changing a node."""
        downstream = self.graph.get_downstream(node_id)
        
        affected_datasets = [n for n in downstream if n.node_type == NodeType.DATASET]
        affected_models = [n for n in downstream if n.node_type == NodeType.MODEL]
        affected_transforms = [n for n in downstream if n.node_type == NodeType.TRANSFORMATION]
        
        return {
            "source_node": node_id,
            "total_affected": len(downstream),
            "affected_datasets": [n.id for n in affected_datasets],
            "affected_models": [n.id for n in affected_models],
            "affected_transformations": [n.id for n in affected_transforms],
            "risk_level": "high" if affected_models else "medium" if affected_datasets else "low",
        }


__all__ = [
    # Enums
    "NodeType",
    "EdgeType",
    # Data classes
    "LineageNode",
    "LineageEdge",
    "DataAsset",
    # Core
    "LineageGraph",
    "LineageTracker",
    "ImpactAnalyzer",
]
