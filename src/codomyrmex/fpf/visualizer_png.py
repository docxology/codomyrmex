"""PNG visualization engine for FPF specifications.

This module provides functionality to generate high-quality PNG visualizations
of FPF patterns, concepts, relationships, and shared terms with professional
academic styling.
"""

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from codomyrmex.cerebrum.visualization_base import BaseNetworkVisualizer
from codomyrmex.cerebrum.visualization_theme import get_default_theme

from .graph_generator import GraphGenerator
from .models import FPFSpec, Pattern
from .term_analyzer import TermAnalyzer


class FPFVisualizerPNG:
    """PNG visualizer for FPF specifications with enhanced styling."""

    def __init__(self, figsize: Tuple[int, int] = (16, 12), dpi: int = 300):
        """Initialize the PNG visualizer.

        Args:
            figsize: Figure size (width, height) in inches
            dpi: Dots per inch for output
        """
        self.figsize = figsize
        self.dpi = dpi
        self.theme = get_default_theme()
        self.graph_generator = GraphGenerator(figsize=figsize, dpi=dpi)
        self.term_analyzer = TermAnalyzer()
        self.network_viz = BaseNetworkVisualizer(figure_size=figsize, dpi=dpi)

    def visualize_shared_terms_network(
        self,
        spec: FPFSpec,
        output_path: Path,
        min_weight: int = 2,
        top_n: int = 100,
    ) -> None:
        """Generate shared terms network visualization.

        Args:
            spec: The FPFSpec object
            output_path: Path to save PNG file
            min_weight: Minimum co-occurrence weight to show
            top_n: Number of top terms to include
        """
        # Get co-occurrence matrix
        cooccurrence = self.term_analyzer.build_term_cooccurrence_matrix(spec)

        # Get top terms
        important_terms = self.term_analyzer.get_important_terms(spec, top_n=top_n)
        top_term_set = {term for term, _, _ in important_terms}

        # Filter co-occurrence to top terms
        filtered_cooccurrence = {
            term1: {
                term2: weight
                for term2, weight in neighbors.items()
                if term2 in top_term_set and weight >= min_weight
            }
            for term1, neighbors in cooccurrence.items()
            if term1 in top_term_set
        }

        # Create graph
        G = self.graph_generator.create_term_cooccurrence_graph(
            filtered_cooccurrence, min_weight=min_weight
        )

        if len(G.nodes()) == 0:
            raise ValueError("No terms found for visualization")

        # Create figure with theme
        fig, ax = self.network_viz.create_figure()

        # Apply layout
        pos = self.network_viz.apply_layout(G, layout="spring", k=2.0, iterations=100)

        # Get node sizes and colors
        node_sizes = self.network_viz.get_node_sizes(G, metric="degree", min_size=300, max_size=3000)
        node_colors = self.theme.get_color_sequence(len(G.nodes()), "primary")

        # Get edge widths
        edge_widths = self.network_viz.get_edge_widths(G, min_width=0.5, max_width=2.5)

        # Draw edges first
        nx.draw_networkx_edges(
            G,
            pos,
            ax=ax,
            width=edge_widths if edge_widths else 1.0,
            alpha=0.6,
            edge_color=self.theme.colors.edge_default,
        )

        # Draw nodes
        nx.draw_networkx_nodes(
            G,
            pos,
            ax=ax,
            node_size=node_sizes,
            node_color=node_colors,
            alpha=0.9,
            edgecolors="black",
            linewidths=1.0,
        )

        # Draw labels for important nodes
        important_nodes = [n for n in G.nodes() if G.degree(n) > np.percentile([G.degree(n) for n in G.nodes()], 75)]
        labels = {n: n[:20] + "..." if len(n) > 20 else n for n in important_nodes}
        nx.draw_networkx_labels(
            G,
            pos,
            labels,
            ax=ax,
            font_size=self.theme.font.tick_size,
            font_weight="bold",
        )

        # Format title
        self.network_viz.format_title(ax, "Shared Terms Network")

        # Apply theme
        self.theme.apply_to_axes(ax)
        ax.axis("off")

        # Save
        self.network_viz.save_figure(fig, str(output_path))

    def visualize_pattern_dependencies(
        self,
        spec: FPFSpec,
        output_path: Path,
        layout: str = "hierarchical",
        color_by: str = "status",
    ) -> None:
        """Generate pattern dependency graph visualization.

        Args:
            spec: The FPFSpec object
            output_path: Path to save PNG file
            layout: Layout type ("hierarchical", "spring", "circular")
            color_by: Attribute to color by ("status", "part")
        """
        # Create graph
        G = self.graph_generator.create_pattern_dependency_graph(spec, layout=layout)

        if len(G.nodes()) == 0:
            raise ValueError("No patterns found for visualization")

        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Apply layout
        if layout == "hierarchical":
            pos = self.graph_generator.apply_hierarchical_layout(G)
        elif layout == "circular":
            pos = self.graph_generator.apply_circular_layout(G)
        else:
            pos = self.graph_generator.apply_force_directed_layout(G)

        # Get node colors
        node_colors = self.graph_generator.get_node_colors_by_attribute(G, color_by)

        # Get node sizes
        node_sizes = self.graph_generator.get_node_sizes_by_importance(G, "degree")

        # Draw network
        nx.draw_networkx_nodes(
            G, pos, ax=ax, node_size=node_sizes, node_color=node_colors, alpha=0.8
        )

        # Draw edges
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.3, edge_color="#95a5a6", arrows=True, arrowsize=20)

        # Draw labels (abbreviated)
        labels = {node: node for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=6)

        ax.set_title(f"Pattern Dependency Graph ({layout})", fontsize=16, fontweight="bold", pad=20)
        ax.axis("off")

        # Add legend
        if color_by == "status":
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor="#2ecc71", label="Stable"),
                Patch(facecolor="#f39c12", label="Draft"),
                Patch(facecolor="#95a5a6", label="Stub"),
                Patch(facecolor="#3498db", label="New"),
            ]
            ax.legend(handles=legend_elements, loc="upper right")

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close()

    def visualize_concept_map(
        self, spec: FPFSpec, output_path: Path, layout: str = "circular"
    ) -> None:
        """Generate concept relationship map visualization.

        Args:
            spec: The FPFSpec object
            output_path: Path to save PNG file
            layout: Layout type ("circular", "spring", "hierarchical")
        """
        # Create graph
        G = self.graph_generator.create_concept_relationship_graph(spec)

        if len(G.nodes()) == 0:
            raise ValueError("No concepts found for visualization")

        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Apply layout
        if layout == "circular":
            pos = self.graph_generator.apply_circular_layout(G)
        elif layout == "hierarchical":
            pos = self.graph_generator.apply_hierarchical_layout(G)
        else:
            pos = self.graph_generator.apply_force_directed_layout(G)

        # Get node colors by type
        node_colors = self.graph_generator.get_node_colors_by_attribute(G, "type")

        # Get node sizes
        node_sizes = self.graph_generator.get_node_sizes_by_importance(G, "degree")

        # Draw network
        nx.draw_networkx_nodes(
            G, pos, ax=ax, node_size=node_sizes, node_color=node_colors, alpha=0.8
        )

        # Draw edges
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.3, edge_color="#95a5a6")

        # Draw labels (abbreviated)
        labels = {node: node[:15] + "..." if len(node) > 15 else node for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=7)

        ax.set_title("Concept Relationship Map", fontsize=16, fontweight="bold", pad=20)
        ax.axis("off")

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close()

    def visualize_part_hierarchy(
        self, spec: FPFSpec, output_path: Path
    ) -> None:
        """Generate part hierarchy tree visualization.

        Args:
            spec: The FPFSpec object
            output_path: Path to save PNG file
        """
        # Create graph with parts as nodes
        G = nx.DiGraph()

        # Group patterns by part
        part_patterns: Dict[str, List[str]] = defaultdict(list)
        for pattern in spec.patterns:
            part = pattern.part or "Other"
            part_patterns[part].append(pattern.id)

        # Add part nodes
        for part, patterns in part_patterns.items():
            G.add_node(part, count=len(patterns))

        # Create edges between parts (if there are relationships)
        for relationship in spec.relationships:
            source_pattern = next((p for p in spec.patterns if p.id == relationship.source), None)
            target_pattern = next((p for p in spec.patterns if p.id == relationship.target), None)
            
            if source_pattern and target_pattern:
                source_part = source_pattern.part or "Other"
                target_part = target_pattern.part or "Other"
                if source_part != target_part:
                    if not G.has_edge(source_part, target_part):
                        G.add_edge(source_part, target_part, weight=1)
                    else:
                        G[source_part][target_part]["weight"] += 1

        if len(G.nodes()) == 0:
            raise ValueError("No parts found for visualization")

        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Apply tree layout
        pos = self.graph_generator.apply_tree_layout(G)

        # Get node sizes by count
        node_sizes = [G.nodes[node].get("count", 1) * 500 for node in G.nodes()]

        # Get node colors
        node_colors = plt.cm.Set3(np.linspace(0, 1, len(G.nodes())))

        # Draw network
        nx.draw_networkx_nodes(
            G, pos, ax=ax, node_size=node_sizes, node_color=node_colors, alpha=0.8
        )

        # Draw edges
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.3, edge_color="#95a5a6", arrows=True, arrowsize=20)

        # Draw labels
        labels = {node: f"{node}\n({G.nodes[node].get('count', 0)} patterns)" for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=10, font_weight="bold")

        ax.set_title("Part Hierarchy", fontsize=16, fontweight="bold", pad=20)
        ax.axis("off")

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close()

    def visualize_status_distribution(
        self, spec: FPFSpec, output_path: Path, chart_type: str = "bar"
    ) -> None:
        """Generate status distribution chart.

        Args:
            spec: The FPFSpec object
            output_path: Path to save PNG file
            chart_type: Chart type ("bar", "pie")
        """
        # Count patterns by status
        status_counts = {}
        for pattern in spec.patterns:
            status = pattern.status
            status_counts[status] = status_counts.get(status, 0) + 1

        if not status_counts:
            raise ValueError("No patterns found for visualization")

        # Create figure with theme
        from codomyrmex.cerebrum.visualization_base import BaseChartVisualizer
        chart_viz = BaseChartVisualizer(figure_size=self.figsize, dpi=self.dpi)

        statuses = list(status_counts.keys())
        counts = list(status_counts.values())

        # Use theme colors
        colors = [self.theme.get_status_color(status) for status in statuses]

        if chart_type == "pie":
            fig, ax = chart_viz.create_figure()
            ax.pie(
                counts,
                labels=statuses,
                autopct="%1.1f%%",
                colors=colors,
                startangle=90,
                textprops={"fontsize": self.theme.font.label_size},
            )
            chart_viz.format_title(ax, "Pattern Status Distribution")
        else:
            fig, ax = chart_viz.create_figure()
            bars = ax.bar(
                statuses,
                counts,
                color=colors,
                alpha=0.8,
                edgecolor="black",
                linewidth=1.0,
            )
            chart_viz.format_axes_labels(ax, xlabel="Status", ylabel="Count")
            chart_viz.format_title(ax, "Pattern Status Distribution")
            
            # Add value labels on bars
            chart_viz.add_value_labels(ax, bars, format_str="{:.0f}")

            # Add legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor=color, edgecolor="black", label=status, alpha=0.8)
                for status, color in zip(statuses, colors)
            ]
            self.theme.create_legend(ax, legend_elements, statuses, loc="upper right")

        # Apply theme
        self.theme.apply_to_axes(ax)

        # Save
        chart_viz.save_figure(fig, str(output_path))

