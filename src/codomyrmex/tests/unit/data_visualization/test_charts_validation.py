"""Unit tests for data_visualization/charts/ — ValueError on invalid/empty input.

All chart functions now raise ValueError instead of returning None for bad
input. Tests cover:
  - Empty data raises ValueError
  - Length mismatch raises ValueError
  - Valid data returns a matplotlib Figure

matplotlib is required; the module-level skipif guard skips the entire file
if it is not installed.
"""

import importlib.util
import os

import pytest

_matplotlib_available = importlib.util.find_spec("matplotlib") is not None

pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(
        not _matplotlib_available,
        reason="matplotlib not installed",
    ),
]

# Set non-interactive backend before any matplotlib import to prevent circular
# import issues that arise when charts/__init__.py re-enters during submodule loads.
os.environ.setdefault("MPLBACKEND", "Agg")

if _matplotlib_available:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Import all at module level so charts/__init__.py resolves the full import
    # graph once, cleanly — avoids circular import when tests import submodules
    # individually in different orders.
    from codomyrmex.data_visualization.charts.area_chart import create_area_chart
    from codomyrmex.data_visualization.charts.bar_chart import create_bar_chart
    from codomyrmex.data_visualization.charts.box_plot import create_box_plot
    from codomyrmex.data_visualization.charts.heatmap import create_heatmap
    from codomyrmex.data_visualization.charts.histogram import create_histogram
    from codomyrmex.data_visualization.charts.line_plot import create_line_plot
    from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart
    from codomyrmex.data_visualization.charts.scatter_plot import create_scatter_plot


# ---------------------------------------------------------------------------
# bar_chart
# ---------------------------------------------------------------------------


class TestBarChartValidation:
    """ValueError contract for create_bar_chart."""

    def test_empty_categories_raises(self):
        with pytest.raises(ValueError):
            create_bar_chart([], [1, 2, 3])

    def test_empty_values_raises(self):
        with pytest.raises(ValueError):
            create_bar_chart(["A", "B"], [])

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            create_bar_chart(["A", "B"], [1, 2, 3])

    def test_valid_data_returns_figure(self):
        fig = create_bar_chart(["A", "B", "C"], [1, 2, 3])
        assert isinstance(fig, plt.Figure)
        plt.close("all")

    def test_single_item_returns_figure(self):
        fig = create_bar_chart(["X"], [42])
        assert isinstance(fig, plt.Figure)
        plt.close("all")

    def test_horizontal_valid_returns_figure(self):
        fig = create_bar_chart(["A", "B"], [10, 20], horizontal=True)
        assert isinstance(fig, plt.Figure)
        plt.close("all")


# ---------------------------------------------------------------------------
# scatter_plot
# ---------------------------------------------------------------------------


class TestScatterPlotValidation:
    """ValueError contract for create_scatter_plot."""

    def test_empty_x_data_raises(self):
        with pytest.raises(ValueError):
            create_scatter_plot([], [1, 2])

    def test_empty_y_data_raises(self):
        with pytest.raises(ValueError):
            create_scatter_plot([1, 2], [])

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            create_scatter_plot([1, 2, 3], [4, 5])

    def test_valid_data_returns_figure(self):
        fig = create_scatter_plot([1, 2, 3], [4, 5, 6])
        assert isinstance(fig, plt.Figure)
        plt.close("all")

    def test_single_point_returns_figure(self):
        fig = create_scatter_plot([0], [0])
        assert isinstance(fig, plt.Figure)
        plt.close("all")


# ---------------------------------------------------------------------------
# area_chart
# ---------------------------------------------------------------------------


class TestAreaChartValidation:
    """ValueError contract for create_area_chart."""

    def test_empty_x_raises(self):
        with pytest.raises(ValueError):
            create_area_chart([], [1, 2, 3])

    def test_empty_y_raises(self):
        with pytest.raises(ValueError):
            create_area_chart([1, 2, 3], [])

    def test_valid_single_series_returns_figure(self):
        fig = create_area_chart([1, 2, 3], [4, 5, 6])
        assert isinstance(fig, plt.Figure)
        plt.close("all")

    def test_valid_multi_series_returns_figure(self):
        fig = create_area_chart([1, 2, 3], [[1, 2, 3], [3, 2, 1]])
        assert isinstance(fig, plt.Figure)
        plt.close("all")


# ---------------------------------------------------------------------------
# box_plot
# ---------------------------------------------------------------------------


class TestBoxPlotValidation:
    """ValueError contract for create_box_plot."""

    def test_empty_list_raises(self):
        with pytest.raises(ValueError):
            create_box_plot([])

    def test_empty_dict_raises(self):
        with pytest.raises(ValueError):
            create_box_plot({})

    def test_single_group_list_returns_figure(self):
        fig = create_box_plot([1, 2, 3, 4, 5])
        assert isinstance(fig, plt.Figure)
        plt.close("all")

    def test_dict_input_returns_figure(self):
        fig = create_box_plot({"A": [1, 2, 3], "B": [4, 5, 6]})
        assert isinstance(fig, plt.Figure)
        plt.close("all")

    def test_multi_group_list_returns_figure(self):
        fig = create_box_plot([[1, 2, 3], [4, 5, 6]])
        assert isinstance(fig, plt.Figure)
        plt.close("all")


# ---------------------------------------------------------------------------
# heatmap
# ---------------------------------------------------------------------------


class TestHeatmapValidation:
    """ValueError contract for create_heatmap."""

    def test_empty_list_raises(self):
        with pytest.raises(ValueError):
            create_heatmap([])

    def test_flat_list_raises(self):
        with pytest.raises(ValueError):
            create_heatmap([1, 2, 3])

    def test_none_raises(self):
        with pytest.raises(ValueError):
            create_heatmap(None)

    def test_valid_2d_data_returns_figure(self):
        fig = create_heatmap([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        assert isinstance(fig, plt.Figure)
        plt.close("all")

    def test_2x2_matrix_returns_figure(self):
        fig = create_heatmap([[0, 1], [1, 0]])
        assert isinstance(fig, plt.Figure)
        plt.close("all")


# ---------------------------------------------------------------------------
# histogram
# ---------------------------------------------------------------------------


class TestHistogramValidation:
    """ValueError contract for create_histogram."""

    def test_empty_data_raises(self):
        with pytest.raises(ValueError):
            create_histogram([])

    def test_valid_data_returns_figure(self):
        fig = create_histogram([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        assert isinstance(fig, plt.Figure)
        plt.close("all")

    def test_single_value_returns_figure(self):
        fig = create_histogram([42])
        assert isinstance(fig, plt.Figure)
        plt.close("all")

    def test_custom_bins_returns_figure(self):
        fig = create_histogram(list(range(100)), bins=20)
        assert isinstance(fig, plt.Figure)
        plt.close("all")


# ---------------------------------------------------------------------------
# line_plot
# ---------------------------------------------------------------------------


class TestLinePlotValidation:
    """ValueError contract for create_line_plot."""

    def test_empty_x_raises(self):
        with pytest.raises(ValueError):
            create_line_plot([], [1, 2, 3])

    def test_empty_y_raises(self):
        with pytest.raises(ValueError):
            create_line_plot([1, 2, 3], [])

    def test_valid_single_line_returns_figure(self):
        fig = create_line_plot([1, 2, 3], [4, 5, 6])
        assert isinstance(fig, plt.Figure)
        plt.close("all")

    def test_valid_multi_line_returns_figure(self):
        fig = create_line_plot([1, 2, 3], [[1, 2, 3], [3, 2, 1]])
        assert isinstance(fig, plt.Figure)
        plt.close("all")

    def test_single_line_length_mismatch_returns_none(self):
        result = create_line_plot([1, 2, 3], [4, 5])
        assert result is None


# ---------------------------------------------------------------------------
# pie_chart
# ---------------------------------------------------------------------------


class TestPieChartValidation:
    """ValueError contract for create_pie_chart."""

    def test_empty_labels_raises(self):
        with pytest.raises(ValueError):
            create_pie_chart([], [1, 2, 3])

    def test_empty_sizes_raises(self):
        with pytest.raises(ValueError):
            create_pie_chart(["A", "B"], [])

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            create_pie_chart(["A", "B", "C"], [10, 20])

    def test_valid_data_returns_figure(self):
        fig = create_pie_chart(["A", "B", "C"], [10, 30, 60])
        assert isinstance(fig, plt.Figure)
        plt.close("all")

    def test_single_slice_returns_figure(self):
        fig = create_pie_chart(["Only"], [100])
        assert isinstance(fig, plt.Figure)
        plt.close("all")

    def test_explode_mismatch_still_returns_figure(self):
        fig = create_pie_chart(["A", "B"], [50, 50], explode=[0.1])
        assert isinstance(fig, plt.Figure)
        plt.close("all")
