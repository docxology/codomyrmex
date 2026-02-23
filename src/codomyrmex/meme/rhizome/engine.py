"""RhizomeEngine — orchestrator for network operations."""

from __future__ import annotations

from typing import List, Dict

from codomyrmex.meme.rhizome.models import Graph, NetworkTopology
from codomyrmex.meme.rhizome.network import build_graph, calculate_centrality


class RhizomeEngine:
    """Engine for managing distributed graph networks."""

    def __init__(self) -> None:
        self.graph = Graph()

    def initialize_network(self, size: int = 100, topology: str = "scale_free") -> None:
        """Initialize the internal network structure."""
        if topology == "random":
            topo = NetworkTopology.RANDOM
        elif topology == "scale_free":
            topo = NetworkTopology.SCALE_FREE
        else:
            topo = NetworkTopology.RANDOM
            
        self.graph = build_graph(size, topo)

    def analyze_resilience(self) -> float:
        """Analyze network resilience (connectivity after random node removal)."""
        # Functional fallback: estimate resilience based on average degree
        node_count = len(self.graph.nodes)
        if node_count == 0:
            return 0.0
            
        edge_count = len(self.graph.edges)
        avg_degree = (2.0 * edge_count) / node_count
        
        # Simple heuristic: Higher average degree means higher resilience (capped at 1.0)
        return min(1.0, avg_degree / 10.0)

    def find_influencers(self, top_n: int = 5) -> List[str]:
        """Identify key influencer nodes via centrality."""
        scores = calculate_centrality(self.graph)
        sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [nid for nid, score in sorted_nodes[:top_n]]
