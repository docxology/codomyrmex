"""Unit tests verifying data_visualization module imports and public API availability."""

import pytest


# ============================================================================
# TestImports
# ============================================================================
@pytest.mark.unit
class TestImports:
    """Test that all module and submodule imports work correctly."""

    def test_import_data_visualization_package(self):
        """Verify import data visualization package behavior."""
        import codomyrmex.data_visualization
        assert hasattr(codomyrmex.data_visualization, '__version__')

    def test_import_charts_submodule(self):
        """Verify import charts submodule behavior."""
        from codomyrmex.data_visualization import charts
        assert hasattr(charts, '__name__')

    def test_import_themes_submodule(self):
        """Verify import themes submodule behavior."""
        from codomyrmex.data_visualization import themes
        assert hasattr(themes, '__name__')

    def test_import_mermaid_submodule(self):
        """Verify import mermaid submodule behavior."""
        from codomyrmex.data_visualization import mermaid
        assert hasattr(mermaid, '__name__')

    def test_import_engines_submodule(self):
        """Verify import engines submodule behavior."""
        from codomyrmex.data_visualization import engines
        assert hasattr(engines, '__name__')

    def test_import_git_submodule(self):
        """Verify import git submodule behavior."""
        from codomyrmex.data_visualization import git
        assert hasattr(git, '__name__')

    def test_import_exceptions(self):
        """Verify import exceptions behavior."""
        from codomyrmex.data_visualization.exceptions import (
            ChartCreationError,
            DataVisualizationError,
            InvalidDataError,
        )
        assert issubclass(DataVisualizationError, Exception)
        assert issubclass(ChartCreationError, Exception)
        assert issubclass(InvalidDataError, DataVisualizationError)

    def test_import_chart_functions_from_charts(self):
        """Verify import chart functions from charts behavior."""
        from codomyrmex.data_visualization.charts import (
            create_area_chart,
            create_bar_chart,
            create_box_plot,
            create_heatmap,
            create_histogram,
            create_line_plot,
            create_pie_chart,
            create_scatter_plot,
        )
        assert all(callable(f) for f in [
            create_bar_chart, create_line_plot, create_scatter_plot,
            create_histogram, create_pie_chart, create_heatmap,
            create_box_plot, create_area_chart,
        ])

    def test_import_chart_classes_from_charts(self):
        """Verify import chart classes from charts behavior."""
        from codomyrmex.data_visualization.charts import (
            AreaChart,
            BarChart,
            BoxPlot,
            Heatmap,
            Histogram,
            LinePlot,
            PieChart,
            ScatterPlot,
        )
        assert all(callable(c) for c in [
            BarChart, LinePlot, ScatterPlot, Histogram, PieChart,
            Heatmap, BoxPlot, AreaChart,
        ])



    def test_engines_plotter_class(self):
        """Verify engines plotter class behavior."""
        from codomyrmex.data_visualization.engines import Plotter
        assert callable(Plotter)

    def test_engines_advanced_plotter_class(self):
        """Verify engines advanced plotter class behavior."""
        from codomyrmex.data_visualization.engines import AdvancedPlotter
        assert callable(AdvancedPlotter)

    def test_git_visualizer_import(self):
        """Verify git visualizer import behavior."""
        from codomyrmex.data_visualization.git import GitVisualizer
        assert callable(GitVisualizer)

    def test_top_level_create_heatmap(self):
        """Verify top level create heatmap behavior."""
        from codomyrmex.data_visualization import create_heatmap
        assert callable(create_heatmap)

    def test_top_level_create_box_plot(self):
        """Verify top level create box plot behavior."""
        from codomyrmex.data_visualization import create_box_plot
        assert callable(create_box_plot)

    def test_top_level_create_area_chart(self):
        """Verify top level create area chart behavior."""
        from codomyrmex.data_visualization import create_area_chart
        assert callable(create_area_chart)
