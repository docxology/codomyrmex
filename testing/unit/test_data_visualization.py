"""Unit tests for data_visualization module."""

import pytest
import sys
from unittest.mock import patch, MagicMock
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing


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

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.show')
    def test_plot_generation_mock(self, mock_show, mock_savefig, code_dir):
        """Test plot generation with mocked matplotlib."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization import plotter

        # Mock matplotlib functions to avoid actual plot generation
        mock_savefig.return_value = None
        mock_show.return_value = None

        # This is a placeholder test - actual implementation would depend on plotter functions
        assert hasattr(plotter, '__file__')

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

    @patch('codomyrmex.data_visualization.plot_utils.logging.getLogger')
    @patch('codomyrmex.logging_monitoring.logger_config.get_logger')
    def test_get_codomyrmex_logger_with_codomyrmex(self, mock_get_logger, mock_logging_getlogger, code_dir):
        """Test get_codomyrmex_logger when Codomyrmex logging is available."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.plot_utils import get_codomyrmex_logger

        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        result = get_codomyrmex_logger("test_module")

        assert result is mock_logger
        # Check that our specific call was made (it may not be the only call due to module imports)
        mock_get_logger.assert_any_call("test_module")

    @patch('codomyrmex.data_visualization.plot_utils.logging.getLogger')
    @patch('codomyrmex.data_visualization.plot_utils.logging.basicConfig')
    def test_get_codomyrmex_logger_fallback(self, mock_basic_config, mock_get_logger, code_dir):
        """Test get_codomyrmex_logger fallback when Codomyrmex logging is not available."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.plot_utils import get_codomyrmex_logger

        # Mock ImportError for get_logger import
        with patch('codomyrmex.logging_monitoring.logger_config.get_logger', side_effect=ImportError):
            mock_logger = MagicMock()
            mock_logger.hasHandlers.return_value = False
            mock_get_logger.return_value = mock_logger

            result = get_codomyrmex_logger("test_module")

            assert result is mock_logger
            mock_basic_config.assert_called_once()
            mock_logger.info.assert_called_once()

    @patch('os.makedirs')
    def test_save_plot_success(self, mock_makedirs, tmp_path, code_dir):
        """Test save_plot function success."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.plot_utils import save_plot

        mock_fig = MagicMock()
        output_path = str(tmp_path / "test_plot.png")

        save_plot(mock_fig, output_path, dpi=150)

        mock_makedirs.assert_called_once_with(str(tmp_path), exist_ok=True)
        mock_fig.savefig.assert_called_once_with(output_path, dpi=150, bbox_inches='tight')

    def test_save_plot_no_output_path(self, code_dir):
        """Test save_plot function with no output path."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.plot_utils import save_plot

        mock_fig = MagicMock()

        save_plot(mock_fig, "", dpi=150)

        # Should not call savefig when output_path is empty
        mock_fig.savefig.assert_not_called()

    @patch('os.makedirs')
    def test_save_plot_error(self, mock_makedirs, code_dir):
        """Test save_plot function error handling."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.plot_utils import save_plot

        mock_fig = MagicMock()
        mock_fig.savefig.side_effect = OSError("Permission denied")
        output_path = "/invalid/path/test.png"

        # Should handle the error gracefully without raising exception
        save_plot(mock_fig, output_path)

        mock_fig.savefig.assert_called_once()
        # Error should be logged but not raised

    @patch('matplotlib.pyplot.xticks')
    @patch('matplotlib.pyplot.tight_layout')
    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.subplots')
    @patch('codomyrmex.data_visualization.bar_chart.save_plot')
    def test_create_bar_chart_vertical(self, mock_save_plot, mock_subplots, mock_close,
                                     mock_tight_layout, mock_xticks, code_dir):
        """Test create_bar_chart with vertical orientation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.bar_chart import create_bar_chart

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        categories = ['A', 'B', 'C']
        values = [1, 2, 3]

        create_bar_chart(
            categories=categories,
            values=values,
            title="Test Chart",
            output_path="/tmp/test.png",
            show_plot=False
        )

        mock_subplots.assert_called_once()
        mock_ax.bar.assert_called_once_with(categories, values, color='skyblue')
        mock_ax.set_xlabel.assert_called_once_with("Categories")
        mock_ax.set_ylabel.assert_called_once_with("Values")
        mock_ax.set_title.assert_called_once_with("Test Chart")
        mock_save_plot.assert_called_once()
        mock_close.assert_called_once_with(mock_fig)
        mock_xticks.assert_called_once()

    @patch('matplotlib.pyplot.xticks')
    @patch('matplotlib.pyplot.tight_layout')
    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.subplots')
    @patch('codomyrmex.data_visualization.bar_chart.save_plot')
    def test_create_bar_chart_horizontal(self, mock_save_plot, mock_subplots, mock_close,
                                       mock_tight_layout, mock_xticks, code_dir):
        """Test create_bar_chart with horizontal orientation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.bar_chart import create_bar_chart

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        categories = ['A', 'B', 'C']
        values = [1, 2, 3]

        create_bar_chart(
            categories=categories,
            values=values,
            horizontal=True,
            output_path="/tmp/test.png",
            show_plot=False
        )

        mock_ax.barh.assert_called_once_with(categories, values, color='skyblue')
        mock_ax.set_xlabel.assert_called_once_with("Values")
        mock_ax.set_ylabel.assert_called_once_with("Categories")

    def test_create_bar_chart_empty_data(self, code_dir):
        """Test create_bar_chart with empty data."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.bar_chart import create_bar_chart

        # Test with empty categories
        create_bar_chart(categories=[], values=[1, 2, 3])

        # Test with empty values
        create_bar_chart(categories=['A', 'B'], values=[])

    def test_create_bar_chart_mismatched_lengths(self, code_dir):
        """Test create_bar_chart with mismatched category/value lengths."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.bar_chart import create_bar_chart

        create_bar_chart(categories=['A', 'B'], values=[1, 2, 3])

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.subplots')
    @patch('codomyrmex.data_visualization.bar_chart.save_plot')
    def test_create_bar_chart_show_plot(self, mock_save_plot, mock_subplots, mock_close,
                                      mock_show, code_dir):
        """Test create_bar_chart with show_plot=True."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.bar_chart import create_bar_chart

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        categories = ['A', 'B', 'C']
        values = [1, 2, 3]

        create_bar_chart(
            categories=categories,
            values=values,
            show_plot=True
        )

        mock_show.assert_called_once()
        mock_close.assert_not_called()

    @patch('matplotlib.pyplot.xticks')
    @patch('matplotlib.pyplot.tight_layout')
    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.subplots')
    @patch('codomyrmex.data_visualization.line_plot.save_plot')
    def test_create_line_plot(self, mock_save_plot, mock_subplots, mock_close,
                            mock_tight_layout, mock_xticks, code_dir):
        """Test create_line_plot function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.line_plot import create_line_plot

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        x_data = [1, 2, 3, 4, 5]
        y_data = [10, 20, 15, 25, 30]

        create_line_plot(
            x_data=x_data,
            y_data=y_data,
            title="Test Line Plot",
            x_label="X Values",
            y_label="Y Values",
            output_path="/tmp/test.png",
            show_plot=False
        )

        mock_subplots.assert_called_once()
        mock_ax.plot.assert_called_once_with(x_data, y_data, marker=None)
        mock_ax.set_xlabel.assert_called_once_with("X Values", fontsize=12)
        mock_ax.set_ylabel.assert_called_once_with("Y Values", fontsize=12)
        mock_ax.set_title.assert_called_once_with("Test Line Plot", fontsize=16)
        mock_save_plot.assert_called_once()
        mock_close.assert_called_once_with(mock_fig)

    @patch('matplotlib.pyplot.xticks')
    @patch('matplotlib.pyplot.tight_layout')
    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.subplots')
    @patch('codomyrmex.data_visualization.pie_chart.save_plot')
    def test_create_pie_chart(self, mock_save_plot, mock_subplots, mock_close,
                            mock_tight_layout, mock_xticks, code_dir):
        """Test create_pie_chart function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.pie_chart import create_pie_chart

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        labels = ['A', 'B', 'C']
        sizes = [10, 20, 30]

        create_pie_chart(
            labels=labels,
            sizes=sizes,
            title="Test Pie Chart",
            output_path="/tmp/test.png",
            show_plot=False
        )

        mock_subplots.assert_called_once()
        mock_ax.pie.assert_called_once()
        mock_ax.set_title.assert_called_once_with("Test Pie Chart")
        mock_save_plot.assert_called_once()
        mock_close.assert_called_once_with(mock_fig)

    @patch('matplotlib.pyplot.xticks')
    @patch('matplotlib.pyplot.tight_layout')
    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.subplots')
    @patch('codomyrmex.data_visualization.histogram.save_plot')
    def test_create_histogram(self, mock_save_plot, mock_subplots, mock_close,
                            mock_tight_layout, mock_xticks, code_dir):
        """Test create_histogram function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.histogram import create_histogram

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        data = [1, 2, 2, 3, 3, 3, 4, 4, 5]

        create_histogram(
            data=data,
            title="Test Histogram",
            x_label="Values",
            y_label="Frequency",
            bins=5,
            output_path="/tmp/test.png",
            show_plot=False
        )

        mock_subplots.assert_called_once()
        mock_ax.hist.assert_called_once_with(data, bins=5, color='cornflowerblue', edgecolor='black')
        mock_ax.set_xlabel.assert_called_once_with("Values")
        mock_ax.set_ylabel.assert_called_once_with("Frequency")
        mock_ax.set_title.assert_called_once_with("Test Histogram")
        mock_save_plot.assert_called_once()
        mock_close.assert_called_once_with(mock_fig)

    @patch('matplotlib.pyplot.xticks')
    @patch('matplotlib.pyplot.tight_layout')
    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.subplots')
    @patch('codomyrmex.data_visualization.scatter_plot.save_plot')
    def test_create_scatter_plot(self, mock_save_plot, mock_subplots, mock_close,
                               mock_tight_layout, mock_xticks, code_dir):
        """Test create_scatter_plot function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.scatter_plot import create_scatter_plot

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        x_data = [1, 2, 3, 4, 5]
        y_data = [10, 20, 15, 25, 30]

        create_scatter_plot(
            x_data=x_data,
            y_data=y_data,
            title="Test Scatter Plot",
            x_label="X Values",
            y_label="Y Values",
            output_path="/tmp/test.png",
            show_plot=False
        )

        mock_subplots.assert_called_once()
        mock_ax.scatter.assert_called_once_with(x_data, y_data, s=20, c='blue', alpha=0.7)
        mock_ax.set_xlabel.assert_called_once_with("X Values")
        mock_ax.set_ylabel.assert_called_once_with("Y Values")
        mock_ax.set_title.assert_called_once_with("Test Scatter Plot")
        mock_save_plot.assert_called_once()
        mock_close.assert_called_once_with(mock_fig)

    @patch('matplotlib.pyplot.xticks')
    @patch('matplotlib.pyplot.tight_layout')
    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.subplots')
    @patch('codomyrmex.data_visualization.plotter.save_plot')
    def test_create_heatmap(self, mock_save_plot, mock_subplots, mock_close,
                          mock_tight_layout, mock_xticks, code_dir):
        """Test create_heatmap function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.data_visualization.plotter import create_heatmap

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

        create_heatmap(
            data=data,
            title="Test Heatmap",
            x_labels=['A', 'B', 'C'],
            y_labels=['X', 'Y', 'Z'],
            output_path="/tmp/test.png",
            show_plot=False
        )

        mock_subplots.assert_called_once()
        mock_ax.imshow.assert_called_once()
        mock_ax.set_title.assert_called_once_with("Test Heatmap", fontsize=16)
        mock_save_plot.assert_called_once()
        mock_close.assert_called_once_with(mock_fig)

