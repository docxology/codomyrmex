"""Graph construction and analysis algorithms."""

from __future__ import annotations

import random

from codomyrmex.meme.rhizome.models import Edge, Graph, NetworkTopology, Node


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
        initial_count = min(max(m + 1, 5), num_nodes)
        for i in range(initial_count):
            for j in range(i + 1, initial_count):
                src, tgt = node_ids[i], node_ids[j]
                edge = Edge(source=src, target=tgt)
                g.edges.append(edge)
                g.nodes[src].connections.add(tgt)
                g.nodes[tgt].connections.add(src)

        # Fast Preferential Attachment via node repetition list
        # This replaces the O(N^2) sorting loop with O(m) weighted random choice
        repeated_nodes = []
        for i in range(initial_count):
            repeated_nodes.extend([node_ids[i]] * max(0, initial_count - 1))

        # Add remaining nodes
        for i in range(initial_count, num_nodes):
            targets = set()
            # If not enough nodes to pick from, pick what we can
            available_distinct = i
            target_count = min(m, available_distinct)

            # Pick distinct targets
            if target_count > 0 and len(repeated_nodes) > 0:
                while len(targets) < target_count:
                    target = random.choice(repeated_nodes)
                    targets.add(target)

            src = node_ids[i]
            for t in targets:
                edge = Edge(source=src, target=t)
                g.edges.append(edge)
                g.nodes[src].connections.add(t)
                g.nodes[t].connections.add(src)
                repeated_nodes.extend([src, t])

    return g


def calculate_centrality(graph: Graph) -> dict[str, float]:
    """Calculate degree centrality for all nodes."""
    centrality = {}
    n = len(graph.nodes)
    if n <= 1:
        return dict.fromkeys(graph.nodes, 0.0)

    for nid, node in graph.nodes.items():
        degree = len(node.connections)
        centrality[nid] = degree / (n - 1)

    return centrality
