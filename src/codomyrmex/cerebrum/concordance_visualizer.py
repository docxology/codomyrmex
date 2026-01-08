from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from codomyrmex.cerebrum.exceptions import VisualizationError
from codomyrmex.cerebrum.visualization_base import BaseChartVisualizer, BaseHeatmapVisualizer
from codomyrmex.cerebrum.visualization_theme import VisualizationTheme, get_default_theme
from codomyrmex.logging_monitoring import get_logger






"""Concordance visualizations for cross-analysis comparisons.

This module provides visualizations that compare results from different
CEREBRUM analyses (CBR, Bayesian, Active Inference) and FPF analyses,
showing agreement, correlation, and concordance patterns.
"""


try:

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    Figure = Any


logger = get_logger(__name__)


class ConcordanceVisualizer:
    """Visualizes concordance between different analysis methods."""

    def __init__(
        self,
        figure_size: Tuple[float, float] = (14, 10),
        dpi: int = 300,
        theme: Optional[VisualizationTheme] = None,
    ):
        """Initialize concordance visualizer.

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

    def plot_analysis_concordance_matrix(
        self,
        cbr_results: Dict[str, float],
        bayesian_results: Dict[str, float],
        active_inference_results: Optional[Dict[str, float]] = None,
        pattern_ids: Optional[List[str]] = None,
    ) -> Figure:
        """Plot concordance matrix comparing different analysis methods.

        Args:
            cbr_results: Case-based reasoning results (pattern_id -> score)
            bayesian_results: Bayesian inference results (pattern_id -> score)
            active_inference_results: Optional active inference results
            pattern_ids: Optional list of pattern IDs to include

        Returns:
            Matplotlib figure
        """
        # Get common pattern IDs
        if pattern_ids is None:
            pattern_ids = sorted(set(cbr_results.keys()) & set(bayesian_results.keys()))
            if active_inference_results:
                pattern_ids = sorted(set(pattern_ids) & set(active_inference_results.keys()))

        if not pattern_ids:
            raise ValueError("No common patterns found for concordance analysis")

        # Normalize scores to [0, 1]
        def normalize(scores: Dict[str, float]) -> Dict[str, float]:
            if not scores:
                return {}
            min_val = min(scores.values())
            max_val = max(scores.values())
            if max_val == min_val:
                return {k: 0.5 for k in scores}
            return {k: (v - min_val) / (max_val - min_val) for k, v in scores.items()}

        cbr_norm = normalize({pid: cbr_results.get(pid, 0.0) for pid in pattern_ids})
        bayesian_norm = normalize({pid: bayesian_results.get(pid, 0.0) for pid in pattern_ids})

        # Create correlation matrix
        methods = ["CBR", "Bayesian"]
        if active_inference_results:
            ai_norm = normalize({pid: active_inference_results.get(pid, 0.0) for pid in pattern_ids})
            methods.append("Active Inference")

        n_methods = len(methods)
        correlation_matrix = np.zeros((n_methods, n_methods))

        # Calculate correlations
        cbr_vals = np.array([cbr_norm.get(pid, 0.0) for pid in pattern_ids])
        bayesian_vals = np.array([bayesian_norm.get(pid, 0.0) for pid in pattern_ids])

        correlation_matrix[0, 0] = 1.0
        correlation_matrix[1, 1] = 1.0
        correlation_matrix[0, 1] = np.corrcoef(cbr_vals, bayesian_vals)[0, 1]
        correlation_matrix[1, 0] = correlation_matrix[0, 1]

        if active_inference_results:
            ai_vals = np.array([ai_norm.get(pid, 0.0) for pid in pattern_ids])
            correlation_matrix[2, 2] = 1.0
            correlation_matrix[0, 2] = np.corrcoef(cbr_vals, ai_vals)[0, 1]
            correlation_matrix[2, 0] = correlation_matrix[0, 2]
            correlation_matrix[1, 2] = np.corrcoef(bayesian_vals, ai_vals)[0, 1]
            correlation_matrix[2, 1] = correlation_matrix[1, 2]

        # Create heatmap
        heatmap_viz = BaseHeatmapVisualizer(self.figure_size, self.dpi, self.theme)
        fig, ax = heatmap_viz.create_heatmap(
            correlation_matrix,
            methods,
            methods,
            colormap="coolwarm",
        )

        # Format title
        heatmap_viz.format_title(ax, "Analysis Method Concordance Matrix")

        # Update colorbar
        im = ax.images[0]
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label(
            "Correlation Coefficient",
            fontsize=self.theme.font.label_size,
            fontweight=self.theme.font.weight_label,
        )
        cbar.ax.tick_params(labelsize=self.theme.font.tick_size)

        # Add correlation values as text
        for i in range(n_methods):
            for j in range(n_methods):
                text = ax.text(
                    j,
                    i,
                    f"{correlation_matrix[i, j]:.2f}",
                    ha="center",
                    va="center",
                    color="white" if abs(correlation_matrix[i, j]) > 0.5 else "black",
                    fontsize=self.theme.font.label_size,
                    fontweight="bold",
                )

        # Apply theme
        self.theme.apply_to_axes(ax)

        plt.tight_layout(pad=self.theme.figure.tight_layout_pad)
        return fig

    def plot_pattern_importance_concordance(
        self,
        importance_metrics: Dict[str, Dict[str, float]],
        pattern_ids: Optional[List[str]] = None,
    ) -> Figure:
        """Plot concordance of different importance metrics.

        Args:
            importance_metrics: Dictionary mapping metric names to pattern scores
            pattern_ids: Optional list of pattern IDs to include

        Returns:
            Matplotlib figure
        """
        if not importance_metrics:
            raise ValueError("No importance metrics provided")

        # Get common pattern IDs
        if pattern_ids is None:
            pattern_ids = sorted(set.intersection(*[set(metrics.keys()) for metrics in importance_metrics.values()]))

        if not pattern_ids:
            raise ValueError("No common patterns found")

        # Create scatter plot matrix
        metric_names = list(importance_metrics.keys())
        n_metrics = len(metric_names)

        if n_metrics < 2:
            raise ValueError("Need at least 2 metrics for concordance analysis")

        # Create subplot grid
        chart_viz = BaseChartVisualizer(self.figure_size, self.dpi, self.theme)
        fig, axes = chart_viz.create_figure(nrows=n_metrics, ncols=n_metrics)

        if n_metrics == 1:
            axes = np.array([[axes]])
        axes = axes.flatten().reshape(n_metrics, n_metrics)

        for i, metric1 in enumerate(metric_names):
            for j, metric2 in enumerate(metric_names):
                ax = axes[i, j]

                if i == j:
                    # Diagonal: show distribution
                    values = [importance_metrics[metric1].get(pid, 0.0) for pid in pattern_ids]
                    ax.hist(values, bins=20, color=self.theme.colors.primary[0], alpha=0.7, edgecolor="black")
                    chart_viz.format_axes_labels(ax, xlabel=metric1, ylabel="Frequency")
                else:
                    # Off-diagonal: scatter plot
                    x_vals = [importance_metrics[metric1].get(pid, 0.0) for pid in pattern_ids]
                    y_vals = [importance_metrics[metric2].get(pid, 0.0) for pid in pattern_ids]

                    ax.scatter(
                        x_vals,
                        y_vals,
                        alpha=0.6,
                        s=30,
                        color=self.theme.colors.primary[0],
                        edgecolors="black",
                        linewidths=0.5,
                    )

                    # Add correlation coefficient
                    corr = np.corrcoef(x_vals, y_vals)[0, 1]
                    ax.text(
                        0.05,
                        0.95,
                        f"r = {corr:.2f}",
                        transform=ax.transAxes,
                        fontsize=self.theme.font.annotation_size,
                        fontweight="bold",
                        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
                    )

                    chart_viz.format_axes_labels(ax, xlabel=metric1, ylabel=metric2)

                # Apply theme
                self.theme.apply_to_axes(ax)

        # Format overall title
        fig.suptitle("Pattern Importance Metric Concordance", fontsize=self.theme.font.title_size, fontweight="bold", y=0.995)

        plt.tight_layout(pad=self.theme.figure.tight_layout_pad)
        return fig

    def plot_agreement_heatmap(
        self,
        analysis_results: Dict[str, Dict[str, Any]],
        pattern_ids: List[str],
        agreement_threshold: float = 0.7,
    ) -> Figure:
        """Plot heatmap showing agreement/disagreement between analyses.

        Args:
            analysis_results: Dictionary mapping analysis names to results
            pattern_ids: List of pattern IDs
            agreement_threshold: Threshold for considering results in agreement

        Returns:
            Matplotlib figure
        """
        # Calculate agreement matrix
        n_patterns = len(pattern_ids)
        n_analyses = len(analysis_results)

        # Normalize all results to [0, 1]
        normalized_results = {}
        for analysis_name, results in analysis_results.items():
            if isinstance(results, dict):
                values = list(results.values())
                if values:
                    min_val = min(values)
                    max_val = max(values)
                    if max_val == min_val:
                        normalized_results[analysis_name] = {pid: 0.5 for pid in pattern_ids}
                    else:
                        normalized_results[analysis_name] = {
                            pid: (results.get(pid, 0.0) - min_val) / (max_val - min_val)
                            for pid in pattern_ids
                        }
                else:
                    normalized_results[analysis_name] = {pid: 0.0 for pid in pattern_ids}
            else:
                normalized_results[analysis_name] = {pid: 0.0 for pid in pattern_ids}

        # Calculate agreement scores (1 = agreement, 0 = disagreement)
        agreement_matrix = np.zeros((n_patterns, n_analyses))
        analysis_names = list(analysis_results.keys())

        for i, pid in enumerate(pattern_ids):
            values = [normalized_results[an].get(pid, 0.0) for an in analysis_names]
            # Agreement: low variance means high agreement
            if len(values) > 1:
                variance = np.var(values)
                agreement = 1.0 - min(1.0, variance * 2)  # Scale variance
            else:
                agreement = 1.0
            agreement_matrix[i, :] = agreement

        # Create heatmap
        heatmap_viz = BaseHeatmapVisualizer(self.figure_size, self.dpi, self.theme)
        fig, ax = heatmap_viz.create_heatmap(
            agreement_matrix,
            pattern_ids,
            analysis_names,
            colormap="RdYlGn",
        )

        # Format title
        heatmap_viz.format_title(ax, f"Analysis Agreement Heatmap (threshold: {agreement_threshold:.2f})")

        # Update colorbar
        im = ax.images[0]
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label(
            "Agreement Score",
            fontsize=self.theme.font.label_size,
            fontweight=self.theme.font.weight_label,
        )
        cbar.ax.tick_params(labelsize=self.theme.font.tick_size)

        # Rotate x-axis labels
        ax.set_xticklabels(analysis_names, rotation=45, ha="right")

        # Apply theme
        self.theme.apply_to_axes(ax)

        plt.tight_layout(pad=self.theme.figure.tight_layout_pad)
        return fig



