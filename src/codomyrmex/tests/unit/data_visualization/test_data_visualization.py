"""Comprehensive unit tests for the data_visualization module."""

import pytest
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path

# Use non-interactive backend for testing
matplotlib.use('Agg')


# ============================================================================
# TestImports
# ============================================================================
@pytest.mark.unit
class TestImports:
    """Test that all module and submodule imports work correctly."""

    def test_import_data_visualization_package(self):
        import codomyrmex.data_visualization
        assert hasattr(codomyrmex.data_visualization, '__version__')

    def test_import_charts_submodule(self):
        from codomyrmex.data_visualization import charts
        assert charts is not None

    def test_import_themes_submodule(self):
        from codomyrmex.data_visualization import themes
        assert themes is not None

    def test_import_mermaid_submodule(self):
        from codomyrmex.data_visualization import mermaid
        assert mermaid is not None

    def test_import_engines_submodule(self):
        from codomyrmex.data_visualization import engines
        assert engines is not None

    def test_import_git_submodule(self):
        from codomyrmex.data_visualization import git
        assert git is not None

    def test_import_exceptions(self):
        from codomyrmex.data_visualization.exceptions import (
            DataVisualizationError,
            ChartCreationError,
            InvalidDataError,
            ThemeError,
            MermaidGenerationError,
            GitVisualizationError,
            PlotSaveError,
        )
        assert DataVisualizationError is not None
        assert ChartCreationError is not None
        assert InvalidDataError is not None

    def test_import_chart_functions_from_charts(self):
        from codomyrmex.data_visualization.charts import (
            create_bar_chart, create_line_plot, create_scatter_plot,
            create_histogram, create_pie_chart, create_heatmap,
            create_box_plot, create_area_chart,
        )
        assert all(callable(f) for f in [
            create_bar_chart, create_line_plot, create_scatter_plot,
            create_histogram, create_pie_chart, create_heatmap,
            create_box_plot, create_area_chart,
        ])

    def test_import_chart_classes_from_charts(self):
        from codomyrmex.data_visualization.charts import (
            BarChart, LinePlot, ScatterPlot, Histogram, PieChart,
            Heatmap, BoxPlot, AreaChart,
        )
        assert all(c is not None for c in [
            BarChart, LinePlot, ScatterPlot, Histogram, PieChart,
            Heatmap, BoxPlot, AreaChart,
        ])

    def test_backward_compat_line_plot_import(self):
        from codomyrmex.data_visualization.line_plot import create_line_plot
        assert callable(create_line_plot)

    def test_backward_compat_bar_chart_import(self):
        from codomyrmex.data_visualization.bar_chart import create_bar_chart
        assert callable(create_bar_chart)

    def test_backward_compat_scatter_plot_import(self):
        from codomyrmex.data_visualization.scatter_plot import create_scatter_plot
        assert callable(create_scatter_plot)

    def test_backward_compat_histogram_import(self):
        from codomyrmex.data_visualization.histogram import create_histogram
        assert callable(create_histogram)

    def test_backward_compat_pie_chart_import(self):
        from codomyrmex.data_visualization.pie_chart import create_pie_chart
        assert callable(create_pie_chart)

    def test_backward_compat_plotter_import(self):
        from codomyrmex.data_visualization.plotter import create_heatmap
        assert callable(create_heatmap)

    def test_backward_compat_plot_utils_import(self):
        from codomyrmex.data_visualization.plot_utils import save_plot, get_codomyrmex_logger
        assert callable(save_plot)
        assert callable(get_codomyrmex_logger)

    def test_engines_plotter_class(self):
        from codomyrmex.data_visualization.engines import Plotter
        assert Plotter is not None

    def test_engines_advanced_plotter_class(self):
        from codomyrmex.data_visualization.engines import AdvancedPlotter
        assert AdvancedPlotter is not None

    def test_git_visualizer_import(self):
        from codomyrmex.data_visualization.git import GitVisualizer
        assert GitVisualizer is not None

    def test_top_level_create_heatmap(self):
        from codomyrmex.data_visualization import create_heatmap
        assert callable(create_heatmap)

    def test_top_level_create_box_plot(self):
        from codomyrmex.data_visualization import create_box_plot
        assert callable(create_box_plot)

    def test_top_level_create_area_chart(self):
        from codomyrmex.data_visualization import create_area_chart
        assert callable(create_area_chart)


# ============================================================================
# TestPlotUtils
# ============================================================================
@pytest.mark.unit
class TestPlotUtils:
    """Test plot utility functions."""

    def test_get_codomyrmex_logger(self):
        from codomyrmex.data_visualization.charts.plot_utils import get_codomyrmex_logger
        logger = get_codomyrmex_logger("test_module")
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')

    def test_save_plot_success(self, tmp_path):
        from codomyrmex.data_visualization.charts.plot_utils import save_plot
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        output_path = str(tmp_path / "test_save.png")
        result = save_plot(fig, output_path)
        assert result is True
        assert Path(output_path).exists()
        assert Path(output_path).stat().st_size > 0
        plt.close(fig)

    def test_save_plot_creates_directory(self, tmp_path):
        from codomyrmex.data_visualization.charts.plot_utils import save_plot
        fig, ax = plt.subplots()
        ax.plot([1, 2], [3, 4])
        output_path = str(tmp_path / "nested" / "dir" / "plot.png")
        result = save_plot(fig, output_path)
        assert result is True
        assert Path(output_path).exists()
        plt.close(fig)

    def test_save_plot_pdf_format(self, tmp_path):
        from codomyrmex.data_visualization.charts.plot_utils import save_plot
        fig, ax = plt.subplots()
        ax.plot([1, 2], [3, 4])
        output_path = str(tmp_path / "test_save.pdf")
        result = save_plot(fig, output_path)
        assert result is True
        assert Path(output_path).exists()
        plt.close(fig)

    def test_apply_common_aesthetics(self):
        from codomyrmex.data_visualization.charts.plot_utils import apply_common_aesthetics
        fig, ax = plt.subplots()
        result = apply_common_aesthetics(ax, title="Test", x_label="X", y_label="Y")
        assert result is ax
        assert ax.get_title() == "Test"
        assert ax.get_xlabel() == "X"
        assert ax.get_ylabel() == "Y"
        assert ax.spines['top'].get_visible() is False
        assert ax.spines['right'].get_visible() is False
        plt.close(fig)

    def test_get_color_palette_default(self):
        from codomyrmex.data_visualization.charts.plot_utils import get_color_palette
        palette = get_color_palette()
        assert len(palette) == 10
        assert all(c.startswith('#') for c in palette)

    def test_get_color_palette_custom_size(self):
        from codomyrmex.data_visualization.charts.plot_utils import get_color_palette
        palette = get_color_palette(5)
        assert len(palette) == 5

    def test_get_color_palette_more_than_base(self):
        from codomyrmex.data_visualization.charts.plot_utils import get_color_palette
        palette = get_color_palette(15)
        assert len(palette) == 15

    def test_configure_plot(self):
        from codomyrmex.data_visualization.charts.plot_utils import configure_plot
        fig, ax = plt.subplots()
        result_fig, result_ax = configure_plot(fig, ax, title="Config Test")
        assert result_fig is fig
        assert result_ax is ax
        assert ax.get_title() == "Config Test"
        plt.close(fig)

    def test_apply_style(self):
        from codomyrmex.data_visualization.charts.plot_utils import apply_style
        fig, ax = plt.subplots()
        result = apply_style(ax, "default")
        assert result is ax
        plt.close(fig)

    def test_save_figure_alias(self):
        from codomyrmex.data_visualization.charts.plot_utils import save_figure, save_plot
        assert save_figure is save_plot

    def test_default_figure_size(self):
        from codomyrmex.data_visualization.charts.plot_utils import DEFAULT_FIGURE_SIZE
        assert DEFAULT_FIGURE_SIZE == (10, 6)


# ============================================================================
# TestBarChart
# ============================================================================
@pytest.mark.unit
class TestBarChart:
    """Test bar chart generation."""

    def test_basic_bar_chart(self, tmp_path):
        from codomyrmex.data_visualization.charts.bar_chart import create_bar_chart
        output = str(tmp_path / "bar.png")
        fig = create_bar_chart(['A', 'B', 'C'], [1, 2, 3], output_path=output)
        assert fig is not None
        assert Path(output).exists()

    def test_horizontal_bar_chart(self, tmp_path):
        from codomyrmex.data_visualization.charts.bar_chart import create_bar_chart
        output = str(tmp_path / "bar_h.png")
        fig = create_bar_chart(['A', 'B'], [10, 20], horizontal=True, output_path=output)
        assert fig is not None
        assert Path(output).exists()

    def test_empty_data_returns_none(self):
        from codomyrmex.data_visualization.charts.bar_chart import create_bar_chart
        assert create_bar_chart([], [1, 2]) is None
        assert create_bar_chart(['A'], []) is None

    def test_mismatched_lengths_returns_none(self):
        from codomyrmex.data_visualization.charts.bar_chart import create_bar_chart
        assert create_bar_chart(['A', 'B'], [1, 2, 3]) is None

    def test_bar_chart_with_theme(self, tmp_path):
        from codomyrmex.data_visualization.charts.bar_chart import create_bar_chart
        output = str(tmp_path / "bar_theme.png")
        fig = create_bar_chart(['X', 'Y'], [5, 10], theme="dark", output_path=output)
        assert fig is not None

    def test_bar_chart_class(self, tmp_path):
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
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        output = str(tmp_path / "line.png")
        fig = create_line_plot([1, 2, 3], [4, 5, 6], output_path=output)
        assert fig is not None
        assert Path(output).exists()

    def test_multiple_lines(self, tmp_path):
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        output = str(tmp_path / "multi_line.png")
        fig = create_line_plot(
            [1, 2, 3],
            [[1, 2, 3], [3, 2, 1]],
            line_labels=["Up", "Down"],
            output_path=output,
        )
        assert fig is not None
        assert Path(output).exists()

    def test_empty_data_returns_none(self):
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        assert create_line_plot([], []) is None

    def test_with_markers(self, tmp_path):
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        output = str(tmp_path / "markers.png")
        fig = create_line_plot([1, 2, 3], [1, 4, 9], markers=True, output_path=output)
        assert fig is not None

    def test_line_plot_with_theme(self, tmp_path):
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        fig = create_line_plot([1, 2, 3], [2, 4, 6], theme="light")
        assert fig is not None

    def test_line_plot_class(self, tmp_path):
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
        from codomyrmex.data_visualization.charts.scatter_plot import create_scatter_plot
        output = str(tmp_path / "scatter.png")
        fig = create_scatter_plot([1, 2, 3], [4, 5, 6], output_path=output)
        assert fig is not None
        assert Path(output).exists()

    def test_empty_data_returns_none(self):
        from codomyrmex.data_visualization.charts.scatter_plot import create_scatter_plot
        assert create_scatter_plot([], []) is None

    def test_mismatched_data_returns_none(self):
        from codomyrmex.data_visualization.charts.scatter_plot import create_scatter_plot
        assert create_scatter_plot([1, 2], [1, 2, 3]) is None

    def test_custom_styling(self, tmp_path):
        from codomyrmex.data_visualization.charts.scatter_plot import create_scatter_plot
        output = str(tmp_path / "scatter_styled.png")
        fig = create_scatter_plot(
            [1, 2, 3, 4], [2, 4, 6, 8],
            dot_size=50, dot_color="red", alpha=0.5,
            output_path=output,
        )
        assert fig is not None

    def test_scatter_with_theme(self, tmp_path):
        from codomyrmex.data_visualization.charts.scatter_plot import create_scatter_plot
        fig = create_scatter_plot([1, 2, 3], [3, 2, 1], theme="vibrant")
        assert fig is not None

    def test_scatter_plot_class(self, tmp_path):
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
        from codomyrmex.data_visualization.charts.histogram import create_histogram
        output = str(tmp_path / "hist.png")
        fig = create_histogram([1, 2, 2, 3, 3, 3, 4, 5], output_path=output)
        assert fig is not None
        assert Path(output).exists()

    def test_empty_data_returns_none(self):
        from codomyrmex.data_visualization.charts.histogram import create_histogram
        assert create_histogram([]) is None

    def test_custom_bins(self, tmp_path):
        from codomyrmex.data_visualization.charts.histogram import create_histogram
        output = str(tmp_path / "hist_bins.png")
        fig = create_histogram(list(range(50)), bins=5, output_path=output)
        assert fig is not None

    def test_histogram_with_theme(self, tmp_path):
        from codomyrmex.data_visualization.charts.histogram import create_histogram
        fig = create_histogram([1, 2, 3, 4, 5], theme="minimal")
        assert fig is not None

    def test_histogram_class(self, tmp_path):
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
        from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart
        output = str(tmp_path / "pie.png")
        fig = create_pie_chart(['A', 'B', 'C'], [10, 20, 30], output_path=output)
        assert fig is not None
        assert Path(output).exists()

    def test_pie_with_explode(self, tmp_path):
        from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart
        output = str(tmp_path / "pie_explode.png")
        fig = create_pie_chart(
            ['A', 'B', 'C'], [10, 20, 30],
            explode=[0, 0.1, 0],
            output_path=output,
        )
        assert fig is not None

    def test_empty_data_returns_none(self):
        from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart
        assert create_pie_chart([], []) is None

    def test_mismatched_explode_ignored(self, tmp_path):
        from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart
        output = str(tmp_path / "pie_mismatch.png")
        fig = create_pie_chart(
            ['A', 'B'], [10, 20],
            explode=[0, 0.1, 0],
            output_path=output,
        )
        assert fig is not None

    def test_pie_with_theme(self, tmp_path):
        from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart
        fig = create_pie_chart(['X', 'Y'], [40, 60], theme="scientific")
        assert fig is not None

    def test_pie_chart_class(self, tmp_path):
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
        from codomyrmex.data_visualization.charts.heatmap import create_heatmap
        output = str(tmp_path / "heatmap.png")
        fig = create_heatmap([[1, 2], [3, 4]], output_path=output)
        assert fig is not None
        assert Path(output).exists()

    def test_heatmap_with_labels(self, tmp_path):
        from codomyrmex.data_visualization.charts.heatmap import create_heatmap
        output = str(tmp_path / "heatmap_labels.png")
        fig = create_heatmap(
            [[1, 2, 3], [4, 5, 6]],
            x_labels=['A', 'B', 'C'],
            y_labels=['Row1', 'Row2'],
            output_path=output,
        )
        assert fig is not None

    def test_heatmap_with_annotations(self, tmp_path):
        from codomyrmex.data_visualization.charts.heatmap import create_heatmap
        output = str(tmp_path / "heatmap_annot.png")
        fig = create_heatmap([[1, 2], [3, 4]], annot=True, output_path=output)
        assert fig is not None

    def test_heatmap_invalid_data_returns_none(self):
        from codomyrmex.data_visualization.charts.heatmap import create_heatmap
        assert create_heatmap(None) is None
        assert create_heatmap([]) is None
        assert create_heatmap("not a list") is None

    def test_heatmap_with_theme(self, tmp_path):
        from codomyrmex.data_visualization.charts.heatmap import create_heatmap
        fig = create_heatmap([[1, 2], [3, 4]], theme="dark")
        assert fig is not None

    def test_heatmap_class(self, tmp_path):
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
        from codomyrmex.data_visualization.charts.box_plot import create_box_plot
        output = str(tmp_path / "box.png")
        fig = create_box_plot([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], output_path=output)
        assert fig is not None
        assert Path(output).exists()

    def test_box_plot_with_dict_data(self, tmp_path):
        from codomyrmex.data_visualization.charts.box_plot import create_box_plot
        output = str(tmp_path / "box_dict.png")
        fig = create_box_plot(
            {"Group A": [1, 2, 3, 4, 5], "Group B": [3, 4, 5, 6, 7]},
            output_path=output,
        )
        assert fig is not None

    def test_box_plot_multiple_lists(self, tmp_path):
        from codomyrmex.data_visualization.charts.box_plot import create_box_plot
        output = str(tmp_path / "box_multi.png")
        fig = create_box_plot(
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            labels=["Low", "Mid", "High"],
            output_path=output,
        )
        assert fig is not None

    def test_box_plot_empty_returns_none(self):
        from codomyrmex.data_visualization.charts.box_plot import create_box_plot
        assert create_box_plot([]) is None
        assert create_box_plot(None) is None

    def test_box_plot_class(self, tmp_path):
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
        from codomyrmex.data_visualization.charts.area_chart import create_area_chart
        output = str(tmp_path / "area.png")
        fig = create_area_chart([1, 2, 3, 4, 5], [2, 4, 3, 5, 4], output_path=output)
        assert fig is not None
        assert Path(output).exists()

    def test_stacked_area_chart(self, tmp_path):
        from codomyrmex.data_visualization.charts.area_chart import create_area_chart
        output = str(tmp_path / "area_stacked.png")
        fig = create_area_chart(
            [1, 2, 3, 4],
            [[1, 2, 3, 4], [4, 3, 2, 1]],
            stacked=True,
            labels=["Series 1", "Series 2"],
            output_path=output,
        )
        assert fig is not None

    def test_multiple_area_unstacked(self, tmp_path):
        from codomyrmex.data_visualization.charts.area_chart import create_area_chart
        output = str(tmp_path / "area_multi.png")
        fig = create_area_chart(
            [1, 2, 3],
            [[1, 3, 2], [2, 1, 3]],
            output_path=output,
        )
        assert fig is not None

    def test_empty_data_returns_none(self):
        from codomyrmex.data_visualization.charts.area_chart import create_area_chart
        assert create_area_chart([], []) is None

    def test_area_chart_class(self, tmp_path):
        from codomyrmex.data_visualization.charts.area_chart import AreaChart
        chart = AreaChart(x_data=[1, 2, 3], y_data=[3, 1, 2], title="OO Area")
        output = str(tmp_path / "area_oo.png")
        chart.save(output)
        assert Path(output).exists()


# ============================================================================
# TestThemes
# ============================================================================
@pytest.mark.unit
class TestThemes:
    """Test theme system."""

    def test_get_all_themes(self):
        from codomyrmex.data_visualization.themes import ThemeName, get_theme
        for name in ThemeName:
            theme = get_theme(name)
            assert theme is not None
            assert theme.name == name

    def test_default_theme(self):
        from codomyrmex.data_visualization.themes import ThemeName, get_theme
        theme = get_theme(ThemeName.DEFAULT)
        assert theme.colors.primary == "#1f77b4"

    def test_dark_theme(self):
        from codomyrmex.data_visualization.themes import ThemeName, get_theme
        theme = get_theme(ThemeName.DARK)
        assert theme.figure_facecolor == "#1a1a2e"

    def test_theme_to_rcparams(self):
        from codomyrmex.data_visualization.themes import ThemeName, get_theme
        theme = get_theme(ThemeName.DEFAULT)
        params = theme.to_matplotlib_rcparams()
        assert isinstance(params, dict)
        assert 'figure.facecolor' in params
        assert 'axes.facecolor' in params
        assert 'font.family' in params

    def test_apply_theme(self):
        from codomyrmex.data_visualization.themes import ThemeName, get_theme, apply_theme
        theme = get_theme(ThemeName.LIGHT)
        apply_theme(theme)
        assert plt.rcParams['figure.facecolor'] == theme.figure_facecolor

    def test_list_themes(self):
        from codomyrmex.data_visualization.themes import list_themes
        themes = list_themes()
        assert isinstance(themes, list)
        assert len(themes) == 6
        assert "default" in themes
        assert "dark" in themes

    def test_color_palette_cycling(self):
        from codomyrmex.data_visualization.themes import ThemeName, get_theme
        theme = get_theme(ThemeName.DEFAULT)
        palette = theme.colors
        # Should cycle
        color0 = palette.get_series_color(0)
        color_cycle = palette.get_series_color(len(palette.series))
        assert color0 == color_cycle

    def test_minimal_theme_no_grid(self):
        from codomyrmex.data_visualization.themes import ThemeName, get_theme
        theme = get_theme(ThemeName.MINIMAL)
        assert theme.grid.show is False

    def test_scientific_theme_serif(self):
        from codomyrmex.data_visualization.themes import ThemeName, get_theme
        theme = get_theme(ThemeName.SCIENTIFIC)
        assert theme.fonts.family == "serif"


# ============================================================================
# TestAdvancedPlotter
# ============================================================================
@pytest.mark.unit
class TestAdvancedPlotter:
    """Test the AdvancedPlotter class."""

    def test_create_figure(self):
        from codomyrmex.data_visualization.engines.advanced_plotter import AdvancedPlotter
        plotter = AdvancedPlotter()
        fig, ax = plotter.create_figure()
        assert fig is not None
        assert ax is not None
        plotter.clear_figures()

    def test_plot_line(self):
        from codomyrmex.data_visualization.engines.advanced_plotter import AdvancedPlotter
        plotter = AdvancedPlotter()
        plotter.create_figure()
        line = plotter.plot_line([1, 2, 3], [4, 5, 6], label="test")
        assert line is not None
        plotter.clear_figures()

    def test_plot_scatter(self):
        from codomyrmex.data_visualization.engines.advanced_plotter import AdvancedPlotter
        plotter = AdvancedPlotter()
        plotter.create_figure()
        scatter = plotter.plot_scatter([1, 2, 3], [4, 5, 6])
        assert scatter is not None
        plotter.clear_figures()

    def test_plot_bar(self):
        from codomyrmex.data_visualization.engines.advanced_plotter import AdvancedPlotter
        plotter = AdvancedPlotter()
        plotter.create_figure()
        bars = plotter.plot_bar(['A', 'B'], [10, 20])
        assert bars is not None
        plotter.clear_figures()

    def test_plot_histogram(self):
        from codomyrmex.data_visualization.engines.advanced_plotter import AdvancedPlotter
        plotter = AdvancedPlotter()
        plotter.create_figure()
        result = plotter.plot_histogram([1, 2, 2, 3, 3, 3])
        assert result is not None
        plotter.clear_figures()

    def test_plot_heatmap(self):
        from codomyrmex.data_visualization.engines.advanced_plotter import AdvancedPlotter
        plotter = AdvancedPlotter()
        plotter.create_figure()
        try:
            hm = plotter.plot_heatmap([[1, 2], [3, 4]])
            assert hm is not None
        except TypeError:
            # seaborn version incompatibility with xticklabels
            pytest.skip("seaborn heatmap incompatible with current version")
        finally:
            plotter.clear_figures()

    def test_plot_box(self):
        from codomyrmex.data_visualization.engines.advanced_plotter import AdvancedPlotter
        plotter = AdvancedPlotter()
        plotter.create_figure()
        bp = plotter.plot_box({"A": [1, 2, 3], "B": [4, 5, 6]})
        assert bp is not None
        plotter.clear_figures()

    def test_save_plot(self, tmp_path):
        from codomyrmex.data_visualization.engines.advanced_plotter import AdvancedPlotter
        plotter = AdvancedPlotter()
        plotter.create_figure()
        plotter.plot_line([1, 2, 3], [1, 4, 9])
        output = str(tmp_path / "adv_plot.png")
        result = plotter.save_plot(output)
        assert result is True
        assert Path(output).exists()
        plotter.clear_figures()

    def test_clear_figures(self):
        from codomyrmex.data_visualization.engines.advanced_plotter import AdvancedPlotter
        plotter = AdvancedPlotter()
        plotter.create_figure()
        plotter.create_figure()
        assert len(plotter.figures) == 2
        plotter.clear_figures()
        assert len(plotter.figures) == 0
        assert plotter.current_figure is None

    def test_convenience_functions(self):
        from codomyrmex.data_visualization.engines.advanced_plotter import (
            create_advanced_line_plot,
            create_advanced_scatter_plot,
            create_advanced_bar_chart,
            get_available_styles,
            get_available_palettes,
            get_available_plot_types,
        )
        assert callable(create_advanced_line_plot)
        assert callable(create_advanced_scatter_plot)
        assert callable(create_advanced_bar_chart)
        assert len(get_available_styles()) > 0
        assert len(get_available_palettes()) > 0
        assert len(get_available_plot_types()) > 0

    def test_plot_config_dataclass(self):
        from codomyrmex.data_visualization.engines.advanced_plotter import PlotConfig
        config = PlotConfig(title="Test", figsize=(8, 5), dpi=150)
        assert config.title == "Test"
        assert config.figsize == (8, 5)
        assert config.dpi == 150

    def test_enums(self):
        from codomyrmex.data_visualization.engines.advanced_plotter import (
            PlotType, ChartStyle, ColorPalette,
        )
        assert PlotType.LINE.value == "line"
        assert ChartStyle.DARK.value == "dark"
        assert ColorPalette.VIRIDIS.value == "viridis"


# ============================================================================
# TestMermaidBuilders
# ============================================================================
@pytest.mark.unit
class TestMermaidBuilders:
    """Test Mermaid diagram builder classes."""

    def test_flowchart_creation(self):
        from codomyrmex.data_visualization.mermaid import (
            Flowchart, FlowDirection, NodeShape,
        )
        fc = Flowchart(direction=FlowDirection.TOP_DOWN)
        fc.add_node("A", "Start", NodeShape.ROUND)
        fc.add_node("B", "End", NodeShape.ROUND)
        fc.add_link("A", "B", "goes to")
        content = fc.render()
        assert "flowchart TD" in content
        assert "A" in content
        assert "B" in content

    def test_sequence_diagram(self):
        from codomyrmex.data_visualization.mermaid import SequenceDiagram
        sd = SequenceDiagram()
        sd.add_participant("Alice")
        sd.add_participant("Bob")
        sd.add_message("Alice", "Bob", "Hello")
        content = sd.render()
        assert "sequenceDiagram" in content
        assert "Alice" in content
        assert "Bob" in content

    def test_class_diagram(self):
        from codomyrmex.data_visualization.mermaid import ClassDiagram
        cd = ClassDiagram()
        cd.add_class("Animal", attributes=["name: str"], methods=["speak()"])
        content = cd.render()
        assert "classDiagram" in content
        assert "Animal" in content

    def test_flowchart_subgraph(self):
        from codomyrmex.data_visualization.mermaid import (
            Flowchart, FlowDirection, NodeShape,
        )
        fc = Flowchart(direction=FlowDirection.LEFT_RIGHT)
        fc.add_node("A", "Node A", NodeShape.RECTANGLE)
        fc.add_node("B", "Node B", NodeShape.RECTANGLE)
        fc.add_subgraph("Sub1", "My Subgraph", ["B"])
        content = fc.render()
        assert "subgraph" in content

    def test_to_markdown(self):
        from codomyrmex.data_visualization.mermaid import Flowchart, FlowDirection
        fc = Flowchart(direction=FlowDirection.TOP_DOWN)
        md = fc.to_markdown()
        assert "```mermaid" in md
        assert "```" in md


# ============================================================================
# TestMermaidGenerator
# ============================================================================
@pytest.mark.unit
class TestMermaidGenerator:
    """Test MermaidDiagramGenerator."""

    def test_git_branch_diagram(self):
        from codomyrmex.data_visualization.mermaid.mermaid_generator import MermaidDiagramGenerator
        gen = MermaidDiagramGenerator()
        branches = [{"name": "main", "created_at": "2024-01-01"}]
        commits = [
            {"hash": "abc123", "message": "Init", "branch": "main", "date": "2024-01-01"},
        ]
        content = gen.create_git_branch_diagram(branches=branches, commits=commits)
        assert content  # non-empty

    def test_git_workflow_diagram(self):
        from codomyrmex.data_visualization.mermaid.mermaid_generator import MermaidDiagramGenerator
        gen = MermaidDiagramGenerator()
        workflow_steps = [
            {"name": "checkout", "description": "Checkout code"},
            {"name": "build", "description": "Build project"},
        ]
        content = gen.create_git_workflow_diagram(workflow_steps=workflow_steps, title="Test Workflow")
        assert content
        assert len(content) > 0

    def test_commit_timeline_diagram(self):
        from codomyrmex.data_visualization.mermaid.mermaid_generator import create_commit_timeline_diagram
        commits = [
            {"hash": "abc", "message": "First", "date": "2024-01-01"},
            {"hash": "def", "message": "Second", "date": "2024-01-02"},
        ]
        content = create_commit_timeline_diagram(commits=commits)
        assert content

    def test_repository_structure_diagram(self):
        from codomyrmex.data_visualization.mermaid.mermaid_generator import MermaidDiagramGenerator
        gen = MermaidDiagramGenerator()
        structure = {"src": {"main.py": "file"}, "README.md": "file"}
        content = gen.create_repository_structure_diagram(repo_structure=structure)
        assert content

    def test_save_mermaid_to_file(self, tmp_path):
        from codomyrmex.data_visualization.mermaid.mermaid_generator import MermaidDiagramGenerator
        gen = MermaidDiagramGenerator()
        output = str(tmp_path / "test.mmd")
        workflow_steps = [
            {"name": "checkout", "description": "Checkout code"},
        ]
        content = gen.create_git_workflow_diagram(
            workflow_steps=workflow_steps, title="Save Test", output_path=output
        )
        assert content
        assert Path(output).exists()


# ============================================================================
# TestGitVisualizer
# ============================================================================
@pytest.mark.unit
class TestGitVisualizer:
    """Test GitVisualizer class."""

    def test_instantiation(self):
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        assert viz is not None
        assert viz.mermaid_generator is not None
        assert "main" in viz.colors

    def test_git_tree_png_with_sample_data(self, tmp_path):
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        output = str(tmp_path / "git_tree.png")
        result = viz.visualize_git_tree_png(title="Test Tree", output_path=output)
        assert result is True
        assert Path(output).exists()

    def test_git_tree_mermaid_with_sample_data(self, tmp_path):
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        output = str(tmp_path / "git_tree.mmd")
        content = viz.visualize_git_tree_mermaid(title="Test Mermaid", output_path=output)
        assert content  # non-empty string

    def test_commit_activity_png(self, tmp_path):
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        output = str(tmp_path / "activity.png")
        result = viz.visualize_commit_activity_png(title="Activity", output_path=output)
        assert result is True
        assert Path(output).exists()

    def test_repository_summary_png(self, tmp_path):
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        output = str(tmp_path / "summary.png")
        result = viz.visualize_repository_summary_png(
            title="Summary", output_path=output
        )
        assert result is True
        assert Path(output).exists()

    def test_branch_color_mapping(self):
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        assert viz._get_branch_color("main") == viz.colors["main"]
        assert viz._get_branch_color("develop") == viz.colors["develop"]
        assert viz._get_branch_color("feature/auth") == viz.colors["feature"]
        assert viz._get_branch_color("hotfix/urgent") == viz.colors["hotfix"]
        assert viz._get_branch_color("release/1.0") == viz.colors["release"]
        assert viz._get_branch_color("other") == viz.colors["commit"]

    def test_sample_commits_generation(self):
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        commits = viz._generate_sample_commits(10)
        assert len(commits) == 10
        assert all("hash" in c and "message" in c for c in commits)

    def test_convenience_functions(self, tmp_path):
        from codomyrmex.data_visualization.git.git_visualizer import (
            create_git_tree_png, create_git_tree_mermaid,
        )
        png_output = str(tmp_path / "conv_tree.png")
        result = create_git_tree_png(output_path=png_output, title="Conv PNG")
        assert result is True

        mmd_output = str(tmp_path / "conv_tree.mmd")
        content = create_git_tree_mermaid(output_path=mmd_output, title="Conv Mermaid")
        assert content


# ============================================================================
# TestExceptions
# ============================================================================
@pytest.mark.unit
class TestExceptions:
    """Test exception hierarchy."""

    def test_exception_hierarchy(self):
        from codomyrmex.data_visualization.exceptions import (
            DataVisualizationError,
            ChartCreationError,
            InvalidDataError,
            ThemeError,
            MermaidGenerationError,
            GitVisualizationError,
            PlotSaveError,
        )
        from codomyrmex.exceptions import VisualizationError, PlottingError

        # DataVisualizationError inherits from VisualizationError
        assert issubclass(DataVisualizationError, VisualizationError)

        # ChartCreationError inherits from PlottingError
        assert issubclass(ChartCreationError, PlottingError)

        # All custom exceptions inherit from DataVisualizationError
        assert issubclass(InvalidDataError, DataVisualizationError)
        assert issubclass(ThemeError, DataVisualizationError)
        assert issubclass(MermaidGenerationError, DataVisualizationError)
        assert issubclass(GitVisualizationError, DataVisualizationError)
        assert issubclass(PlotSaveError, DataVisualizationError)

    def test_exceptions_are_raisable(self):
        from codomyrmex.data_visualization.exceptions import (
            DataVisualizationError,
            ChartCreationError,
            InvalidDataError,
        )

        with pytest.raises(DataVisualizationError):
            raise DataVisualizationError("test error")

        with pytest.raises(ChartCreationError):
            raise ChartCreationError("chart error")

        with pytest.raises(InvalidDataError):
            raise InvalidDataError("bad data")

    def test_exception_message(self):
        from codomyrmex.data_visualization.exceptions import DataVisualizationError
        err = DataVisualizationError("something went wrong")
        assert "something went wrong" in str(err)


# ============================================================================
# TestPlotter (engines.plotter.Plotter)
# ============================================================================
@pytest.mark.unit
class TestPlotter:
    """Test the Plotter wrapper class."""

    def test_plotter_bar_chart(self, tmp_path):
        from codomyrmex.data_visualization.engines.plotter import Plotter
        p = Plotter()
        fig = p.bar_chart(['A', 'B'], [1, 2], output_path=str(tmp_path / "p_bar.png"))
        assert fig is not None

    def test_plotter_line_plot(self, tmp_path):
        from codomyrmex.data_visualization.engines.plotter import Plotter
        p = Plotter()
        fig = p.line_plot([1, 2, 3], [4, 5, 6], output_path=str(tmp_path / "p_line.png"))
        assert fig is not None

    def test_plotter_heatmap(self, tmp_path):
        from codomyrmex.data_visualization.engines.plotter import Plotter
        p = Plotter()
        fig = p.heatmap([[1, 2], [3, 4]], output_path=str(tmp_path / "p_hm.png"))
        assert fig is not None

    def test_plotter_default_figure_size(self):
        from codomyrmex.data_visualization.engines.plotter import Plotter, DEFAULT_FIGURE_SIZE
        p = Plotter()
        assert p.figure_size == DEFAULT_FIGURE_SIZE
