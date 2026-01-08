"""Graph generator for FPF visualizations using NetworkX and Matplotlib.

This module provides graph generation utilities for creating various
types of network visualizations from FPF specifications.
"""

from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from .models import FPFSpec, Pattern, Relationship


class GraphGenerator:
    """Generator for graph visualizations from FPF specifications."""

    def __init__(self, figsize: Tuple[int, int] = (12, 8), dpi: int = 300):
        """Initialize the graph generator.

        Args:
            figsize: Figure size (width, height) in inches
            dpi: Dots per inch for output
        """
        self.figsize = figsize
        self.dpi = dpi

    def create_pattern_dependency_graph(
        self, spec: FPFSpec, layout: str = "hierarchical"
    ) -> nx.DiGraph:
        """Create a directed graph of pattern dependencies.

        Args:
            spec: The FPFSpec object
            layout: Layout type ("hierarchical", "spring", "circular")

        Returns:
            NetworkX directed graph
        """
        G = nx.DiGraph()

        # Add nodes (patterns)
        for pattern in spec.patterns:
            G.add_node(
                pattern.id,
                title=pattern.title,
                status=pattern.status,
                part=pattern.part or "Other",
            )

        # Add edges (relationships)
        for relationship in spec.relationships:
            if relationship.type in ["builds_on", "prerequisite_for"]:
                G.add_edge(
                    relationship.source,
                    relationship.target,
                    type=relationship.type,
                )

        return G

    def create_term_cooccurrence_graph(
        self, cooccurrence: Dict[str, Dict[str, int]], min_weight: int = 2
    ) -> nx.Graph:
        """Create an undirected graph of term co-occurrences.

        Args:
            cooccurrence: Co-occurrence matrix from TermAnalyzer
            min_weight: Minimum edge weight to include

        Returns:
            NetworkX undirected graph
        """
        G = nx.Graph()

        for term1, neighbors in cooccurrence.items():
            if term1 not in G:
                G.add_node(term1)

            for term2, weight in neighbors.items():
                if weight >= min_weight:
                    if term2 not in G:
                        G.add_node(term2)
                    G.add_edge(term1, term2, weight=weight)

        return G

    def create_concept_relationship_graph(self, spec: FPFSpec) -> nx.Graph:
        """Create a graph of concept relationships.

        Args:
            spec: The FPFSpec object

        Returns:
            NetworkX graph
        """
        G = nx.Graph()

        # Add concept nodes
        for concept in spec.concepts:
            G.add_node(
                concept.name,
                type=concept.type,
                pattern_id=concept.pattern_id,
            )

        # Add edges based on shared patterns
        concept_patterns: Dict[str, Set[str]] = {}
        for concept in spec.concepts:
            concept_patterns[concept.name] = {concept.pattern_id}
            concept_patterns[concept.name].update(concept.references)

        # Connect concepts that share patterns
        concepts_list = list(spec.concepts)
        for i, concept1 in enumerate(concepts_list):
            for concept2 in concepts_list[i + 1:]:
                patterns1 = concept_patterns.get(concept1.name, set())
                patterns2 = concept_patterns.get(concept2.name, set())
                if patterns1 & patterns2:
                    G.add_edge(concept1.name, concept2.name)

        return G

    def apply_hierarchical_layout(self, G: nx.DiGraph) -> Dict[str, Tuple[float, float]]:
        """Apply hierarchical layout to a directed graph.

        Args:
            G: NetworkX directed graph

        Returns:
            Dictionary mapping node IDs to (x, y) positions
        """
        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
        except Exception:
            # Fallback to spring layout if graphviz not available
            pos = nx.spring_layout(G, k=2, iterations=50)

        return pos

    def apply_force_directed_layout(
        self, G: nx.Graph, k: float = None, iterations: int = 50
    ) -> Dict[str, Tuple[float, float]]:
        """Apply force-directed layout to a graph.

        Args:
            G: NetworkX graph
            k: Optimal distance between nodes
            iterations: Number of iterations

        Returns:
            Dictionary mapping node IDs to (x, y) positions
        """
        if k is None:
            k = 1 / np.sqrt(len(G.nodes()))

        pos = nx.spring_layout(G, k=k, iterations=iterations)
        return pos

    def apply_circular_layout(self, G: nx.Graph) -> Dict[str, Tuple[float, float]]:
        """Apply circular layout to a graph.

        Args:
            G: NetworkX graph

        Returns:
            Dictionary mapping node IDs to (x, y) positions
        """
        return nx.circular_layout(G)

    def apply_tree_layout(self, G: nx.Graph, root: Optional[str] = None) -> Dict[str, Tuple[float, float]]:
        """Apply tree layout to a graph.

        Args:
            G: NetworkX graph
            root: Optional root node

        Returns:
            Dictionary mapping node IDs to (x, y) positions
        """
        try:
            if root and root in G:
                pos = nx.nx_agraph.graphviz_layout(G, prog="dot", root=root)
            else:
                pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
        except Exception:
            # Fallback to hierarchical spring layout
            pos = nx.spring_layout(G, k=2, iterations=100)

        return pos

    def get_node_colors_by_attribute(
        self, G: nx.Graph, attribute: str, color_map: Dict[str, str] = None
    ) -> List[str]:
        """Get node colors based on a node attribute.

        Args:
            G: NetworkX graph
            attribute: Node attribute name
            color_map: Optional mapping of attribute values to colors

        Returns:
            List of color values for each node
        """
        if color_map is None:
            # Default color maps
            if attribute == "status":
                color_map = {
                    "Stable": "#2ecc71",  # Green
                    "Draft": "#f39c12",  # Orange
                    "Stub": "#95a5a6",  # Gray
                    "New": "#3498db",  # Blue
                }
            elif attribute == "part":
                # Use colormap for parts
                parts = {G.nodes[node].get(attribute, "Other") for node in G.nodes()}
                part_list = sorted(list(parts))
                colors_list = plt.cm.Set3(np.linspace(0, 1, len(part_list)))
                color_map = {part: colors_list[i] for i, part in enumerate(part_list)}
            else:
                # Default: use attribute hash
                unique_vals = {G.nodes[node].get(attribute, "default") for node in G.nodes()}
                colors_list = plt.cm.tab10(np.linspace(0, 1, len(unique_vals)))
                color_map = {val: colors_list[i] for i, val in enumerate(sorted(unique_vals))}

        colors = []
        for node in G.nodes():
            attr_value = G.nodes[node].get(attribute, "default")
            colors.append(color_map.get(attr_value, "#95a5a6"))

        return colors

    def get_node_sizes_by_importance(
        self, G: nx.Graph, importance_metric: str = "degree"
    ) -> List[float]:
        """Get node sizes based on importance metric.

        Args:
            G: NetworkX graph
            importance_metric: Metric to use ("degree", "betweenness", "pagerank")

        Returns:
            List of sizes for each node
        """
        if importance_metric == "degree":
            importances = dict(G.degree())
        elif importance_metric == "betweenness":
            importances = nx.betweenness_centrality(G)
        elif importance_metric == "pagerank":
            importances = nx.pagerank(G)
        else:
            importances = dict(G.degree())

        if not importances:
            return [300] * len(G.nodes())

        max_importance = max(importances.values()) if importances.values() else 1
        min_importance = min(importances.values()) if importances.values() else 0

        if max_importance == min_importance:
            return [300] * len(G.nodes())

        # Scale to 100-2000 range
        sizes = [
            100 + (importances.get(node, 0) - min_importance) / (max_importance - min_importance) * 1900
            for node in G.nodes()
        ]

        return sizes



