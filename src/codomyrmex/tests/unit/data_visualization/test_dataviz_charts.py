"""Unit tests for standard chart types -- bar, line, scatter, histogram, pie, heatmap, box plot, and area charts."""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pytest

# Use non-interactive backend for testing
matplotlib.use('Agg')


# ============================================================================
# TestBarChart
# ============================================================================
@pytest.mark.unit
class TestBarChart:
    """Test bar chart generation."""

    def test_basic_bar_chart(self, tmp_path):
        """Test functionality: basic bar chart."""
        from codomyrmex.data_visualization.charts.bar_chart import create_bar_chart
        output = str(tmp_path / "bar.png")
        fig = create_bar_chart(['A', 'B', 'C'], [1, 2, 3], output_path=output)
        assert isinstance(fig, plt.Figure)
        assert Path(output).exists()

    def test_horizontal_bar_chart(self, tmp_path):
        """Test functionality: horizontal bar chart."""
        from codomyrmex.data_visualization.charts.bar_chart import create_bar_chart
        output = str(tmp_path / "bar_h.png")
        fig = create_bar_chart(['A', 'B'], [10, 20], horizontal=True, output_path=output)
        assert isinstance(fig, plt.Figure)
        assert Path(output).exists()

    def test_empty_data_returns_none(self):
        """Test functionality: empty data returns none."""
        from codomyrmex.data_visualization.charts.bar_chart import create_bar_chart
        assert create_bar_chart([], [1, 2]) is None
        assert create_bar_chart(['A'], []) is None

    def test_mismatched_lengths_returns_none(self):
        """Test functionality: mismatched lengths returns none."""
        from codomyrmex.data_visualization.charts.bar_chart import create_bar_chart
        assert create_bar_chart(['A', 'B'], [1, 2, 3]) is None

    def test_bar_chart_with_theme(self, tmp_path):
        """Test functionality: bar chart with theme."""
        from codomyrmex.data_visualization.charts.bar_chart import create_bar_chart
        output = str(tmp_path / "bar_theme.png")
        fig = create_bar_chart(['X', 'Y'], [5, 10], theme="dark", output_path=output)
        assert isinstance(fig, plt.Figure)

    def test_bar_chart_class(self, tmp_path):
        """Test functionality: bar chart class."""
        from codomyrmex.data_visualization.charts.bar_chart import BarChart
        chart = BarChart(categories=['A', 'B'], values=[1, 2], title="OO Bar")
        output = str(tmp_path / "bar_oo.png")
        chart.save(output)
        assert Path(output).exists()


# ============================================================================
# TestLinePlot
# ============================================================================
@pytest.mark.unit
class TestLinePlot:
    """Test line plot generation."""

    def test_basic_line_plot(self, tmp_path):
        """Test functionality: basic line plot."""
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        output = str(tmp_path / "line.png")
        fig = create_line_plot([1, 2, 3], [4, 5, 6], output_path=output)
        assert isinstance(fig, plt.Figure)
        assert Path(output).exists()

    def test_multiple_lines(self, tmp_path):
        """Test functionality: multiple lines."""
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        output = str(tmp_path / "multi_line.png")
        fig = create_line_plot(
            [1, 2, 3],
            [[1, 2, 3], [3, 2, 1]],
            line_labels=["Up", "Down"],
            output_path=output,
        )
        assert isinstance(fig, plt.Figure)
        assert Path(output).exists()

    def test_empty_data_returns_none(self):
        """Test functionality: empty data returns none."""
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        assert create_line_plot([], []) is None

    def test_with_markers(self, tmp_path):
        """Test functionality: with markers."""
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        output = str(tmp_path / "markers.png")
        fig = create_line_plot([1, 2, 3], [1, 4, 9], markers=True, output_path=output)
        assert isinstance(fig, plt.Figure)

    def test_line_plot_with_theme(self, tmp_path):
        """Test functionality: line plot with theme."""
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        fig = create_line_plot([1, 2, 3], [2, 4, 6], theme="light")
        assert isinstance(fig, plt.Figure)

    def test_line_plot_class(self, tmp_path):
        """Test functionality: line plot class."""
        from codomyrmex.data_visualization.charts.line_plot import LinePlot
        chart = LinePlot(x_data=[1, 2, 3], y_data=[3, 2, 1], title="OO Line")
        output = str(tmp_path / "line_oo.png")
        chart.save(output)
        assert Path(output).exists()


# ============================================================================
# TestScatterPlot
# ============================================================================
@pytest.mark.unit
class TestScatterPlot:
    """Test scatter plot generation."""

    def test_basic_scatter_plot(self, tmp_path):
        """Test functionality: basic scatter plot."""
        from codomyrmex.data_visualization.charts.scatter_plot import (
            create_scatter_plot,
        )
        output = str(tmp_path / "scatter.png")
        fig = create_scatter_plot([1, 2, 3], [4, 5, 6], output_path=output)
        assert isinstance(fig, plt.Figure)
        assert Path(output).exists()

    def test_empty_data_returns_none(self):
        """Test functionality: empty data returns none."""
        from codomyrmex.data_visualization.charts.scatter_plot import (
            create_scatter_plot,
        )
        assert create_scatter_plot([], []) is None

    def test_mismatched_data_returns_none(self):
        """Test functionality: mismatched data returns none."""
        from codomyrmex.data_visualization.charts.scatter_plot import (
            create_scatter_plot,
        )
        assert create_scatter_plot([1, 2], [1, 2, 3]) is None

    def test_custom_styling(self, tmp_path):
        """Test functionality: custom styling."""
        from codomyrmex.data_visualization.charts.scatter_plot import (
            create_scatter_plot,
        )
        output = str(tmp_path / "scatter_styled.png")
        fig = create_scatter_plot(
            [1, 2, 3, 4], [2, 4, 6, 8],
            dot_size=50, dot_color="red", alpha=0.5,
            output_path=output,
        )
        assert isinstance(fig, plt.Figure)

    def test_scatter_with_theme(self, tmp_path):
        """Test functionality: scatter with theme."""
        from codomyrmex.data_visualization.charts.scatter_plot import (
            create_scatter_plot,
        )
        fig = create_scatter_plot([1, 2, 3], [3, 2, 1], theme="vibrant")
        assert isinstance(fig, plt.Figure)

    def test_scatter_plot_class(self, tmp_path):
        """Test functionality: scatter plot class."""
        from codomyrmex.data_visualization.charts.scatter_plot import ScatterPlot
        chart = ScatterPlot(x_data=[1, 2, 3], y_data=[3, 2, 1])
        output = str(tmp_path / "scatter_oo.png")
        chart.save(output)
        assert Path(output).exists()


# ============================================================================
# TestHistogram
# ============================================================================
@pytest.mark.unit
class TestHistogram:
    """Test histogram generation."""

    def test_basic_histogram(self, tmp_path):
        """Test functionality: basic histogram."""
        from codomyrmex.data_visualization.charts.histogram import create_histogram
        output = str(tmp_path / "hist.png")
        fig = create_histogram([1, 2, 2, 3, 3, 3, 4, 5], output_path=output)
        assert isinstance(fig, plt.Figure)
        assert Path(output).exists()

    def test_empty_data_returns_none(self):
        """Test functionality: empty data returns none."""
        from codomyrmex.data_visualization.charts.histogram import create_histogram
        assert create_histogram([]) is None

    def test_custom_bins(self, tmp_path):
        """Test functionality: custom bins."""
        from codomyrmex.data_visualization.charts.histogram import create_histogram
        output = str(tmp_path / "hist_bins.png")
        fig = create_histogram(list(range(50)), bins=5, output_path=output)
        assert isinstance(fig, plt.Figure)

    def test_histogram_with_theme(self, tmp_path):
        """Test functionality: histogram with theme."""
        from codomyrmex.data_visualization.charts.histogram import create_histogram
        fig = create_histogram([1, 2, 3, 4, 5], theme="minimal")
        assert isinstance(fig, plt.Figure)

    def test_histogram_class(self, tmp_path):
        """Test functionality: histogram class."""
        from codomyrmex.data_visualization.charts.histogram import Histogram
        chart = Histogram(data=[1, 2, 3, 4, 5], bins=3)
        output = str(tmp_path / "hist_oo.png")
        chart.save(output)
        assert Path(output).exists()


# ============================================================================
# TestPieChart
# ============================================================================
@pytest.mark.unit
class TestPieChart:
    """Test pie chart generation."""

    def test_basic_pie_chart(self, tmp_path):
        """Test functionality: basic pie chart."""
        from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart
        output = str(tmp_path / "pie.png")
        fig = create_pie_chart(['A', 'B', 'C'], [10, 20, 30], output_path=output)
        assert isinstance(fig, plt.Figure)
        assert Path(output).exists()

    def test_pie_with_explode(self, tmp_path):
        """Test functionality: pie with explode."""
        from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart
        output = str(tmp_path / "pie_explode.png")
        fig = create_pie_chart(
            ['A', 'B', 'C'], [10, 20, 30],
            explode=[0, 0.1, 0],
            output_path=output,
        )
        assert isinstance(fig, plt.Figure)

    def test_empty_data_returns_none(self):
        """Test functionality: empty data returns none."""
        from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart
        assert create_pie_chart([], []) is None

    def test_mismatched_explode_ignored(self, tmp_path):
        """Test functionality: mismatched explode ignored."""
        from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart
        output = str(tmp_path / "pie_mismatch.png")
        fig = create_pie_chart(
            ['A', 'B'], [10, 20],
            explode=[0, 0.1, 0],
            output_path=output,
        )
        assert isinstance(fig, plt.Figure)

    def test_pie_with_theme(self, tmp_path):
        """Test functionality: pie with theme."""
        from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart
        fig = create_pie_chart(['X', 'Y'], [40, 60], theme="scientific")
        assert isinstance(fig, plt.Figure)

    def test_pie_chart_class(self, tmp_path):
        """Test functionality: pie chart class."""
        from codomyrmex.data_visualization.charts.pie_chart import PieChart
        chart = PieChart(labels=['A', 'B'], sizes=[50, 50])
        output = str(tmp_path / "pie_oo.png")
        chart.save(output)
        assert Path(output).exists()


# ============================================================================
# TestHeatmap
# ============================================================================
@pytest.mark.unit
class TestHeatmap:
    """Test heatmap generation."""

    def test_basic_heatmap(self, tmp_path):
        """Test functionality: basic heatmap."""
        from codomyrmex.data_visualization.charts.heatmap import create_heatmap
        output = str(tmp_path / "heatmap.png")
        fig = create_heatmap([[1, 2], [3, 4]], output_path=output)
        assert isinstance(fig, plt.Figure)
        assert Path(output).exists()

    def test_heatmap_with_labels(self, tmp_path):
        """Test functionality: heatmap with labels."""
        from codomyrmex.data_visualization.charts.heatmap import create_heatmap
        output = str(tmp_path / "heatmap_labels.png")
        fig = create_heatmap(
            [[1, 2, 3], [4, 5, 6]],
            x_labels=['A', 'B', 'C'],
            y_labels=['Row1', 'Row2'],
            output_path=output,
        )
        assert isinstance(fig, plt.Figure)

    def test_heatmap_with_annotations(self, tmp_path):
        """Test functionality: heatmap with annotations."""
        from codomyrmex.data_visualization.charts.heatmap import create_heatmap
        output = str(tmp_path / "heatmap_annot.png")
        fig = create_heatmap([[1, 2], [3, 4]], annot=True, output_path=output)
        assert isinstance(fig, plt.Figure)

    def test_heatmap_invalid_data_returns_none(self):
        """Test functionality: heatmap invalid data returns none."""
        from codomyrmex.data_visualization.charts.heatmap import create_heatmap
        assert create_heatmap(None) is None
        assert create_heatmap([]) is None
        assert create_heatmap("not a list") is None

    def test_heatmap_with_theme(self, tmp_path):
        """Test functionality: heatmap with theme."""
        from codomyrmex.data_visualization.charts.heatmap import create_heatmap
        fig = create_heatmap([[1, 2], [3, 4]], theme="dark")
        assert isinstance(fig, plt.Figure)

    def test_heatmap_class(self, tmp_path):
        """Test functionality: heatmap class."""
        from codomyrmex.data_visualization.charts.heatmap import Heatmap
        chart = Heatmap(data=[[1, 2], [3, 4]], title="OO Heatmap")
        output = str(tmp_path / "heatmap_oo.png")
        chart.save(output)
        assert Path(output).exists()


# ============================================================================
# TestBoxPlot
# ============================================================================
@pytest.mark.unit
class TestBoxPlot:
    """Test box plot generation."""

    def test_basic_box_plot(self, tmp_path):
        """Test functionality: basic box plot."""
        from codomyrmex.data_visualization.charts.box_plot import create_box_plot
        output = str(tmp_path / "box.png")
        fig = create_box_plot([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], output_path=output)
        assert isinstance(fig, plt.Figure)
        assert Path(output).exists()

    def test_box_plot_with_dict_data(self, tmp_path):
        """Test functionality: box plot with dict data."""
        from codomyrmex.data_visualization.charts.box_plot import create_box_plot
        output = str(tmp_path / "box_dict.png")
        fig = create_box_plot(
            {"Group A": [1, 2, 3, 4, 5], "Group B": [3, 4, 5, 6, 7]},
            output_path=output,
        )
        assert isinstance(fig, plt.Figure)

    def test_box_plot_multiple_lists(self, tmp_path):
        """Test functionality: box plot multiple lists."""
        from codomyrmex.data_visualization.charts.box_plot import create_box_plot
        output = str(tmp_path / "box_multi.png")
        fig = create_box_plot(
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            labels=["Low", "Mid", "High"],
            output_path=output,
        )
        assert isinstance(fig, plt.Figure)

    def test_box_plot_empty_returns_none(self):
        """Test functionality: box plot empty returns none."""
        from codomyrmex.data_visualization.charts.box_plot import create_box_plot
        assert create_box_plot([]) is None
        assert create_box_plot(None) is None

    def test_box_plot_class(self, tmp_path):
        """Test functionality: box plot class."""
        from codomyrmex.data_visualization.charts.box_plot import BoxPlot
        chart = BoxPlot(data={"A": [1, 2, 3], "B": [4, 5, 6]}, title="OO Box")
        output = str(tmp_path / "box_oo.png")
        chart.save(output)
        assert Path(output).exists()


# ============================================================================
# TestAreaChart
# ============================================================================
@pytest.mark.unit
class TestAreaChart:
    """Test area chart generation."""

    def test_basic_area_chart(self, tmp_path):
        """Test functionality: basic area chart."""
        from codomyrmex.data_visualization.charts.area_chart import create_area_chart
        output = str(tmp_path / "area.png")
        fig = create_area_chart([1, 2, 3, 4, 5], [2, 4, 3, 5, 4], output_path=output)
        assert isinstance(fig, plt.Figure)
        assert Path(output).exists()

    def test_stacked_area_chart(self, tmp_path):
        """Test functionality: stacked area chart."""
        from codomyrmex.data_visualization.charts.area_chart import create_area_chart
        output = str(tmp_path / "area_stacked.png")
        fig = create_area_chart(
            [1, 2, 3, 4],
            [[1, 2, 3, 4], [4, 3, 2, 1]],
            stacked=True,
            labels=["Series 1", "Series 2"],
            output_path=output,
        )
        assert isinstance(fig, plt.Figure)

    def test_multiple_area_unstacked(self, tmp_path):
        """Test functionality: multiple area unstacked."""
        from codomyrmex.data_visualization.charts.area_chart import create_area_chart
        output = str(tmp_path / "area_multi.png")
        fig = create_area_chart(
            [1, 2, 3],
            [[1, 3, 2], [2, 1, 3]],
            output_path=output,
        )
        assert isinstance(fig, plt.Figure)

    def test_empty_data_returns_none(self):
        """Test functionality: empty data returns none."""
        from codomyrmex.data_visualization.charts.area_chart import create_area_chart
        assert create_area_chart([], []) is None

    def test_area_chart_class(self, tmp_path):
        """Test functionality: area chart class."""
        from codomyrmex.data_visualization.charts.area_chart import AreaChart
        chart = AreaChart(x_data=[1, 2, 3], y_data=[3, 1, 2], title="OO Area")
        output = str(tmp_path / "area_oo.png")
        chart.save(output)
        assert Path(output).exists()
