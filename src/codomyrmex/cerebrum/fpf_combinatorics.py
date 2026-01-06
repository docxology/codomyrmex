"""Comprehensive combinatorics analysis using CEREBRUM on FPF.

This module generates all possible combinations and analyses of FPF patterns
using CEREBRUM methods, including:
- Pattern pair analysis
- Dependency chain analysis
- Concept co-occurrence analysis
- Cross-part relationships
- Term network analysis
"""

import csv
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from codomyrmex.cerebrum import (
    BayesianNetwork,
    Case,
    CaseBase,
    CerebrumEngine,
    InferenceEngine,
)
from codomyrmex.cerebrum.visualization import CaseVisualizer, InferenceVisualizer, ModelVisualizer
from codomyrmex.fpf import FPFClient, FPFAnalyzer, TermAnalyzer
from codomyrmex.logging_monitoring import get_logger, setup_logging

logger = get_logger(__name__)


class FPFCombinatoricsAnalyzer:
    """Analyzes all combinatorics of FPF patterns using CEREBRUM."""

    def __init__(self, fpf_spec_path: Optional[str] = None, output_dir: str = "output/cerebrum/combinatorics"):
        """Initialize combinatorics analyzer.

        Args:
            fpf_spec_path: Path to FPF-Spec.md
            output_dir: Output directory (default: output/cerebrum/combinatorics)
        """
        setup_logging()
        self.logger = get_logger(__name__)

        # Load FPF
        self.fpf_client = FPFClient()
        if fpf_spec_path:
            self.spec = self.fpf_client.load_from_file(fpf_spec_path)
        else:
            self.spec = self.fpf_client.fetch_and_load()

        # Initialize CEREBRUM
        self.cerebrum = CerebrumEngine()
        self.fpf_analyzer = FPFAnalyzer(self.spec)
        self.term_analyzer = TermAnalyzer()

        # Output
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Initialized combinatorics analyzer with {len(self.spec.patterns)} patterns")

    def analyze_pattern_pairs(self) -> Dict[str, Any]:
        """Analyze all pairs of patterns for relationships.

        Returns:
            Dictionary with pair analysis results
        """
        self.logger.info("Analyzing pattern pairs")

        pairs_analysis = []
        patterns = self.spec.patterns

        # Analyze all pairs (limit to first 50 patterns for performance)
        for i, pattern1 in enumerate(patterns[:50]):
            for pattern2 in patterns[i + 1:50]:
                # Create cases for both patterns
                case1 = self._pattern_to_case(pattern1)
                case2 = self._pattern_to_case(pattern2)

                # Compute similarity
                similarity = self.cerebrum.case_base.compute_similarity(case1, case2)

                # Check for explicit relationships
                has_relationship = any(
                    (rel.source == pattern1.id and rel.target == pattern2.id) or
                    (rel.source == pattern2.id and rel.target == pattern1.id)
                    for rel in self.spec.relationships
                )

                # Get relationship types
                relationship_types = []
                for rel in self.spec.relationships:
                    if (rel.source == pattern1.id and rel.target == pattern2.id) or \
                       (rel.source == pattern2.id and rel.target == pattern1.id):
                        relationship_types.append(rel.type)

                pairs_analysis.append({
                    "pattern1": pattern1.id,
                    "pattern2": pattern2.id,
                    "similarity": similarity,
                    "has_relationship": has_relationship,
                    "relationship_types": relationship_types,
                    "shared_keywords": list(set(pattern1.keywords) & set(pattern2.keywords)),
                    "shared_concepts": self._find_shared_concepts(pattern1, pattern2),
                })

        # Sort by similarity
        pairs_analysis.sort(key=lambda x: x["similarity"], reverse=True)

        self.logger.info(f"Analyzed {len(pairs_analysis)} pattern pairs")
        return {
            "total_pairs": len(pairs_analysis),
            "high_similarity_pairs": [p for p in pairs_analysis if p["similarity"] > 0.7][:20],
            "related_pairs": [p for p in pairs_analysis if p["has_relationship"]][:20],
            "all_pairs": pairs_analysis[:100],  # Top 100
        }

    def analyze_dependency_chains(self) -> Dict[str, Any]:
        """Analyze dependency chains in FPF patterns.

        Returns:
            Dictionary with chain analysis
        """
        self.logger.info("Analyzing dependency chains")

        chains = []
        visited = set()

        def build_chain(pattern_id: str, current_chain: List[str], depth: int, max_depth: int = 5):
            """Recursively build dependency chains."""
            if depth > max_depth or pattern_id in visited:
                return

            visited.add(pattern_id)
            current_chain.append(pattern_id)

            pattern = self.spec.get_pattern_by_id(pattern_id)
            if not pattern:
                return

            # Get dependencies
            dependencies = []
            for dep_type, deps in pattern.dependencies.items():
                dependencies.extend(deps)

            if dependencies:
                for dep in dependencies[:3]:  # Limit branching
                    build_chain(dep, current_chain.copy(), depth + 1, max_depth)
            else:
                # End of chain
                if len(current_chain) > 1:
                    chains.append(current_chain.copy())

            visited.remove(pattern_id)

        # Build chains from all patterns
        for pattern in self.spec.patterns[:30]:  # Limit for performance
            build_chain(pattern.id, [], 0)

        # Analyze chains
        chain_analysis = []
        for chain in chains[:50]:  # Top 50 chains
            chain_patterns = [self.spec.get_pattern_by_id(pid) for pid in chain if self.spec.get_pattern_by_id(pid)]
            if chain_patterns:
                importance_scores = self.fpf_analyzer.calculate_pattern_importance()
                chain_importance = sum(importance_scores.get(pid, 0) for pid in chain) / len(chain)

                chain_analysis.append({
                    "chain": chain,
                    "length": len(chain),
                    "avg_importance": chain_importance,
                    "parts": list(set(p.part for p in chain_patterns if p.part)),
                })

        chain_analysis.sort(key=lambda x: x["avg_importance"], reverse=True)

        self.logger.info(f"Found {len(chains)} dependency chains")
        return {
            "total_chains": len(chains),
            "longest_chains": sorted(chains, key=len, reverse=True)[:10],
            "most_important_chains": chain_analysis[:20],
        }

    def analyze_concept_cooccurrence(self) -> Dict[str, Any]:
        """Analyze concept co-occurrence across patterns.

        Returns:
            Dictionary with co-occurrence analysis
        """
        self.logger.info("Analyzing concept co-occurrence")

        # Get co-occurrence matrix
        cooccurrence = self.term_analyzer.build_term_cooccurrence_matrix(self.spec)

        # Find strongest co-occurrences
        strong_pairs = []
        for term1, neighbors in cooccurrence.items():
            for term2, weight in neighbors.items():
                if weight >= 3:  # Minimum co-occurrence threshold
                    strong_pairs.append({
                        "term1": term1,
                        "term2": term2,
                        "cooccurrence_count": weight,
                    })

        strong_pairs.sort(key=lambda x: x["cooccurrence_count"], reverse=True)

        # Analyze concept clusters
        concept_clusters = self._find_concept_clusters(cooccurrence, min_weight=3)

        self.logger.info(f"Found {len(strong_pairs)} strong concept co-occurrences")
        return {
            "cooccurrence_matrix": {k: dict(v) for k, v in list(cooccurrence.items())[:50]},
            "strong_pairs": strong_pairs[:50],
            "concept_clusters": concept_clusters,
        }

    def analyze_cross_part_relationships(self) -> Dict[str, Any]:
        """Analyze relationships between patterns in different parts.

        Returns:
            Dictionary with cross-part analysis
        """
        self.logger.info("Analyzing cross-part relationships")

        cross_part_rels = []
        part_patterns = defaultdict(list)

        # Group patterns by part
        for pattern in self.spec.patterns:
            part = pattern.part or "Other"
            part_patterns[part].append(pattern.id)

        # Find relationships across parts
        for relationship in self.spec.relationships:
            source_pattern = self.spec.get_pattern_by_id(relationship.source)
            target_pattern = self.spec.get_pattern_by_id(relationship.target)

            if source_pattern and target_pattern:
                source_part = source_pattern.part or "Other"
                target_part = target_pattern.part or "Other"

                if source_part != target_part:
                    cross_part_rels.append({
                        "source_part": source_part,
                        "target_part": target_part,
                        "source_pattern": relationship.source,
                        "target_pattern": relationship.target,
                        "relationship_type": relationship.type,
                    })

        # Group by part pairs
        part_pair_counts = defaultdict(int)
        for rel in cross_part_rels:
            pair = tuple(sorted([rel["source_part"], rel["target_part"]]))
            part_pair_counts[pair] += 1

        self.logger.info(f"Found {len(cross_part_rels)} cross-part relationships")
        return {
            "total_cross_part_relationships": len(cross_part_rels),
            "relationships": cross_part_rels[:50],
            "part_pair_counts": dict(sorted(part_pair_counts.items(), key=lambda x: x[1], reverse=True)),
        }

    def generate_all_visualizations(self, analysis_results: Dict[str, Any]) -> None:
        """Generate all possible visualizations.

        Args:
            analysis_results: All analysis results
        """
        self.logger.info("Generating all visualizations")

        viz_dir = self.output_dir / "visualizations"
        viz_dir.mkdir(parents=True, exist_ok=True)

        # 1. Pattern pair similarity heatmap
        try:
            self._visualize_pair_similarity(analysis_results.get("pattern_pairs", {}), viz_dir)
        except Exception as e:
            self.logger.warning(f"Failed to visualize pair similarity: {e}")

        # 2. Dependency chain visualization
        try:
            self._visualize_dependency_chains(analysis_results.get("dependency_chains", {}), viz_dir)
        except Exception as e:
            self.logger.warning(f"Failed to visualize dependency chains: {e}")

        # 3. Concept co-occurrence network
        try:
            self._visualize_concept_cooccurrence(analysis_results.get("concept_cooccurrence", {}), viz_dir)
        except Exception as e:
            self.logger.warning(f"Failed to visualize concept co-occurrence: {e}")

        # 4. Cross-part relationship network
        try:
            self._visualize_cross_part_relationships(analysis_results.get("cross_part_relationships", {}), viz_dir)
        except Exception as e:
            self.logger.warning(f"Failed to visualize cross-part relationships: {e}")

    def _visualize_pair_similarity(self, pairs_data: Dict[str, Any], viz_dir: Path) -> None:
        """Visualize pattern pair similarities with enhanced styling."""
        try:
            from codomyrmex.cerebrum.visualization_base import BaseHeatmapVisualizer
            import matplotlib.pyplot as plt
            import numpy as np

            pairs = pairs_data.get("all_pairs", [])[:30]  # Top 30 pairs

            if not pairs:
                # Still export empty data
                csv_path = viz_dir / "pair_similarity_heatmap.csv"
                with open(csv_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["pattern1", "pattern2", "similarity", "has_relationship", "relationship_types", "shared_keywords", "shared_concepts"])
                    writer.writeheader()
                self.logger.info("Exported empty pair similarity data")
                return

            # Create similarity matrix
            pattern_ids = sorted(list(set(p["pattern1"] for p in pairs) | set(p["pattern2"] for p in pairs)))
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
            ax.set_xticklabels(pattern_ids, rotation=45, ha="right", fontsize=heatmap_viz.theme.font.tick_size)
            ax.set_yticklabels(pattern_ids, fontsize=heatmap_viz.theme.font.tick_size)

            # Update colorbar
            im = ax.images[0]
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label("Similarity Score", fontsize=heatmap_viz.theme.font.label_size, fontweight=heatmap_viz.theme.font.weight_label)
            cbar.ax.tick_params(labelsize=heatmap_viz.theme.font.tick_size)

            # Apply theme
            heatmap_viz.theme.apply_to_axes(ax)

            # Save
            heatmap_viz.save_figure(fig, str(viz_dir / "pair_similarity_heatmap.png"))
            self.logger.info("Saved pair similarity heatmap")
            
            # Export raw data - pair list
            csv_path = viz_dir / "pair_similarity_heatmap.csv"
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["pattern1", "pattern2", "similarity", "has_relationship", "relationship_types", "shared_keywords", "shared_concepts"])
                writer.writeheader()
                for pair in pairs:
                    row = {
                        "pattern1": pair.get("pattern1", ""),
                        "pattern2": pair.get("pattern2", ""),
                        "similarity": pair.get("similarity", 0.0),
                        "has_relationship": pair.get("has_relationship", False),
                        "relationship_types": ",".join(pair.get("relationship_types", [])),
                        "shared_keywords": ",".join(pair.get("shared_keywords", [])),
                        "shared_concepts": ",".join(pair.get("shared_concepts", []))
                    }
                    writer.writerow(row)
            self.logger.info(f"Exported pair similarity raw data to {csv_path}")
            
            # Export similarity matrix
            matrix_path = viz_dir / "pair_similarity_matrix.csv"
            with open(matrix_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                # Header row
                writer.writerow([""] + pattern_ids)
                # Data rows
                for i, pattern_id in enumerate(pattern_ids):
                    row = [pattern_id] + similarity_matrix[i].tolist()
                    writer.writerow(row)
            self.logger.info(f"Exported similarity matrix to {matrix_path}")
        except ImportError:
            self.logger.warning("matplotlib not available for visualization")

    def _visualize_dependency_chains(self, chains_data: Dict[str, Any], viz_dir: Path) -> None:
        """Visualize dependency chains with enhanced styling."""
        try:
            from codomyrmex.cerebrum.visualization_base import BaseNetworkVisualizer
            import matplotlib.pyplot as plt
            import networkx as nx

            chains = chains_data.get("longest_chains", [])[:10]
            all_chains = chains_data.get("chains", [])
            important_chains = chains_data.get("most_important_chains", [])

            # Always export raw data, even if empty
            json_data = {
                "chains": all_chains,
                "longest_chains": chains_data.get("longest_chains", []),
                "most_important_chains": important_chains,
                "total_chains": chains_data.get("total_chains", 0)
            }
            json_path = viz_dir / "dependency_chains.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2)
            self.logger.info(f"Exported dependency chains raw data to {json_path}")

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
            pos = network_viz.apply_layout(G, layout="hierarchical", k=2.0, iterations=100)

            # Get node sizes and colors
            node_sizes = network_viz.get_node_sizes(G, metric="degree", min_size=500, max_size=2500)
            node_colors = network_viz.theme.get_color_sequence(len(G.nodes()), "primary")

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
                width=edge_widths if edge_widths else 1.5,
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
            labels = {node: node[:20] + "..." if len(node) > 20 else node for node in G.nodes()}
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

    def _visualize_concept_cooccurrence(self, cooccurrence_data: Dict[str, Any], viz_dir: Path) -> None:
        """Visualize concept co-occurrence network with enhanced styling."""
        try:
            from codomyrmex.cerebrum.visualization_base import BaseNetworkVisualizer
            import matplotlib.pyplot as plt
            import networkx as nx

            strong_pairs = cooccurrence_data.get("strong_pairs", [])[:50]

            # Always export raw data, even if empty
            # Build network for data export
            G = nx.Graph()
            if strong_pairs:
                for pair in strong_pairs:
                    G.add_edge(pair["term1"], pair["term2"], weight=pair["cooccurrence_count"])

            # Export JSON format
            json_data = {
                "nodes": [{"term": n, "degree": G.degree(n)} for n in G.nodes()],
                "edges": [{"term1": u, "term2": v, "weight": G[u][v].get("weight", 1)} for u, v in G.edges()]
            }
            json_path = viz_dir / "concept_cooccurrence_network.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2)
            self.logger.info(f"Exported concept co-occurrence network JSON to {json_path}")

            # Export CSV format (edge list)
            csv_path = viz_dir / "concept_cooccurrence_network.csv"
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["term1", "term2", "weight"])
                writer.writeheader()
                for u, v in G.edges():
                    writer.writerow({
                        "term1": u,
                        "term2": v,
                        "weight": G[u][v].get("weight", 1)
                    })
            self.logger.info(f"Exported concept co-occurrence network CSV to {csv_path}")

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
            node_sizes = network_viz.get_node_sizes(G, metric="degree", min_size=300, max_size=3000)
            node_colors = network_viz.theme.get_color_sequence(len(G.nodes()), "accent")

            # Get edge widths
            edge_widths = network_viz.get_edge_widths(G, min_width=0.5, max_width=3.0)

            # Draw edges first
            nx.draw_networkx_edges(
                G,
                pos,
                ax=ax,
                width=edge_widths if edge_widths else 1.0,
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
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor=network_viz.theme.colors.node_default, edgecolor="black", label="Concept", alpha=0.9),
                plt.Line2D([0], [0], color=network_viz.theme.colors.edge_default, linewidth=2, label="Co-occurrence", alpha=0.5),
            ]
            network_viz.theme.create_legend(ax, legend_elements, ["Concept", "Co-occurrence"], loc="upper right")

            # Save
            network_viz.save_figure(fig, str(viz_dir / "concept_cooccurrence_network.png"))
            self.logger.info("Saved concept co-occurrence network")
        except ImportError:
            self.logger.warning("matplotlib/networkx not available")

    def _visualize_cross_part_relationships(self, cross_part_data: Dict[str, Any], viz_dir: Path) -> None:
        """Visualize cross-part relationships with enhanced styling."""
        try:
            from codomyrmex.cerebrum.visualization_base import BaseNetworkVisualizer
            import matplotlib.pyplot as plt
            import networkx as nx

            part_pair_counts = cross_part_data.get("part_pair_counts", {})

            # Always export raw data, even if empty
            csv_path = viz_dir / "cross_part_relationships.csv"
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["part1", "part2", "relationship_count"])
                writer.writeheader()
                if part_pair_counts:
                    for (part1, part2), count in part_pair_counts.items():
                        writer.writerow({
                            "part1": part1,
                            "part2": part2,
                            "relationship_count": count
                        })
            self.logger.info(f"Exported cross-part relationships raw data to {csv_path}")

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
            node_sizes = network_viz.get_node_sizes(G, metric="degree", min_size=1000, max_size=4000)
            node_colors = network_viz.theme.get_color_sequence(len(G.nodes()), "primary")

            # Get edge widths
            edge_widths = network_viz.get_edge_widths(G, min_width=1.0, max_width=5.0)

            # Draw edges first
            nx.draw_networkx_edges(
                G,
                pos,
                ax=ax,
                width=edge_widths if edge_widths else 2.0,
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
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor=network_viz.theme.colors.node_default, edgecolor="black", label="Part", alpha=0.9),
                plt.Line2D([0], [0], color=network_viz.theme.colors.edge_default, linewidth=3, label="Relationship", alpha=0.7),
            ]
            network_viz.theme.create_legend(ax, legend_elements, ["Part", "Relationship"], loc="upper right")

            # Save
            network_viz.save_figure(fig, str(viz_dir / "cross_part_relationships.png"))
            self.logger.info("Saved cross-part relationships visualization")
        except ImportError:
            self.logger.warning("matplotlib/networkx not available")

    def _pattern_to_case(self, pattern) -> Case:
        """Convert FPF pattern to CEREBRUM case."""
        features = {
            "status": pattern.status,
            "part": pattern.part or "Other",
            "num_keywords": len(pattern.keywords),
            "num_dependencies": sum(len(deps) for deps in pattern.dependencies.values()),
        }
        return Case(
            case_id=f"pattern_{pattern.id}",
            features=features,
            context={"pattern_id": pattern.id, "title": pattern.title},
        )

    def _find_shared_concepts(self, pattern1, pattern2) -> List[str]:
        """Find shared concepts between two patterns."""
        concepts1 = self.spec.get_concepts_by_pattern(pattern1.id)
        concepts2 = self.spec.get_concepts_by_pattern(pattern2.id)

        names1 = {c.name for c in concepts1}
        names2 = {c.name for c in concepts2}

        return list(names1 & names2)

    def _find_concept_clusters(self, cooccurrence: Dict[str, Dict[str, int]], min_weight: int = 3) -> List[List[str]]:
        """Find clusters of co-occurring concepts."""
        try:
            import networkx as nx

            G = nx.Graph()

            for term1, neighbors in cooccurrence.items():
                for term2, weight in neighbors.items():
                    if weight >= min_weight:
                        G.add_edge(term1, term2, weight=weight)

            # Find connected components (clusters)
            clusters = list(nx.connected_components(G))

            return [sorted(list(cluster)) for cluster in clusters if len(cluster) > 2]
        except ImportError:
            return []

    def run_comprehensive_combinatorics(self) -> Dict[str, Any]:
        """Run all combinatorics analyses.

        Returns:
            Complete combinatorics analysis results
        """
        self.logger.info("Running comprehensive combinatorics analysis")

        results = {
            "pattern_pairs": self.analyze_pattern_pairs(),
            "dependency_chains": self.analyze_dependency_chains(),
            "concept_cooccurrence": self.analyze_concept_cooccurrence(),
            "cross_part_relationships": self.analyze_cross_part_relationships(),
        }

        # Generate visualizations
        self.generate_all_visualizations(results)

        # Export results
        import json
        json_path = self.output_dir / "combinatorics_analysis.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        self.logger.info(f"Combinatorics analysis complete. Results saved to {self.output_dir}")
        return results

