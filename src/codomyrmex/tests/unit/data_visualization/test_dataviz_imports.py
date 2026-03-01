"""Unit tests verifying data_visualization module imports and public API availability."""

import pytest


# ============================================================================
# TestImports
# ============================================================================
@pytest.mark.unit
class TestImports:
    """Test that all module and submodule imports work correctly."""

    def test_import_data_visualization_package(self):
        """Test functionality: import data visualization package."""
        import codomyrmex.data_visualization
        assert hasattr(codomyrmex.data_visualization, '__version__')

    def test_import_charts_submodule(self):
        """Test functionality: import charts submodule."""
        from codomyrmex.data_visualization import charts
        assert hasattr(charts, '__name__')

    def test_import_themes_submodule(self):
        """Test functionality: import themes submodule."""
        from codomyrmex.data_visualization import themes
        assert hasattr(themes, '__name__')

    def test_import_mermaid_submodule(self):
        """Test functionality: import mermaid submodule."""
        from codomyrmex.data_visualization import mermaid
        assert hasattr(mermaid, '__name__')

    def test_import_engines_submodule(self):
        """Test functionality: import engines submodule."""
        from codomyrmex.data_visualization import engines
        assert hasattr(engines, '__name__')

    def test_import_git_submodule(self):
        """Test functionality: import git submodule."""
        from codomyrmex.data_visualization import git
        assert hasattr(git, '__name__')

    def test_import_exceptions(self):
        """Test functionality: import exceptions."""
        from codomyrmex.data_visualization.exceptions import (
            ChartCreationError,
            DataVisualizationError,
            InvalidDataError,
        )
        assert issubclass(DataVisualizationError, Exception)
        assert issubclass(ChartCreationError, Exception)
        assert issubclass(InvalidDataError, DataVisualizationError)

    def test_import_chart_functions_from_charts(self):
        """Test functionality: import chart functions from charts."""
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
        """Test functionality: import chart classes from charts."""
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
        """Test functionality: engines plotter class."""
        from codomyrmex.data_visualization.engines import Plotter
        assert callable(Plotter)

    def test_engines_advanced_plotter_class(self):
        """Test functionality: engines advanced plotter class."""
        from codomyrmex.data_visualization.engines import AdvancedPlotter
        assert callable(AdvancedPlotter)

    def test_git_visualizer_import(self):
        """Test functionality: git visualizer import."""
        from codomyrmex.data_visualization.git import GitVisualizer
        assert callable(GitVisualizer)

    def test_top_level_create_heatmap(self):
        """Test functionality: top level create heatmap."""
        from codomyrmex.data_visualization import create_heatmap
        assert callable(create_heatmap)

    def test_top_level_create_box_plot(self):
        """Test functionality: top level create box plot."""
        from codomyrmex.data_visualization import create_box_plot
        assert callable(create_box_plot)

    def test_top_level_create_area_chart(self):
        """Test functionality: top level create area chart."""
        from codomyrmex.data_visualization import create_area_chart
        assert callable(create_area_chart)
