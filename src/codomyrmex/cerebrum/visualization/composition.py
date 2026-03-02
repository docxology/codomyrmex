from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch

from codomyrmex.cerebrum.core.exceptions import VisualizationError
from codomyrmex.cerebrum.visualization.base import (
    BaseChartVisualizer,
)
from codomyrmex.cerebrum.visualization.theme import (
    VisualizationTheme,
    get_default_theme,
)
from codomyrmex.logging_monitoring import get_logger

"""Composition visualizations: graphical abstracts and multi-panel compositions.


This module provides composite visualizations that combine multiple analyses
into summary dashboards, overview panels, and graphical abstracts suitable
for presentations and reports.
"""


try:

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    Figure = Any


logger = get_logger(__name__)


class CompositionVisualizer:
    """Creates composite visualizations combining multiple analyses."""

    def __init__(
        self,
        figure_size: tuple[float, float] = (20, 14),
        dpi: int = 300,
        theme: VisualizationTheme | None = None,
    ):
        """Initialize composition visualizer.

        Args:
            figure_size: Figure size (width, height)
            dpi: DPI for figures
            theme: Visualization theme
        """
        if not HAS_MATPLOTLIB:
            raise VisualizationError("matplotlib is required for visualization")

        self.figure_size = figure_size
        self.dpi = dpi
        self.theme = theme or get_default_theme()
        self.logger = get_logger(__name__)

    def create_analysis_overview_dashboard(
        self,
        analysis_summary: dict[str, Any],
        output_path: Path | None = None,
    ) -> Figure:
        """Create multi-panel dashboard summarizing all analyses.

        Args:
            analysis_summary: Dictionary containing summary statistics from all analyses
            output_path: Optional path to save figure

        Returns:
            Matplotlib figure
        """
        fig = plt.figure(figsize=self.figure_size, dpi=self.dpi)
        gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

        # Panel 1: Pattern Status Distribution (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        if "status_distribution" in analysis_summary:
            status_data = analysis_summary["status_distribution"]
            statuses = list(status_data.keys())
            counts = list(status_data.values())
            colors = [self.theme.get_status_color(s) for s in statuses]
            ax1.bar(statuses, counts, color=colors, alpha=0.8, edgecolor="black", linewidth=1.0)
            ax1.set_xlabel("Status", fontsize=self.theme.font.label_size)
            ax1.set_ylabel("Count", fontsize=self.theme.font.label_size)
            ax1.set_title("Pattern Status", fontsize=self.theme.font.label_size, fontweight="bold")
            self.theme.apply_to_axes(ax1)

        # Panel 2: Importance Distribution (top middle)
        ax2 = fig.add_subplot(gs[0, 1])
        if "importance_distribution" in analysis_summary:
            importance_data = analysis_summary["importance_distribution"]
            levels = list(importance_data.keys())
            counts = list(importance_data.values())
            colors = [self.theme.get_importance_color(l) for l in levels]
            ax2.bar(levels, counts, color=colors, alpha=0.8, edgecolor="black", linewidth=1.0)
            ax2.set_xlabel("Importance", fontsize=self.theme.font.label_size)
            ax2.set_ylabel("Count", fontsize=self.theme.font.label_size)
            ax2.set_title("Importance Distribution", fontsize=self.theme.font.label_size, fontweight="bold")
            self.theme.apply_to_axes(ax2)

        # Panel 3: Analysis Method Summary (top right)
        ax3 = fig.add_subplot(gs[0, 2])
        if "method_summary" in analysis_summary:
            method_data = analysis_summary["method_summary"]
            methods = list(method_data.keys())
            scores = list(method_data.values())
            colors = self.theme.get_color_sequence(len(methods), "primary")
            ax3.barh(methods, scores, color=colors, alpha=0.8, edgecolor="black", linewidth=1.0)
            ax3.set_xlabel("Score", fontsize=self.theme.font.label_size)
            ax3.set_title("Method Performance", fontsize=self.theme.font.label_size, fontweight="bold")
            self.theme.apply_to_axes(ax3)

        # Panel 4: Network Overview (middle, spanning 2 columns)
        ax4 = fig.add_subplot(gs[1, :2])
        if "network_summary" in analysis_summary:
            network_data = analysis_summary["network_summary"]
            ax4.text(
                0.5,
                0.5,
                f"Network: {network_data.get('nodes', 0)} nodes, {network_data.get('edges', 0)} edges",
                ha="center",
                va="center",
                fontsize=self.theme.font.title_size,
                fontweight="bold",
                transform=ax4.transAxes,
            )
            ax4.axis("off")
            ax4.set_title("Network Overview", fontsize=self.theme.font.label_size, fontweight="bold")

        # Panel 5: Key Metrics (middle right)
        ax5 = fig.add_subplot(gs[1, 2])
        if "key_metrics" in analysis_summary:
            metrics = analysis_summary["key_metrics"]
            metric_names = list(metrics.keys())[:5]  # Top 5
            metric_values = [metrics[m] for m in metric_names]
            colors = self.theme.get_color_sequence(len(metric_names), "accent")
            ax5.barh(metric_names, metric_values, color=colors, alpha=0.8, edgecolor="black", linewidth=1.0)
            ax5.set_xlabel("Value", fontsize=self.theme.font.label_size)
            ax5.set_title("Key Metrics", fontsize=self.theme.font.label_size, fontweight="bold")
            self.theme.apply_to_axes(ax5)

        # Panel 6: Pattern Distribution by Part (bottom left)
        ax6 = fig.add_subplot(gs[2, 0])
        if "part_distribution" in analysis_summary:
            part_data = analysis_summary["part_distribution"]
            parts = list(part_data.keys())[:8]  # Top 8
            counts = [part_data[p] for p in parts]
            colors = self.theme.get_color_sequence(len(parts), "secondary")
            ax6.bar(parts, counts, color=colors, alpha=0.8, edgecolor="black", linewidth=1.0)
            ax6.set_xlabel("Part", fontsize=self.theme.font.label_size)
            ax6.set_ylabel("Count", fontsize=self.theme.font.label_size)
            ax6.set_title("Patterns by Part", fontsize=self.theme.font.label_size, fontweight="bold")
            ax6.tick_params(axis="x", rotation=45)
            self.theme.apply_to_axes(ax6)

        # Panel 7: Similarity Distribution (bottom middle)
        ax7 = fig.add_subplot(gs[2, 1])
        if "similarity_distribution" in analysis_summary:
            sim_data = analysis_summary["similarity_distribution"]
            bins = np.linspace(0, 1, 20)
            ax7.hist(sim_data, bins=bins, color=self.theme.colors.primary[0], alpha=0.7, edgecolor="black")
            ax7.set_xlabel("Similarity Score", fontsize=self.theme.font.label_size)
            ax7.set_ylabel("Frequency", fontsize=self.theme.font.label_size)
            ax7.set_title("Similarity Distribution", fontsize=self.theme.font.label_size, fontweight="bold")
            self.theme.apply_to_axes(ax7)

        # Panel 8: Analysis Coverage (bottom right)
        ax8 = fig.add_subplot(gs[2, 2])
        if "coverage" in analysis_summary:
            coverage_data = analysis_summary["coverage"]
            categories = list(coverage_data.keys())
            values = list(coverage_data.values())
            colors = self.theme.get_color_sequence(len(categories), "primary")
            ax8.pie(values, labels=categories, autopct="%1.1f%%", colors=colors, startangle=90)
            ax8.set_title("Analysis Coverage", fontsize=self.theme.font.label_size, fontweight="bold")

        # Overall title
        fig.suptitle(
            "CEREBRUM-FPF Analysis Overview Dashboard",
            fontsize=self.theme.font.title_size + 2,
            fontweight="bold",
            y=0.995,
        )

        if output_path:
            fig.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
            plt.close(fig)
            self.logger.info(f"Saved dashboard to {output_path}")
        else:
            plt.tight_layout(pad=self.theme.figure.tight_layout_pad)
            return fig

    def create_pattern_landscape_map(
        self,
        pattern_embeddings: dict[str, tuple[float, float]],
        pattern_metadata: dict[str, dict[str, Any]] | None = None,
        output_path: Path | None = None,
    ) -> Figure:
        """Create 2D embedding map of patterns with annotations.

        Args:
            pattern_embeddings: Dictionary mapping pattern IDs to (x, y) coordinates
            pattern_metadata: Optional metadata for patterns (status, importance, etc.)
            output_path: Optional path to save figure

        Returns:
            Matplotlib figure
        """
        if not pattern_embeddings:
            raise ValueError("No pattern embeddings provided")

        chart_viz = BaseChartVisualizer(self.figure_size, self.dpi, self.theme)
        fig, ax = chart_viz.create_figure()

        pattern_ids = list(pattern_embeddings.keys())
        x_coords = [pattern_embeddings[pid][0] for pid in pattern_ids]
        y_coords = [pattern_embeddings[pid][1] for pid in pattern_ids]

        # Color by status if available
        if pattern_metadata:
            colors = [
                self.theme.get_status_color(pattern_metadata.get(pid, {}).get("status", "Stub"))
                for pid in pattern_ids
            ]
            sizes = [
                100 + (pattern_metadata.get(pid, {}).get("importance", 0.5) * 400)
                for pid in pattern_ids
            ]
        else:
            colors = self.theme.get_color_sequence(len(pattern_ids), "primary")
            sizes = [200] * len(pattern_ids)

        # Scatter plot
        ax.scatter(
            x_coords,
            y_coords,
            c=colors,
            s=sizes,
            alpha=0.7,
            edgecolors="black",
            linewidths=1.0,
        )

        # Annotate important patterns
        if pattern_metadata:
            important_patterns = [
                pid
                for pid in pattern_ids
                if pattern_metadata.get(pid, {}).get("importance", 0) > 0.7
            ]
            for pid in important_patterns[:10]:  # Top 10
                idx = pattern_ids.index(pid)
                ax.annotate(
                    pid,
                    (x_coords[idx], y_coords[idx]),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=self.theme.font.annotation_size,
                    fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                )

        chart_viz.format_axes_labels(ax, xlabel="Dimension 1", ylabel="Dimension 2")
        chart_viz.format_title(ax, "Pattern Landscape Map")

        # Add legend for status
        if pattern_metadata:
            statuses = ["Stable", "Draft", "Stub", "New"]
            legend_elements = [
                Patch(facecolor=self.theme.get_status_color(s), edgecolor="black", label=s, alpha=0.7)
                for s in statuses
            ]
            self.theme.create_legend(ax, legend_elements, statuses, loc="upper right")

        self.theme.apply_to_axes(ax)

        if output_path:
            chart_viz.save_figure(fig, str(output_path))
        else:
            plt.tight_layout(pad=self.theme.figure.tight_layout_pad)
            return fig

    def create_cross_analysis_summary(
        self,
        analysis_results: dict[str, dict[str, Any]],
        output_path: Path | None = None,
    ) -> Figure:
        """Create side-by-side comparison panels for different analyses.

        Args:
            analysis_results: Dictionary mapping analysis names to results
            output_path: Optional path to save figure

        Returns:
            Matplotlib figure
        """
        n_analyses = len(analysis_results)
        if n_analyses == 0:
            raise ValueError("No analysis results provided")

        chart_viz = BaseChartVisualizer(self.figure_size, self.dpi, self.theme)
        fig, axes = chart_viz.create_figure(nrows=1, ncols=n_analyses)

        if n_analyses == 1:
            axes = [axes]

        list(analysis_results.keys())
        colors = self.theme.get_color_sequence(n_analyses, "primary")

        for idx, (analysis_name, results) in enumerate(analysis_results.items()):
            ax = axes[idx]

            # Create summary visualization based on results type
            if isinstance(results, dict):
                # Bar chart of top items
                items = sorted(results.items(), key=lambda x: x[1], reverse=True)[:10]
                labels = [item[0] for item in items]
                values = [item[1] for item in items]

                ax.barh(labels, values, color=colors[idx], alpha=0.8, edgecolor="black", linewidth=1.0)
                ax.set_xlabel("Score", fontsize=self.theme.font.label_size)
                ax.set_title(analysis_name, fontsize=self.theme.font.label_size, fontweight="bold")
            else:
                # Text summary
                ax.text(
                    0.5,
                    0.5,
                    str(results)[:200],
                    ha="center",
                    va="center",
                    fontsize=self.theme.font.label_size,
                    transform=ax.transAxes,
                    wrap=True,
                )
                ax.set_title(analysis_name, fontsize=self.theme.font.label_size, fontweight="bold")
                ax.axis("off")

            self.theme.apply_to_axes(ax)

        fig.suptitle(
            "Cross-Analysis Summary",
            fontsize=self.theme.font.title_size,
            fontweight="bold",
            y=0.995,
        )

        if output_path:
            chart_viz.save_figure(fig, str(output_path))
        else:
            plt.tight_layout(pad=self.theme.figure.tight_layout_pad)
            return fig

