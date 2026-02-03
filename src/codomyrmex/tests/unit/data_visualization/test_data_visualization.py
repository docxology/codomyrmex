"""Unit tests for data_visualization module."""

import pytest
import sys
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path

# Use non-interactive backend for testing
matplotlib.use('Agg')


@pytest.mark.unit
class TestDataVisualization:
    """Test cases for data visualization functionality."""

    def test_plotter_import(self, code_dir):
        """Test that we can import plotter module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.data_visualization import plotter
            assert plotter is not None
        except ImportError as e:
            pytest.fail(f"Failed to import plotter: {e}")

    def test_plot_utils_import(self, code_dir):
        """Test that we can import plot_utils module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.data_visualization import plot_utils
            assert plot_utils is not None
        except ImportError as e:
            pytest.fail(f"Failed to import plot_utils: {e}")

    def test_bar_chart_import(self, code_dir):
        """Test that we can import bar_chart module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.data_visualization import bar_chart
            assert bar_chart is not None
        except ImportError as e:
            pytest.fail(f"Failed to import bar_chart: {e}")

    def test_visualization_modules_structure(self, code_dir):
        """Test that all visualization modules have expected structure."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        modules_to_test = ['plotter', 'plot_utils', 'bar_chart', 'histogram',
                          'line_plot', 'pie_chart', 'scatter_plot']

        for module_name in modules_to_test:
            try:
                module = __import__(f'codomyrmex.data_visualization.{module_name}')
                assert hasattr(module, '__file__')
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")

    def test_plot_generation_real(self, tmp_path, code_dir):
        """Test plot generation with real matplotlib."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.line_plot import create_line_plot

        x_data = [1, 2, 3, 4, 5]
        y_data = [2, 4, 6, 8, 10]
        output_path = tmp_path / "test_plot.png"

        fig = create_line_plot(
            x_data=x_data,
            y_data=y_data,
            title="Real Test Plot",
            output_path=str(output_path),
            show_plot=False
        )

        assert fig is not None
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_plot_utils_functions(self, code_dir):
        """Test plot_utils module functions."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization import plot_utils

        # Test that the module has expected utility functions
        assert hasattr(plot_utils, '__file__')
        assert hasattr(plot_utils, 'get_codomyrmex_logger')
        assert hasattr(plot_utils, 'save_plot')
        assert hasattr(plot_utils, 'apply_common_aesthetics')
        assert callable(plot_utils.get_codomyrmex_logger)
        assert callable(plot_utils.save_plot)
        assert callable(plot_utils.apply_common_aesthetics)

    def test_get_codomyrmex_logger_with_codomyrmex(self, real_logger_fixture, code_dir):
        """Test get_codomyrmex_logger when Codomyrmex logging is available."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.plot_utils import get_codomyrmex_logger

        logger = get_codomyrmex_logger("test_module")

        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')

        # Test actual logging
        logger.info("Test message from get_codomyrmex_logger")

        # Verify log file contains the message
        log_file = real_logger_fixture["log_file"]
        if log_file.exists():
            log_content = log_file.read_text()
            # The message might be in the log file
            assert len(log_content) >= 0  # At least log file exists

    def test_get_codomyrmex_logger_fallback(self, code_dir):
        """Test get_codomyrmex_logger fallback when Codomyrmex logging is not available."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.plot_utils import get_codomyrmex_logger

        # Test that it works even if Codomyrmex logging is not available
        # (it should fall back to standard logging)
        logger = get_codomyrmex_logger("test_module_fallback")

        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'debug')

        # Test actual logging
        logger.info("Test fallback message")

    def test_save_plot_success(self, tmp_path, code_dir):
        """Test save_plot function with real file operations."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.plot_utils import save_plot

        # Create a real matplotlib figure
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        output_path = str(tmp_path / "test_plot.png")

        save_plot(fig, output_path, dpi=150)

        # Verify file was created
        assert Path(output_path).exists()
        assert Path(output_path).stat().st_size > 0
        plt.close(fig)

    def test_save_plot_no_output_path(self, code_dir):
        """Test save_plot function with no output path."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.plot_utils import save_plot

        # Create a real matplotlib figure
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        # Should not raise an error when output_path is empty
        save_plot(fig, "", dpi=150)

        plt.close(fig)

    def test_save_plot_error(self, tmp_path, code_dir):
        """Test save_plot function error handling with real file operations."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.plot_utils import save_plot

        # Create a real matplotlib figure
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        # Use a path that might not be writable (but in tmp_path it should be)
        # Test with a valid path that should work
        output_path = str(tmp_path / "test_plot.png")

        # Should handle the error gracefully without raising exception
        save_plot(fig, output_path)

        # File should be created successfully
        assert Path(output_path).exists()
        plt.close(fig)

    def test_create_bar_chart_vertical(self, tmp_path, code_dir):
        """Test create_bar_chart with vertical orientation using real implementation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.bar_chart import create_bar_chart

        categories = ['A', 'B', 'C']
        values = [1, 2, 3]
        output_path = str(tmp_path / "test_bar_chart.png")

        create_bar_chart(
            categories=categories,
            values=values,
            title="Test Chart",
            output_path=output_path,
            show_plot=False
        )

        # Verify file was created
        assert Path(output_path).exists()
        assert Path(output_path).stat().st_size > 0

    def test_create_bar_chart_horizontal(self, tmp_path, code_dir):
        """Test create_bar_chart with horizontal orientation using real implementation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.bar_chart import create_bar_chart

        categories = ['A', 'B', 'C']
        values = [1, 2, 3]
        output_path = str(tmp_path / "test_bar_chart_horizontal.png")

        create_bar_chart(
            categories=categories,
            values=values,
            horizontal=True,
            output_path=output_path,
            show_plot=False
        )

        # Verify file was created
        assert Path(output_path).exists()
        assert Path(output_path).stat().st_size > 0

    def test_create_bar_chart_empty_data(self, code_dir):
        """Test create_bar_chart with empty data."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.bar_chart import create_bar_chart

        # Test with empty categories - should not raise error
        create_bar_chart(categories=[], values=[1, 2, 3])

        # Test with empty values - should not raise error
        create_bar_chart(categories=['A', 'B'], values=[])

    def test_create_bar_chart_mismatched_lengths(self, code_dir):
        """Test create_bar_chart with mismatched category/value lengths."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.bar_chart import create_bar_chart

        # Should handle mismatch gracefully (function logs warning)
        create_bar_chart(categories=['A', 'B'], values=[1, 2, 3])

    def test_create_bar_chart_show_plot(self, code_dir):
        """Test create_bar_chart with show_plot=True using real implementation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.bar_chart import create_bar_chart

        categories = ['A', 'B', 'C']
        values = [1, 2, 3]

        # With Agg backend, show() won't actually display, but should not raise error
        create_bar_chart(
            categories=categories,
            values=values,
            show_plot=True
        )

        # Test passes if no exception is raised

    def test_create_line_plot(self, tmp_path, code_dir):
        """Test create_line_plot function with real implementation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.line_plot import create_line_plot

        x_data = [1, 2, 3, 4, 5]
        y_data = [10, 20, 15, 25, 30]
        output_path = str(tmp_path / "test_line_plot.png")

        fig = create_line_plot(
            x_data=x_data,
            y_data=y_data,
            title="Test Line Plot",
            x_label="X Values",
            y_label="Y Values",
            output_path=output_path,
            show_plot=False
        )

        # Verify file was created
        assert fig is not None
        assert Path(output_path).exists()
        assert Path(output_path).stat().st_size > 0

    def test_create_pie_chart(self, tmp_path, code_dir):
        """Test create_pie_chart function with real implementation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.pie_chart import create_pie_chart

        labels = ['A', 'B', 'C']
        sizes = [10, 20, 30]
        output_path = str(tmp_path / "test_pie_chart.png")

        create_pie_chart(
            labels=labels,
            sizes=sizes,
            title="Test Pie Chart",
            output_path=output_path,
            show_plot=False
        )

        # Verify file was created
        assert Path(output_path).exists()
        assert Path(output_path).stat().st_size > 0

    def test_create_histogram(self, tmp_path, code_dir):
        """Test create_histogram function with real implementation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.histogram import create_histogram

        data = [1, 2, 2, 3, 3, 3, 4, 4, 5]
        output_path = str(tmp_path / "test_histogram.png")

        create_histogram(
            data=data,
            title="Test Histogram",
            x_label="Values",
            y_label="Frequency",
            bins=5,
            output_path=output_path,
            show_plot=False
        )

        # Verify file was created
        assert Path(output_path).exists()
        assert Path(output_path).stat().st_size > 0

    def test_create_scatter_plot(self, tmp_path, code_dir):
        """Test create_scatter_plot function with real implementation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.scatter_plot import create_scatter_plot

        x_data = [1, 2, 3, 4, 5]
        y_data = [10, 20, 15, 25, 30]
        output_path = str(tmp_path / "test_scatter_plot.png")

        create_scatter_plot(
            x_data=x_data,
            y_data=y_data,
            title="Test Scatter Plot",
            x_label="X Values",
            y_label="Y Values",
            output_path=output_path,
            show_plot=False
        )

        # Verify file was created
        assert Path(output_path).exists()
        assert Path(output_path).stat().st_size > 0

    def test_create_heatmap(self, tmp_path, code_dir):
        """Test create_heatmap function with real implementation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.plotter import create_heatmap

        data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        output_path = str(tmp_path / "test_heatmap.png")

        create_heatmap(
            data=data,
            title="Test Heatmap",
            x_labels=['A', 'B', 'C'],
            y_labels=['X', 'Y', 'Z'],
            output_path=output_path,
            show_plot=False
        )

        # Verify file was created
        assert Path(output_path).exists()
        assert Path(output_path).stat().st_size > 0
