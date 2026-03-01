"""Unit tests for plot utility functions -- save, aesthetics, color palettes, configuration."""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pytest

# Use non-interactive backend for testing
matplotlib.use('Agg')


# ============================================================================
# TestPlotUtils
# ============================================================================
@pytest.mark.unit
class TestPlotUtils:
    """Test plot utility functions."""

    def test_get_codomyrmex_logger(self):
        """Test functionality: get codomyrmex logger."""
        from codomyrmex.data_visualization.charts.plot_utils import (
            get_codomyrmex_logger,
        )
        logger = get_codomyrmex_logger("test_module")
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')

    def test_save_plot_success(self, tmp_path):
        """Test functionality: save plot success."""
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
        """Test functionality: save plot creates directory."""
        from codomyrmex.data_visualization.charts.plot_utils import save_plot
        fig, ax = plt.subplots()
        ax.plot([1, 2], [3, 4])
        output_path = str(tmp_path / "nested" / "dir" / "plot.png")
        result = save_plot(fig, output_path)
        assert result is True
        assert Path(output_path).exists()
        plt.close(fig)

    def test_save_plot_svg_format(self, tmp_path):
        """Test saving a plot in SVG format (non-PNG alternative).

        Note: originally tested PDF, but matplotlib's PDF backend is fragile
        when 9,000+ tests are collected/imported beforehand. SVG exercises
        the same save_plot code path without the backend fragility.
        """
        from codomyrmex.data_visualization.charts.plot_utils import save_plot
        fig, ax = plt.subplots()
        ax.plot([1, 2], [3, 4])
        output_path = str(tmp_path / "test_save.svg")
        try:
            result = save_plot(fig, output_path)
            assert result is True
            assert Path(output_path).exists()
            assert Path(output_path).stat().st_size > 0
        finally:
            plt.close(fig)

    def test_apply_common_aesthetics(self):
        """Test functionality: apply common aesthetics."""
        from codomyrmex.data_visualization.charts.plot_utils import (
            apply_common_aesthetics,
        )
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
        """Test functionality: get color palette default."""
        from codomyrmex.data_visualization.charts.plot_utils import get_color_palette
        palette = get_color_palette()
        assert len(palette) == 10
        assert all(c.startswith('#') for c in palette)

    def test_get_color_palette_custom_size(self):
        """Test functionality: get color palette custom size."""
        from codomyrmex.data_visualization.charts.plot_utils import get_color_palette
        palette = get_color_palette(5)
        assert len(palette) == 5

    def test_get_color_palette_more_than_base(self):
        """Test functionality: get color palette more than base."""
        from codomyrmex.data_visualization.charts.plot_utils import get_color_palette
        palette = get_color_palette(15)
        assert len(palette) == 15

    def test_configure_plot(self):
        """Test functionality: configure plot."""
        from codomyrmex.data_visualization.charts.plot_utils import configure_plot
        fig, ax = plt.subplots()
        result_fig, result_ax = configure_plot(fig, ax, title="Config Test")
        assert result_fig is fig
        assert result_ax is ax
        assert ax.get_title() == "Config Test"
        plt.close(fig)

    def test_apply_style(self):
        """Test functionality: apply style."""
        from codomyrmex.data_visualization.charts.plot_utils import apply_style
        fig, ax = plt.subplots()
        result = apply_style(ax, "default")
        assert result is ax
        plt.close(fig)



    def test_default_figure_size(self):
        """Test functionality: default figure size."""
        from codomyrmex.data_visualization.charts.plot_utils import DEFAULT_FIGURE_SIZE
        assert DEFAULT_FIGURE_SIZE == (10, 6)
