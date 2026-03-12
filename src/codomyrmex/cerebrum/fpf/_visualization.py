import csv
import json
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

try:
    import matplotlib.pyplot as plt
    import networkx as nx
    import numpy as np
    from matplotlib.patches import Patch

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from codomyrmex.cerebrum.visualization.base import (
    BaseHeatmapVisualizer,
    BaseNetworkVisualizer,
)

logger = get_logger(__name__)


class FPFCombinatoricsVisualizationMixin:
    """Mixin for FPF combinatorics visualization generation."""

    def generate_all_visualizations(self, analysis_results: dict[str, Any]) -> None:
        """Generate all possible visualizations.

        Args:
            analysis_results: All analysis results
        """
        self.logger.info("Generating all visualizations")

        viz_dir = self.output_dir / "visualizations"
        viz_dir.mkdir(parents=True, exist_ok=True)

        # 1. Pattern pair similarity heatmap
        try:
            self._visualize_pair_similarity(
                analysis_results.get("pattern_pairs", {}), viz_dir
            )
        except Exception as e:
            self.logger.warning("Failed to visualize pair similarity: %s", e)

        # 2. Dependency chain visualization
        try:
            self._visualize_dependency_chains(
                analysis_results.get("dependency_chains", {}), viz_dir
            )
        except Exception as e:
            self.logger.warning("Failed to visualize dependency chains: %s", e)

        # 3. Concept co-occurrence network
        try:
            self._visualize_concept_cooccurrence(
                analysis_results.get("concept_cooccurrence", {}), viz_dir
            )
        except Exception as e:
            self.logger.warning("Failed to visualize concept co-occurrence: %s", e)

        # 4. Cross-part relationship network
        try:
            self._visualize_cross_part_relationships(
                analysis_results.get("cross_part_relationships", {}), viz_dir
            )
        except Exception as e:
            self.logger.warning("Failed to visualize cross-part relationships: %s", e)

    def _visualize_pair_similarity(
        self, pairs_data: dict[str, Any], viz_dir: Path
    ) -> None:
        """Visualize pattern pair similarities with enhanced styling."""
        try:
            pairs = pairs_data.get("all_pairs", [])[:30]  # Top 30 pairs

            if not pairs:
                # Still export empty data
                csv_path = viz_dir / "pair_similarity_heatmap.csv"
                with open(csv_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=[
                            "pattern1",
                            "pattern2",
                            "similarity",
                            "has_relationship",
                            "relationship_types",
                            "shared_keywords",
                            "shared_concepts",
                        ],
                    )
                    writer.writeheader()
                self.logger.info("Exported empty pair similarity data")
                return

            # Create similarity matrix
            pattern_ids = sorted(
                {p["pattern1"] for p in pairs} | {p["pattern2"] for p in pairs}
            )
            similarity_matrix = np.zeros((len(pattern_ids), len(pattern_ids)))

            for pair in pairs:
                i = pattern_ids.index(pair["pattern1"])
                j = pattern_ids.index(pair["pattern2"])
                similarity_matrix[i, j] = pair["similarity"]
                similarity_matrix[j, i] = pair["similarity"]

            # Use enhanced heatmap visualizer
            heatmap_viz = BaseHeatmapVisualizer(figure_size=(18, 14), dpi=300)
            fig, ax = heatmap_viz.create_heatmap(
                similarity_matrix,
                pattern_ids,
                pattern_ids,
                colormap="YlOrRd",
            )

            # Format title and labels
            heatmap_viz.format_title(ax, "Pattern Pair Similarity Matrix")
            ax.set_xticklabels(
                pattern_ids,
                rotation=45,
                ha="right",
                fontsize=heatmap_viz.theme.font.tick_size,
            )
            ax.set_yticklabels(pattern_ids, fontsize=heatmap_viz.theme.font.tick_size)

            # Update colorbar
            im = ax.images[0]
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label(
                "Similarity Score",
                fontsize=heatmap_viz.theme.font.label_size,
                fontweight=heatmap_viz.theme.font.weight_label,
            )
            cbar.ax.tick_params(labelsize=heatmap_viz.theme.font.tick_size)

            # Apply theme
            heatmap_viz.theme.apply_to_axes(ax)

            # Save
            heatmap_viz.save_figure(fig, str(viz_dir / "pair_similarity_heatmap.png"))
            self.logger.info("Saved pair similarity heatmap")

            # Export raw data - pair list
            csv_path = viz_dir / "pair_similarity_heatmap.csv"
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "pattern1",
                        "pattern2",
                        "similarity",
                        "has_relationship",
                        "relationship_types",
                        "shared_keywords",
                        "shared_concepts",
                    ],
                )
                writer.writeheader()
                for pair in pairs:
                    row = {
                        "pattern1": pair.get("pattern1", ""),
                        "pattern2": pair.get("pattern2", ""),
                        "similarity": pair.get("similarity", 0.0),
                        "has_relationship": pair.get("has_relationship", False),
                        "relationship_types": ",".join(
                            pair.get("relationship_types", [])
                        ),
                        "shared_keywords": ",".join(pair.get("shared_keywords", [])),
                        "shared_concepts": ",".join(pair.get("shared_concepts", [])),
                    }
                    writer.writerow(row)
            self.logger.info("Exported pair similarity raw data to %s", csv_path)

            # Export similarity matrix
            matrix_path = viz_dir / "pair_similarity_matrix.csv"
            with open(matrix_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                # Header row
                writer.writerow(["", *pattern_ids])
                # Data rows
                for i, pattern_id in enumerate(pattern_ids):
                    row = [pattern_id, *similarity_matrix[i].tolist()]
                    writer.writerow(row)
            self.logger.info("Exported similarity matrix to %s", matrix_path)
        except ImportError:
            self.logger.warning("matplotlib not available for visualization")

    def _visualize_dependency_chains(
        self, chains_data: dict[str, Any], viz_dir: Path
    ) -> None:
        """Visualize dependency chains with enhanced styling."""
        try:
            chains = chains_data.get("longest_chains", [])[:10]
            all_chains = chains_data.get("chains", [])
            important_chains = chains_data.get("most_important_chains", [])

            # Always export raw data, even if empty
            json_data = {
                "chains": all_chains,
                "longest_chains": chains_data.get("longest_chains", []),
                "most_important_chains": important_chains,
                "total_chains": chains_data.get("total_chains", 0),
            }
            json_path = viz_dir / "dependency_chains.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2)
            self.logger.info("Exported dependency chains raw data to %s", json_path)

            if not chains:
                self.logger.info("No dependency chains to visualize")
                return

            # Create graph from chains
            G = nx.DiGraph()

            for chain in chains:
                for i in range(len(chain) - 1):
                    G.add_edge(chain[i], chain[i + 1], weight=1.0)

            if len(G.nodes()) == 0:
                return

            # Use enhanced network visualizer
            network_viz = BaseNetworkVisualizer(figure_size=(22, 14), dpi=300)
            fig, ax = network_viz.create_figure()

            # Apply layout
            pos = network_viz.apply_layout(
                G, layout="hierarchical", k=2.0, iterations=100
            )

            # Get node sizes and colors
            node_sizes = network_viz.get_node_sizes(
                G, metric="degree", min_size=500, max_size=2500
            )
            node_colors = network_viz.theme.get_color_sequence(
                len(G.nodes()), "primary"
            )

            # Get edge widths
            edge_widths = network_viz.get_edge_widths(G, min_width=1.0, max_width=3.0)

            # Draw edges first
            nx.draw_networkx_edges(
                G,
                pos,
                ax=ax,
                arrows=True,
                arrowsize=30,
                edge_color=network_viz.theme.colors.edge_default,
                width=edge_widths or 1.5,
                alpha=0.6,
                arrowstyle="->",
                connectionstyle="arc3,rad=0.1",
            )

            # Draw nodes
            nx.draw_networkx_nodes(
                G,
                pos,
                ax=ax,
                node_color=node_colors,
                node_size=node_sizes,
                alpha=0.9,
                edgecolors="black",
                linewidths=1.5,
            )

            # Draw labels
            labels = {
                node: node[:20] + "..." if len(node) > 20 else node
                for node in G.nodes()
            }
            nx.draw_networkx_labels(
                G,
                pos,
                labels,
                ax=ax,
                font_size=network_viz.theme.font.tick_size,
                font_weight="bold",
            )

            # Format title
            network_viz.format_title(ax, "Dependency Chains")

            # Apply theme
            network_viz.theme.apply_to_axes(ax)
            ax.axis("off")

            # Save
            network_viz.save_figure(fig, str(viz_dir / "dependency_chains.png"))
            self.logger.info("Saved dependency chains visualization")
        except ImportError:
            self.logger.warning("matplotlib/networkx not available")

    def _visualize_concept_cooccurrence(
        self, cooccurrence_data: dict[str, Any], viz_dir: Path
    ) -> None:
        """Visualize concept co-occurrence network with enhanced styling."""
        try:
            strong_pairs = cooccurrence_data.get("strong_pairs", [])[:50]

            # Always export raw data, even if empty
            # Build network for data export
            G = nx.Graph()
            if strong_pairs:
                for pair in strong_pairs:
                    G.add_edge(
                        pair["term1"], pair["term2"], weight=pair["cooccurrence_count"]
                    )

            # Export JSON format
            json_data = {
                "nodes": [{"term": n, "degree": G.degree(n)} for n in G.nodes()],
                "edges": [
                    {"term1": u, "term2": v, "weight": G[u][v].get("weight", 1)}
                    for u, v in G.edges()
                ],
            }
            json_path = viz_dir / "concept_cooccurrence_network.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2)
            self.logger.info(
                "Exported concept co-occurrence network JSON to %s", json_path
            )

            # Export CSV format (edge list)
            csv_path = viz_dir / "concept_cooccurrence_network.csv"
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["term1", "term2", "weight"])
                writer.writeheader()
                for u, v in G.edges():
                    writer.writerow(
                        {"term1": u, "term2": v, "weight": G[u][v].get("weight", 1)}
                    )
            self.logger.info(
                "Exported concept co-occurrence network CSV to %s", csv_path
            )

            if not strong_pairs:
                self.logger.info("No concept co-occurrence pairs to visualize")
                return

            if len(G.nodes()) == 0:
                return

            # Use enhanced network visualizer
            network_viz = BaseNetworkVisualizer(figure_size=(22, 18), dpi=300)
            fig, ax = network_viz.create_figure()

            # Apply layout
            pos = network_viz.apply_layout(G, layout="spring", k=3.0, iterations=100)

            # Get node sizes and colors
            node_sizes = network_viz.get_node_sizes(
                G, metric="degree", min_size=300, max_size=3000
            )
            node_colors = network_viz.theme.get_color_sequence(len(G.nodes()), "accent")

            # Get edge widths
            edge_widths = network_viz.get_edge_widths(G, min_width=0.5, max_width=3.0)

            # Draw edges first
            nx.draw_networkx_edges(
                G,
                pos,
                ax=ax,
                width=edge_widths or 1.0,
                alpha=0.5,
                edge_color=network_viz.theme.colors.edge_default,
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

            # Label only important nodes
            important_nodes = [n for n in G.nodes() if G.degree(n) > 3]
            labels = {n: n[:20] + "..." if len(n) > 20 else n for n in important_nodes}
            nx.draw_networkx_labels(
                G,
                pos,
                labels,
                ax=ax,
                font_size=network_viz.theme.font.tick_size,
                font_weight="bold",
            )

            # Format title
            network_viz.format_title(ax, "Concept Co-occurrence Network")

            # Apply theme
            network_viz.theme.apply_to_axes(ax)
            ax.axis("off")

            # Add legend
            legend_elements = [
                Patch(
                    facecolor=network_viz.theme.colors.node_default,
                    edgecolor="black",
                    label="Concept",
                    alpha=0.9,
                ),
                plt.Line2D(
                    [0],
                    [0],
                    color=network_viz.theme.colors.edge_default,
                    linewidth=2,
                    label="Co-occurrence",
                    alpha=0.5,
                ),
            ]
            network_viz.theme.create_legend(
                ax, legend_elements, ["Concept", "Co-occurrence"], loc="upper right"
            )

            # Save
            network_viz.save_figure(
                fig, str(viz_dir / "concept_cooccurrence_network.png")
            )
            self.logger.info("Saved concept co-occurrence network")
        except ImportError:
            self.logger.warning("matplotlib/networkx not available")

    def _visualize_cross_part_relationships(
        self, cross_part_data: dict[str, Any], viz_dir: Path
    ) -> None:
        """Visualize cross-part relationships with enhanced styling."""
        try:
            part_pair_counts = cross_part_data.get("part_pair_counts", {})

            # Always export raw data, even if empty
            csv_path = viz_dir / "cross_part_relationships.csv"
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["part1", "part2", "relationship_count"]
                )
                writer.writeheader()
                if part_pair_counts:
                    for (part1, part2), count in part_pair_counts.items():
                        writer.writerow(
                            {
                                "part1": part1,
                                "part2": part2,
                                "relationship_count": count,
                            }
                        )
            self.logger.info(
                "Exported cross-part relationships raw data to %s", csv_path
            )

            if not part_pair_counts:
                self.logger.info("No cross-part relationships to visualize")
                return

            G = nx.Graph()

            for (part1, part2), count in part_pair_counts.items():
                G.add_edge(part1, part2, weight=count)

            if len(G.nodes()) == 0:
                return

            # Use enhanced network visualizer
            network_viz = BaseNetworkVisualizer(figure_size=(18, 14), dpi=300)
            fig, ax = network_viz.create_figure()

            # Apply layout
            pos = network_viz.apply_layout(G, layout="circular")

            # Get node sizes and colors
            node_sizes = network_viz.get_node_sizes(
                G, metric="degree", min_size=1000, max_size=4000
            )
            node_colors = network_viz.theme.get_color_sequence(
                len(G.nodes()), "primary"
            )

            # Get edge widths
            edge_widths = network_viz.get_edge_widths(G, min_width=1.0, max_width=5.0)

            # Draw edges first
            nx.draw_networkx_edges(
                G,
                pos,
                ax=ax,
                width=edge_widths or 2.0,
                alpha=0.7,
                edge_color=network_viz.theme.colors.edge_default,
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
                linewidths=2.0,
            )

            # Draw labels
            labels = {node: node for node in G.nodes()}
            nx.draw_networkx_labels(
                G,
                pos,
                labels,
                ax=ax,
                font_size=network_viz.theme.font.label_size,
                font_weight="bold",
            )

            # Format title
            network_viz.format_title(ax, "Cross-Part Relationships")

            # Apply theme
            network_viz.theme.apply_to_axes(ax)
            ax.axis("off")

            # Add legend
            legend_elements = [
                Patch(
                    facecolor=network_viz.theme.colors.node_default,
                    edgecolor="black",
                    label="Part",
                    alpha=0.9,
                ),
                plt.Line2D(
                    [0],
                    [0],
                    color=network_viz.theme.colors.edge_default,
                    linewidth=3,
                    label="Relationship",
                    alpha=0.7,
                ),
            ]
            network_viz.theme.create_legend(
                ax, legend_elements, ["Part", "Relationship"], loc="upper right"
            )

            # Save
            network_viz.save_figure(fig, str(viz_dir / "cross_part_relationships.png"))
            self.logger.info("Saved cross-part relationships visualization")
        except ImportError:
            self.logger.warning("matplotlib/networkx not available")
