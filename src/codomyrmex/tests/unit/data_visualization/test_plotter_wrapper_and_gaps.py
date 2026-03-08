"""Targeted zero-mock tests for data_visualization gaps not covered by test_advanced_plotter.py.

Covers:
- engines/plotter.py Plotter wrapper class (all 6 chart methods)
- AdvancedPlotter.finalize_plot with save_path (real file I/O)
- AdvancedPlotter.save_plot failure path (no current_figure)
- AdvancedPlotter.clear_figures full state reset
- AdvancedPlotter._iter_axes iterator (single and multi-subplot)
- AdvancedPlotter._plot_dataset method (LINE/SCATTER/BAR/HISTOGRAM dispatch)
- _scatter.apply_scatter standalone function
- _compat.py PERFORMANCE_MONITORING_AVAILABLE and monitor_performance passthrough
- PlotConfig field mutations and non-default values
- DataPoint and Dataset edge cases (None color, size)
"""

import importlib.util

import pytest

_has_matplotlib = importlib.util.find_spec("matplotlib") is not None
_has_seaborn = importlib.util.find_spec("seaborn") is not None
_has_numpy = importlib.util.find_spec("numpy") is not None
_has_pandas = importlib.util.find_spec("pandas") is not None

pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(
        not (_has_matplotlib and _has_seaborn and _has_numpy and _has_pandas),
        reason="Requires matplotlib, seaborn, numpy, and pandas",
    ),
]

# Force non-interactive backend before any matplotlib import.
if _has_matplotlib:
    import matplotlib as mpl

    mpl.use("Agg")

import matplotlib.pyplot as plt

from codomyrmex.data_visualization.engines._scatter import apply_scatter
from codomyrmex.data_visualization.engines.advanced_plotter import (
    AdvancedPlotter,
    ChartStyle,
    ColorPalette,
    DataPoint,
    Dataset,
    PlotConfig,
    PlotType,
)
from codomyrmex.data_visualization.engines.plotter import Plotter

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _noshow_config(**kwargs) -> PlotConfig:
    """Return a PlotConfig with show_plot=False to avoid Agg backend warnings."""
    kwargs.setdefault("show_plot", False)
    return PlotConfig(**kwargs)


def _sample_plotter(**kwargs) -> AdvancedPlotter:
    return AdvancedPlotter(_noshow_config(**kwargs))


# ---------------------------------------------------------------------------
# Plotter wrapper (engines/plotter.py)
# ---------------------------------------------------------------------------

class TestPlotterWrapperInit:
    """Plotter.__init__ stores figure_size correctly."""

    def test_default_figure_size(self):
        p = Plotter()
        assert isinstance(p.figure_size, tuple)
        assert len(p.figure_size) == 2

    def test_custom_figure_size(self):
        p = Plotter(figure_size=(8, 4))
        assert p.figure_size == (8, 4)


class TestPlotterWrapperBarChart:
    """Plotter.bar_chart delegates to charts.bar_chart.create_bar_chart."""

    def test_bar_chart_returns_figure(self):
        p = Plotter()
        fig = p.bar_chart(["A", "B", "C"], [1, 2, 3])
        assert fig is not None
        plt.close("all")

    def test_bar_chart_uses_default_figure_size(self):
        """figure_size should be injected via setdefault."""
        p = Plotter(figure_size=(5, 3))
        # Just verify it doesn't raise; figure_size is passed through kwargs
        fig = p.bar_chart(["X"], [10])
        assert fig is not None
        plt.close("all")


class TestPlotterWrapperLinePlot:
    """Plotter.line_plot delegates to charts.line_plot.create_line_plot."""

    def test_line_plot_returns_figure(self):
        p = Plotter()
        fig = p.line_plot([1, 2, 3], [4, 5, 6])
        assert fig is not None
        plt.close("all")

    def test_line_plot_custom_figsize(self):
        p = Plotter(figure_size=(6, 2))
        fig = p.line_plot([0, 1], [0, 1])
        assert fig is not None
        plt.close("all")


class TestPlotterWrapperScatterPlot:
    """Plotter.scatter_plot delegates to charts.scatter_plot.create_scatter_plot."""

    def test_scatter_plot_returns_figure(self):
        p = Plotter()
        fig = p.scatter_plot([1, 2, 3], [3, 2, 1])
        assert fig is not None
        plt.close("all")


class TestPlotterWrapperHistogram:
    """Plotter.histogram delegates to charts.histogram.create_histogram."""

    def test_histogram_returns_figure(self):
        p = Plotter()
        data = list(range(50))
        fig = p.histogram(data)
        assert fig is not None
        plt.close("all")


class TestPlotterWrapperPieChart:
    """Plotter.pie_chart delegates to charts.pie_chart.create_pie_chart."""

    def test_pie_chart_returns_figure(self):
        p = Plotter()
        fig = p.pie_chart(["A", "B", "C"], [30, 40, 30])
        assert fig is not None
        plt.close("all")


class TestPlotterWrapperHeatmap:
    """Plotter.heatmap delegates to charts.heatmap.create_heatmap."""

    def test_heatmap_returns_figure(self):
        p = Plotter()
        data = [[1, 2], [3, 4]]
        fig = p.heatmap(data)
        assert fig is not None
        plt.close("all")


# ---------------------------------------------------------------------------
# AdvancedPlotter.finalize_plot with save_path (line 152 in advanced_plotter.py)
# ---------------------------------------------------------------------------

class TestFinalizePlotWithSavePath:
    """finalize_plot(save_path=...) triggers real file save."""

    def test_save_path_creates_file(self, tmp_path):
        p = _sample_plotter()
        p.create_figure()
        p.plot_line([0, 1, 2], [0, 1, 0])
        out = tmp_path / "output.png"
        fig = p.finalize_plot(title="SaveTest", save_path=str(out))
        assert fig is not None
        assert out.exists()
        assert out.stat().st_size > 0

    def test_save_path_png_format(self, tmp_path):
        p = _sample_plotter()
        p.create_figure()
        p.plot_bar(["a", "b"], [1, 2])
        out = tmp_path / "bars.png"
        p.finalize_plot(save_path=str(out))
        assert out.exists()

    def test_save_path_does_not_modify_figure(self, tmp_path):
        p = _sample_plotter()
        p.create_figure()
        p.plot_scatter([1, 2], [3, 4])
        out = tmp_path / "scatter.png"
        fig = p.finalize_plot(save_path=str(out))
        # figure is still accessible after save
        assert p.current_figure is not None


# ---------------------------------------------------------------------------
# AdvancedPlotter.save_plot failure path (no current_figure)
# ---------------------------------------------------------------------------

class TestSavePlotNoFigure:
    """save_plot returns False when current_figure is None."""

    def test_save_returns_false_without_figure(self, tmp_path):
        p = AdvancedPlotter()
        assert p.current_figure is None
        result = p.save_plot(str(tmp_path / "noop.png"))
        assert result is False

    def test_save_succeeds_with_figure(self, tmp_path):
        p = _sample_plotter()
        p.create_figure()
        p.plot_line([1, 2], [3, 4])
        out = tmp_path / "ok.png"
        result = p.save_plot(str(out))
        assert result is True
        assert out.exists()

    def test_save_with_explicit_format(self, tmp_path):
        p = _sample_plotter()
        p.create_figure()
        p.plot_line([1], [1])
        out = tmp_path / "chart.png"
        result = p.save_plot(str(out), format="png", dpi=72)
        assert result is True


# ---------------------------------------------------------------------------
# AdvancedPlotter.clear_figures full state reset
# ---------------------------------------------------------------------------

class TestClearFigures:
    """clear_figures resets all state."""

    def test_clear_empties_figures_list(self):
        p = _sample_plotter()
        p.create_figure()
        p.create_figure()
        assert len(p.figures) == 2
        p.clear_figures()
        assert len(p.figures) == 0

    def test_clear_sets_current_figure_to_none(self):
        p = _sample_plotter()
        p.create_figure()
        assert p.current_figure is not None
        p.clear_figures()
        assert p.current_figure is None

    def test_clear_sets_current_axes_to_none(self):
        p = _sample_plotter()
        p.create_figure()
        assert p.current_axes is not None
        p.clear_figures()
        assert p.current_axes is None

    def test_clear_on_empty_plotter_is_safe(self):
        p = AdvancedPlotter()
        # Should not raise even when nothing to clear
        p.clear_figures()
        assert p.figures == []
        assert p.current_figure is None

    def test_figures_accumulate_before_clear(self):
        p = _sample_plotter()
        for _ in range(4):
            p.create_figure()
        assert len(p.figures) == 4
        p.clear_figures()
        assert p.figures == []


# ---------------------------------------------------------------------------
# AdvancedPlotter._iter_axes iterator
# ---------------------------------------------------------------------------

class TestIterAxes:
    """_iter_axes yields correct axes objects."""

    def test_single_axes_yields_one_item(self):
        p = _sample_plotter()
        p.create_figure(subplots=(1, 1))
        items = list(p._iter_axes())
        assert len(items) == 1

    def test_multi_subplot_yields_all_axes(self):
        p = _sample_plotter()
        p.create_figure(subplots=(2, 3))
        items = list(p._iter_axes())
        assert len(items) == 6

    def test_single_row_multi_col_yields_all(self):
        p = _sample_plotter()
        p.create_figure(subplots=(1, 4))
        items = list(p._iter_axes())
        assert len(items) == 4

    def test_each_item_has_plot_method(self):
        p = _sample_plotter()
        p.create_figure(subplots=(2, 2))
        for ax in p._iter_axes():
            assert hasattr(ax, "plot")

    def test_iter_axes_iterable_branch(self):
        """Axes with __iter__ but not .flat (1D numpy array from (1,N) layout) yields all."""
        p = _sample_plotter()
        p.create_figure(subplots=(1, 3))
        # numpy 1D array has __iter__ but also .flat; force the elif branch by
        # assigning a plain list of axes (has __iter__, no .flat attribute).
        fig, axes = plt.subplots(1, 3)
        plain_list = list(axes)  # list has __iter__ but no .flat
        p.current_axes = plain_list
        items = list(p._iter_axes())
        assert len(items) == 3
        plt.close("all")


# ---------------------------------------------------------------------------
# AdvancedPlotter._plot_dataset dispatch (LINE/SCATTER/BAR/HISTOGRAM)
# ---------------------------------------------------------------------------

class TestPlotDatasetDispatch:
    """_plot_dataset dispatches to the correct matplotlib call for each PlotType."""

    def _make_points(self, n=5):
        return [DataPoint(x=float(i), y=float(i * 2)) for i in range(n)]

    def test_line_dataset_dispatches_to_plot(self):
        p = _sample_plotter()
        p.create_figure()
        ax = next(iter(p._iter_axes()))
        ds = Dataset(
            name="line",
            data=self._make_points(),
            plot_type=PlotType.LINE,
            label="L",
            color="blue",
        )
        before = len(ax.lines)
        p._plot_dataset(ax, ds)
        assert len(ax.lines) > before

    def test_scatter_dataset_dispatches_to_scatter(self):
        p = _sample_plotter()
        p.create_figure()
        ax = next(iter(p._iter_axes()))
        ds = Dataset(
            name="scatter",
            data=self._make_points(),
            plot_type=PlotType.SCATTER,
            label="S",
            color="red",
        )
        before = len(ax.collections)
        p._plot_dataset(ax, ds)
        assert len(ax.collections) > before

    def test_bar_dataset_dispatches_to_bar(self):
        p = _sample_plotter()
        p.create_figure()
        ax = next(iter(p._iter_axes()))
        ds = Dataset(
            name="bar",
            data=self._make_points(),
            plot_type=PlotType.BAR,
            label="B",
            color="green",
        )
        before = len(ax.patches)
        p._plot_dataset(ax, ds)
        assert len(ax.patches) > before

    def test_histogram_dataset_dispatches_to_hist(self):
        p = _sample_plotter()
        p.create_figure()
        ax = next(iter(p._iter_axes()))
        ds = Dataset(
            name="hist",
            data=self._make_points(10),
            plot_type=PlotType.HISTOGRAM,
            label="H",
        )
        before = len(ax.patches)
        p._plot_dataset(ax, ds)
        assert len(ax.patches) > before

    def test_dataset_without_label_no_legend(self):
        """Dataset with no label — legend() should not be called (no assertion error)."""
        p = _sample_plotter()
        p.create_figure()
        ax = next(iter(p._iter_axes()))
        ds = Dataset(
            name="unlabeled",
            data=self._make_points(),
            plot_type=PlotType.LINE,
        )
        # Should not raise
        p._plot_dataset(ax, ds)

    def test_scatter_per_point_color_and_size(self):
        """Per-point color and size in DataPoint are used for SCATTER dispatch."""
        p = _sample_plotter()
        p.create_figure()
        ax = next(iter(p._iter_axes()))
        points = [
            DataPoint(x=1.0, y=2.0, color="red", size=100.0),
            DataPoint(x=2.0, y=3.0, color="blue", size=200.0),
        ]
        ds = Dataset(name="pts", data=points, plot_type=PlotType.SCATTER)
        p._plot_dataset(ax, ds)
        assert len(ax.collections) >= 1

    def test_scatter_no_per_point_color_uses_dataset_color(self):
        """When DataPoint.color is None, dataset.color is used as fallback."""
        p = _sample_plotter()
        p.create_figure()
        ax = next(iter(p._iter_axes()))
        points = [DataPoint(x=float(i), y=float(i)) for i in range(3)]
        ds = Dataset(name="fallback", data=points, plot_type=PlotType.SCATTER, color="purple")
        p._plot_dataset(ax, ds)
        assert len(ax.collections) >= 1


# ---------------------------------------------------------------------------
# _scatter.apply_scatter standalone function
# ---------------------------------------------------------------------------

class TestApplyScatterStandalone:
    """apply_scatter is a standalone delegate function in _scatter.py."""

    def test_apply_scatter_returns_path_collection(self):
        fig, ax = plt.subplots()
        result = apply_scatter(ax, [1, 2, 3], [4, 5, 6])
        # PathCollection from ax.scatter
        from matplotlib.collections import PathCollection
        assert isinstance(result, PathCollection)
        plt.close(fig)

    def test_apply_scatter_with_kwargs(self):
        fig, ax = plt.subplots()
        result = apply_scatter(ax, [0, 1], [0, 1], s=100, c="red", alpha=0.5)
        assert result is not None
        plt.close(fig)

    def test_apply_scatter_single_point(self):
        fig, ax = plt.subplots()
        result = apply_scatter(ax, [5], [10])
        assert result is not None
        assert len(result.get_offsets()) == 1
        plt.close(fig)


# ---------------------------------------------------------------------------
# _compat.py PERFORMANCE_MONITORING_AVAILABLE and stubs
# ---------------------------------------------------------------------------

class TestCompatModule:
    """_compat exports the correct interface regardless of performance install state."""

    def test_performance_monitoring_available_is_bool(self):
        from codomyrmex.data_visualization._compat import (
            PERFORMANCE_MONITORING_AVAILABLE,
        )
        assert isinstance(PERFORMANCE_MONITORING_AVAILABLE, bool)

    def test_monitor_performance_is_callable(self):
        from codomyrmex.data_visualization._compat import monitor_performance
        assert callable(monitor_performance)

    def test_monitor_performance_decorator_passes_return_value(self):
        from codomyrmex.data_visualization._compat import monitor_performance

        @monitor_performance("test_op")
        def compute(x):
            return x * 2

        result = compute(7)
        assert result == 14

    def test_monitor_performance_decorator_passes_multiple_args(self):
        from codomyrmex.data_visualization._compat import monitor_performance

        @monitor_performance("add")
        def add(a, b):
            return a + b

        assert add(3, 4) == 7

    def test_performance_context_is_callable(self):
        from codomyrmex.data_visualization._compat import performance_context
        assert callable(performance_context)

    def test_performance_context_enters_and_exits(self):
        from codomyrmex.data_visualization._compat import performance_context
        with performance_context("my_op"):
            pass  # must not raise

    def test_performance_context_as_context_manager(self):
        """performance_context works as a context manager without raising."""
        from codomyrmex.data_visualization._compat import performance_context
        entered = False
        with performance_context("op"):
            entered = True
        assert entered

    def test_compat_all_exports(self):
        import codomyrmex.data_visualization._compat as compat
        for name in ["PERFORMANCE_MONITORING_AVAILABLE", "monitor_performance", "performance_context"]:
            assert hasattr(compat, name)


# ---------------------------------------------------------------------------
# PlotConfig edge cases
# ---------------------------------------------------------------------------

class TestPlotConfigEdgeCases:
    """PlotConfig field mutations and non-default values."""

    def test_config_with_all_non_defaults(self):
        cfg = PlotConfig(
            title="T",
            xlabel="X",
            ylabel="Y",
            figsize=(5, 5),
            dpi=72,
            style=ChartStyle.DARK,
            palette=ColorPalette.INFERNO,
            grid=False,
            legend=False,
            tight_layout=False,
            save_format="svg",
            save_dpi=150,
            show_plot=False,
            transparent=True,
            bbox_inches="standard",
        )
        assert cfg.title == "T"
        assert cfg.dpi == 72
        assert cfg.style == ChartStyle.DARK
        assert cfg.palette == ColorPalette.INFERNO
        assert cfg.grid is False
        assert cfg.transparent is True

    def test_config_mutable_after_creation(self):
        cfg = PlotConfig()
        cfg.title = "Mutated"
        cfg.dpi = 150
        assert cfg.title == "Mutated"
        assert cfg.dpi == 150

    @pytest.mark.parametrize("style", list(ChartStyle))
    def test_all_chart_styles_valid(self, style):
        cfg = PlotConfig(style=style, show_plot=False)
        p = AdvancedPlotter(cfg)
        p._setup_style()  # must not raise

    @pytest.mark.parametrize("palette", list(ColorPalette))
    def test_all_color_palettes_valid(self, palette):
        cfg = PlotConfig(palette=palette, show_plot=False)
        p = AdvancedPlotter(cfg)
        colors = p._get_color_palette(4)
        assert len(colors) == 4


# ---------------------------------------------------------------------------
# DataPoint and Dataset edge cases
# ---------------------------------------------------------------------------

class TestDataPointEdgeCases:
    """DataPoint with optional None fields and datetime x/y."""

    def test_data_point_none_color_and_size(self):
        dp = DataPoint(x=1.0, y=2.0, color=None, size=None)
        assert dp.color is None
        assert dp.size is None

    def test_data_point_string_x_y(self):
        dp = DataPoint(x="Jan", y="Feb")
        assert dp.x == "Jan"
        assert dp.y == "Feb"

    def test_data_point_alpha_default(self):
        dp = DataPoint(x=0, y=0)
        assert dp.alpha == 1.0

    def test_data_point_custom_label(self):
        dp = DataPoint(x=1, y=2, label="point1")
        assert dp.label == "point1"


class TestDatasetEdgeCases:
    """Dataset field defaults and mutations."""

    def test_dataset_default_alpha(self):
        ds = Dataset(name="d", data=[], plot_type=PlotType.LINE)
        assert ds.alpha == 1.0

    def test_dataset_default_linewidth(self):
        ds = Dataset(name="d", data=[], plot_type=PlotType.LINE)
        assert ds.linewidth == 2.0

    def test_dataset_default_markersize(self):
        ds = Dataset(name="d", data=[], plot_type=PlotType.SCATTER)
        assert ds.markersize == 6.0

    def test_dataset_all_plot_types_accepted(self):
        for pt in PlotType:
            ds = Dataset(name="d", data=[], plot_type=pt)
            assert ds.plot_type == pt


# ---------------------------------------------------------------------------
# AdvancedPlotter state consistency after multiple plots
# ---------------------------------------------------------------------------

class TestAdvancedPlotterStateConsistency:
    """State tracking (figures list, current_figure) is correct across multiple ops."""

    def test_figures_list_grows_with_each_create(self):
        p = _sample_plotter()
        assert len(p.figures) == 0
        p.create_figure()
        assert len(p.figures) == 1
        p.create_figure()
        assert len(p.figures) == 2

    def test_current_figure_is_last_created(self):
        p = _sample_plotter()
        fig1, _ = p.create_figure()
        fig2, _ = p.create_figure()
        assert p.current_figure is fig2

    def test_plot_line_without_pre_created_figure(self):
        """plot_line auto-creates figure when current_axes is None."""
        p = _sample_plotter()
        assert p.current_axes is None
        p.plot_line([1, 2, 3], [4, 5, 6])
        assert p.current_axes is not None
        assert len(p.figures) == 1

    def test_plot_bar_without_pre_created_figure(self):
        p = _sample_plotter()
        p.plot_bar(["a", "b"], [1, 2])
        assert p.current_axes is not None

    def test_plot_scatter_without_pre_created_figure(self):
        p = _sample_plotter()
        p.plot_scatter([1, 2], [3, 4])
        assert p.current_axes is not None

    def test_plot_histogram_without_pre_created_figure(self):
        p = _sample_plotter()
        p.plot_histogram([1.0, 2.0, 3.0, 4.0])
        assert p.current_axes is not None

    def test_finalize_raises_without_figure(self):
        p = AdvancedPlotter()
        with pytest.raises(ValueError, match="No current figure"):
            p.finalize_plot()


# ---------------------------------------------------------------------------
# finalize_plot label/legend/grid override logic
# ---------------------------------------------------------------------------

class TestFinalizePlotOverrides:
    """finalize_plot respects explicit args over config defaults."""

    def test_explicit_grid_true_overrides_config_false(self):
        cfg = _noshow_config(grid=False)
        p = AdvancedPlotter(cfg)
        p.create_figure()
        p.plot_line([1, 2], [3, 4])
        fig = p.finalize_plot(grid=True)
        assert fig is not None

    def test_explicit_legend_false_overrides_config_true(self):
        cfg = _noshow_config(legend=True)
        p = AdvancedPlotter(cfg)
        p.create_figure()
        p.plot_line([1, 2], [3, 4], label="my line")
        fig = p.finalize_plot(legend=False)
        assert fig is not None

    def test_explicit_xlabel_ylabel(self):
        p = _sample_plotter()
        p.create_figure()
        p.plot_line([1, 2], [3, 4])
        fig = p.finalize_plot(xlabel="Time", ylabel="Value")
        ax = next(iter(p._iter_axes()))
        assert ax.get_xlabel() == "Time"
        assert ax.get_ylabel() == "Value"


# ---------------------------------------------------------------------------
# save_plot with bad path (OSError path)
# ---------------------------------------------------------------------------

class TestSavePlotErrorPath:
    """save_plot returns False on OSError (bad path)."""

    def test_save_to_invalid_directory_returns_false(self):
        p = _sample_plotter()
        p.create_figure()
        p.plot_line([1], [1])
        # Path into a non-existent deep directory
        result = p.save_plot("/nonexistent/deep/dir/chart.png")
        assert result is False

    def test_save_succeeds_with_svg_format(self, tmp_path):
        p = _sample_plotter()
        p.create_figure()
        p.plot_line([0, 1], [0, 1])
        out = tmp_path / "chart.svg"
        result = p.save_plot(str(out), format="svg")
        assert result is True
        assert out.exists()
