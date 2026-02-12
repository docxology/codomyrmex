"""Graph construction and analysis algorithms."""

from __future__ import annotations

import random
from typing import Dict, List, Set

from codomyrmex.meme.rhizome.models import Graph, Node, Edge, NetworkTopology


def build_graph(num_nodes: int, topology: NetworkTopology) -> Graph:
    """Construct a graph with specific topology."""
    g = Graph(topology=topology)
    node_ids = []
    
    # Create nodes
    for i in range(num_nodes):
        nid = f"n{i}"
        g.nodes[nid] = Node(id=nid, content=f"Node {i}")
        node_ids.append(nid)
    
    if topology == NetworkTopology.RANDOM:
        # Erdős–Rényi style
        p = 0.1
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                if random.random() < p:
                    src, tgt = node_ids[i], node_ids[j]
                    edge = Edge(source=src, target=tgt)
                    g.edges.append(edge)
                    g.nodes[src].connections.add(tgt)
                    g.nodes[tgt].connections.add(src)

    elif topology == NetworkTopology.SCALE_FREE:
        # Barabási–Albert preferential attachment
        m = 2  # New edges per node
        # Initial core
        initial_count = max(m + 1, 5)
        for i in range(initial_count):
            for j in range(i + 1, initial_count):
                src, tgt = node_ids[i], node_ids[j]
                edge = Edge(source=src, target=tgt)
                g.edges.append(edge)
                g.nodes[src].connections.add(tgt)
                g.nodes[tgt].connections.add(src)
                
        # Add remaining nodes
        for i in range(initial_count, num_nodes):
            targets = set()
            # Probability proportional to degree
            # Simplified: just pick from existing list weighted by degree
            existing = node_ids[:i]
            # Since strict PA is expensive O(N^2), use random sample approximation
            # or just pick m nodes if small
            candidates = random.sample(existing, min(len(existing), m * 2))
            # Sort by degree
            candidates.sort(key=lambda nid: len(g.nodes[nid].connections), reverse=True)
            targets = set(candidates[:m])
            
            for t in targets:
                src, tgt = node_ids[i], t
                edge = Edge(source=src, target=tgt)
                g.edges.append(edge)
                g.nodes[src].connections.add(tgt)
                g.nodes[tgt].connections.add(src)

    return g


def calculate_centrality(graph: Graph) -> Dict[str, float]:
    """Calculate degree centrality for all nodes."""
    centrality = {}
    n = len(graph.nodes)
    if n <= 1:
        return {nid: 0.0 for nid in graph.nodes}
        
    for nid, node in graph.nodes.items():
        degree = len(node.connections)
        centrality[nid] = degree / (n - 1)
        
    return centrality
