from typing import Any, Dict, List, Optional, Tuple

from matplotlib.figure import Figure
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from codomyrmex.cerebrum.bayesian import BayesianNetwork
from codomyrmex.cerebrum.cases import Case
from codomyrmex.cerebrum.exceptions import VisualizationError
from codomyrmex.cerebrum.visualization_base import (
    BaseChartVisualizer,
    BaseNetworkVisualizer,
    BaseVisualizer,
)
from codomyrmex.cerebrum.visualization_theme import (
    VisualizationTheme,
    get_default_theme,
)
from codomyrmex.logging_monitoring import get_logger


try:
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    Figure = Any
    Patch = Any
    plt = None

try:
    import networkx as nx
except ImportError:
    nx = None

logger = get_logger(__name__)


class ModelVisualizer(BaseNetworkVisualizer):
    """Visualizes Bayesian networks and model structures with enhanced styling."""

    def __init__(
        self,
        figure_size: Tuple[float, float] = (14, 10),
        dpi: int = 300,
        theme: Optional[VisualizationTheme] = None,
    ):
        """Initialize visualizer.

        Args:
            figure_size: Figure size (width, height)
            dpi: DPI for figures
            theme: Visualization theme (default: use global theme)
        """
        super().__init__(figure_size, dpi, theme)

    def visualize_network(
        self,
        network: BayesianNetwork,
        layout: str = "hierarchical",
        node_size_metric: str = "degree",
        show_legend: bool = True,
    ) -> Figure:
        """Visualize Bayesian network structure with enhanced styling.

        Args:
            network: Bayesian network to visualize
            layout: Layout algorithm ("hierarchical", "spring", "kamada_kawai")
            node_size_metric: Metric for node sizing ("degree", "betweenness", "pagerank")
            show_legend: Whether to show legend

        Returns:
            Matplotlib figure
        """
        # Create directed graph
        G = nx.DiGraph()

        # Add nodes with attributes
        for node in network.nodes:
            G.add_node(node, label=node)

        # Add edges
        for parent, children in network.edges.items():
            for child in children:
                G.add_edge(parent, child, weight=1.0)

        if len(G.nodes()) == 0:
            raise ValueError("Network has no nodes")

        # Create figure
        fig, ax = self.create_figure()

        # Apply layout
        pos = self.apply_layout(G, layout=layout, k=2.0, iterations=100)

        # Get node sizes by importance
        node_sizes = self.get_node_sizes(G, metric=node_size_metric, min_size=300, max_size=3000)

        # Get node colors (use primary palette)
        node_colors = self.theme.get_color_sequence(len(G.nodes()), "primary")
        if len(node_colors) < len(G.nodes()):
            node_colors = (node_colors * ((len(G.nodes()) // len(node_colors)) + 1))[:len(G.nodes())]

        # Get edge widths
        edge_widths = self.get_edge_widths(G, min_width=0.8, max_width=2.5)

        # Draw edges first (so nodes appear on top)
        nx.draw_networkx_edges(
            G,
            pos,
            ax=ax,
            arrows=True,
            arrowsize=25,
            edge_color=self.theme.colors.edge_default,
            width=edge_widths if edge_widths else 1.0,
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

        # Draw labels with better positioning
        labels = {node: node[:20] + "..." if len(node) > 20 else node for node in G.nodes()}
        nx.draw_networkx_labels(
            G,
            pos,
            labels,
            ax=ax,
            font_size=self.theme.font.tick_size,
            font_weight="bold",
            font_family=self.theme.font.family,
        )

        # Format title
        self.format_title(ax, f"Bayesian Network: {network.name}")

        # Format axes
        self.theme.apply_to_axes(ax)
        ax.axis("off")

        # Add legend
        if show_legend:
            legend_elements = [
                Patch(
                    facecolor=self.theme.colors.node_default,
                    edgecolor="black",
                    label="Node",
                    alpha=0.9,
                ),
                plt.Line2D(
                    [0],
                    [0],
                    color=self.theme.colors.edge_default,
                    linewidth=2,
                    label="Edge",
                    alpha=0.6,
                ),
            ]
            self.theme.create_legend(ax, legend_elements, ["Node", "Edge"], loc="upper right")

        plt.tight_layout(pad=self.theme.figure.tight_layout_pad)
        return fig

    def visualize_inference_results(
        self,
        results: Dict[str, Any],
        chart_type: str = "bar",
        show_values: bool = True,
    ) -> Figure:
        """Visualize inference results as enhanced bar charts.

        Args:
            results: Inference results dictionary mapping variable names to distributions
            chart_type: Chart type ("bar", "grouped", "stacked")
            show_values: Whether to show value labels on bars

        Returns:
            Matplotlib figure
        """
        if not results:
            raise ValueError("No results to visualize")

        n_results = len(results)
        fig, axes = self.create_figure(nrows=n_results, ncols=1)

        if n_results == 1:
            axes = [axes]

        colors = self.theme.get_color_sequence(len(results), "accent")

        for idx, (var, dist) in enumerate(results.items()):
            ax = axes[idx]

            values = dist.values
            probabilities = dist.probabilities

            # Create bars with color gradient
            bar_colors = [
                self.theme.get_color_for_value(
                    p, min(probabilities), max(probabilities), "viridis"
                )
                for p in probabilities
            ]

            bars = ax.bar(
                range(len(values)),
                probabilities,
                color=bar_colors,
                alpha=0.8,
                edgecolor="black",
                linewidth=1.0,
            )

            # Format axes
            ax.set_xticks(range(len(values)))
            ax.set_xticklabels([str(v) for v in values], rotation=45, ha="right")
            self.format_axes_labels(ax, xlabel="Value", ylabel="Probability")
            self.theme.format_axis_percentage(ax, axis="y")

            # Format title
            self.format_title(ax, f"Posterior Distribution: {var}")

            # Add value labels
            if show_values:
                self.add_value_labels(ax, bars, format_str="{:.3f}")

            # Add reference line for uniform distribution
            uniform_prob = 1.0 / len(values) if len(values) > 0 else 0.0
            self.add_reference_line(
                ax,
                uniform_prob,
                orientation="horizontal",
                color="#e74c3c",
                linestyle="--",
                label="Uniform",
                alpha=0.5,
            )

            # Apply theme
            self.theme.apply_to_axes(ax)

            # Add legend
            if idx == 0:
                legend_elements = [
                    Patch(facecolor="#440154", edgecolor="black", label="Low Probability", alpha=0.8),
                    Patch(facecolor="#fde725", edgecolor="black", label="High Probability", alpha=0.8),
                    plt.Line2D(
                        [0],
                        [0],
                        color="#e74c3c",
                        linestyle="--",
                        label="Uniform Distribution",
                        linewidth=1.5,
                    ),
                ]
                self.theme.create_legend(ax, legend_elements, ["Low", "High", "Uniform"], loc="upper right")

        plt.tight_layout(pad=self.theme.figure.tight_layout_pad)
        return fig


class CaseVisualizer(BaseChartVisualizer):
    """Visualizes case similarity and retrieval with enhanced styling."""

    def __init__(
        self,
        figure_size: Tuple[float, float] = (12, 10),
        dpi: int = 300,
        theme: Optional[VisualizationTheme] = None,
    ):
        """Initialize case visualizer.

        Args:
            figure_size: Figure size
            dpi: DPI for figures
            theme: Visualization theme
        """
        super().__init__(figure_size, dpi, theme)

    def plot_case_similarity(
        self,
        cases: List[Tuple[Case, float]],
        query_case: Optional[Case] = None,
        group_by: Optional[str] = None,
        show_threshold: bool = True,
        threshold: float = 0.5,
    ) -> Figure:
        """Plot case similarity scores with enhanced styling.

        Args:
            cases: List of (case, similarity) tuples
            query_case: Optional query case for reference
            group_by: Optional attribute to group by ("status", "part")
            show_threshold: Whether to show similarity threshold line
            threshold: Similarity threshold value

        Returns:
            Matplotlib figure
        """
        if not cases:
            raise ValueError("No cases to visualize")

        # Sort by similarity (descending)
        cases_sorted = sorted(cases, key=lambda x: x[1], reverse=True)

        case_ids = [case.case_id for case, _ in cases_sorted]
        similarities = [sim for _, sim in cases_sorted]

        # Create figure
        fig, ax = self.create_figure()

        # Get colors based on similarity (gradient)
        bar_colors = [
            self.get_color_for_value(sim, min(similarities), max(similarities), "viridis")
            for sim in similarities
        ]

        # Create horizontal bars
        y_pos = np.arange(len(case_ids))
        bars = ax.barh(
            y_pos,
            similarities,
            color=bar_colors,
            alpha=0.8,
            edgecolor="black",
            linewidth=0.8,
        )

        # Format axes
        ax.set_yticks(y_pos)
        ax.set_yticklabels(case_ids, fontsize=self.theme.font.tick_size)
        self.format_axes_labels(ax, xlabel="Similarity Score", ylabel="Case ID")
        self.theme.format_axis_percentage(ax, axis="x")

        # Format title
        self.format_title(ax, "Case Similarity Scores")

        # Add threshold line
        if show_threshold:
            self.add_reference_line(
                ax,
                threshold,
                orientation="vertical",
                color="#e74c3c",
                linestyle="--",
                linewidth=2,
                label=f"Threshold ({threshold:.2f})",
                alpha=0.7,
            )

        # Add value labels
        for i, (bar, sim) in enumerate(zip(bars, similarities)):
            ax.text(
                sim + 0.01,
                i,
                f"{sim:.3f}",
                va="center",
                fontsize=self.theme.font.annotation_size,
                fontweight="bold",
            )

        # Apply theme
        self.theme.apply_to_axes(ax)

        # Add legend
        legend_elements = [
            Patch(facecolor="#440154", edgecolor="black", label="Low Similarity", alpha=0.8),
            Patch(facecolor="#fde725", edgecolor="black", label="High Similarity", alpha=0.8),
        ]
        if show_threshold:
            legend_elements.append(
                plt.Line2D(
                    [0],
                    [0],
                    color="#e74c3c",
                    linestyle="--",
                    label=f"Threshold ({threshold:.2f})",
                    linewidth=2,
                )
            )
        labels = ["Low", "High"]
        if show_threshold:
            labels.append(f"Threshold ({threshold:.2f})")
        self.theme.create_legend(ax, legend_elements, labels, loc="lower right")

        plt.tight_layout(pad=self.theme.figure.tight_layout_pad)
        return fig

    def plot_case_features(
        self, cases: List[Case], features: List[str], chart_type: str = "bar"
    ) -> Figure:
        """Plot case features comparison with enhanced styling.

        Args:
            cases: List of cases
            features: Feature names to plot
            chart_type: Chart type ("bar", "grouped")

        Returns:
            Matplotlib figure
        """
        if not cases or not features:
            raise ValueError("Need cases and features to visualize")

        n_features = len(features)
        fig, axes = self.create_figure(nrows=n_features, ncols=1)

        if n_features == 1:
            axes = [axes]

        case_ids = [case.case_id for case in cases]
        colors = self.theme.get_color_sequence(len(cases), "primary")

        for idx, feature in enumerate(features):
            ax = axes[idx]

            values = [case.features.get(feature, 0) for case in cases]

            bars = ax.bar(
                case_ids,
                values,
                color=colors,
                alpha=0.8,
                edgecolor="black",
                linewidth=0.8,
            )

            # Format axes
            ax.tick_params(axis="x", rotation=45, labelsize=self.theme.font.tick_size)
            self.format_axes_labels(ax, xlabel="Case ID", ylabel=feature)

            # Format title
            self.format_title(ax, f"Feature: {feature}")

            # Add value labels
            self.add_value_labels(ax, bars, format_str="{:.2f}")

            # Apply theme
            self.theme.apply_to_axes(ax)

        plt.tight_layout(pad=self.theme.figure.tight_layout_pad)
        return fig


class InferenceVisualizer(BaseChartVisualizer):
    """Visualizes inference results and model performance with enhanced styling."""

    def __init__(
        self,
        figure_size: Tuple[float, float] = (12, 8),
        dpi: int = 300,
        theme: Optional[VisualizationTheme] = None,
    ):
        """Initialize inference visualizer.

        Args:
            figure_size: Figure size
            dpi: DPI for figures
            theme: Visualization theme
        """
        super().__init__(figure_size, dpi, theme)

    def plot_inference_results(self, results: Dict[str, Any]) -> Figure:
        """Plot inference results using ModelVisualizer.

        Args:
            results: Inference results dictionary

        Returns:
            Matplotlib figure
        """
        visualizer = ModelVisualizer(self.figure_size, self.dpi, self.theme)
        return visualizer.visualize_inference_results(results)

    def plot_belief_evolution(
        self,
        belief_history: List[Dict[str, float]],
        show_confidence: bool = False,
    ) -> Figure:
        """Plot evolution of beliefs over time with enhanced styling.

        Args:
            belief_history: List of belief dictionaries over time
            show_confidence: Whether to show confidence intervals (if available)

        Returns:
            Matplotlib figure
        """
        if not belief_history:
            raise ValueError("No belief history to visualize")

        fig, ax = self.create_figure()

        # Get all states
        all_states = set()
        for beliefs in belief_history:
            all_states.update(beliefs.keys())

        all_states = sorted(list(all_states))
        time_steps = np.arange(len(belief_history))

        # Get colors for each state
        colors = self.theme.get_color_sequence(len(all_states), "primary")

        # Plot each state
        for state, color in zip(all_states, colors):
            values = [beliefs.get(state, 0.0) for beliefs in belief_history]
            ax.plot(
                time_steps,
                values,
                marker="o",
                label=state,
                linewidth=2.5,
                markersize=6,
                color=color,
                alpha=0.8,
                markerfacecolor=color,
                markeredgecolor="black",
                markeredgewidth=0.5,
            )

        # Format axes
        self.format_axes_labels(ax, xlabel="Time Step", ylabel="Belief Probability")
        self.theme.format_axis_percentage(ax, axis="y")

        # Format title
        self.format_title(ax, "Belief Evolution Over Time")

        # Apply theme
        self.theme.apply_to_axes(ax)

        # Add legend
        self.theme.create_legend(
            ax,
            [plt.Line2D([0], [0], color=c, linewidth=2.5, marker="o") for c in colors],
            all_states,
            loc="best",
            ncol=min(3, len(all_states)),
        )

        plt.tight_layout(pad=self.theme.figure.tight_layout_pad)
        return fig
