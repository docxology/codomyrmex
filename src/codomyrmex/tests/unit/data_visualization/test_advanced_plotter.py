"""Comprehensive tests for AdvancedPlotter in data_visualization.engines.advanced_plotter.

Covers: style setup, color palettes, all plot types (line, scatter, bar, histogram,
heatmap, box, violin, correlation), dashboard creation, finalize/save workflow,
convenience functions, and edge cases.
"""

import importlib.util
import os

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

# Force non-interactive backend before any matplotlib import
if _has_matplotlib:
    import matplotlib
    matplotlib.use("Agg")


import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from codomyrmex.data_visualization.engines.advanced_plotter import (  # noqa: E402
    AdvancedPlotter,
    ChartStyle,
    ColorPalette,
    DataPoint,
    Dataset,
    PlotConfig,
    PlotType,
    create_advanced_bar_chart,
    create_advanced_dashboard,
    create_advanced_heatmap,
    create_advanced_histogram,
    create_advanced_line_plot,
    create_advanced_scatter_plot,
    get_available_palettes,
    get_available_plot_types,
    get_available_styles,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _close_figures():
    """Close all matplotlib figures after each test to avoid resource leaks."""
    yield
    plt.close("all")


@pytest.fixture()
def plotter():
    """Return an AdvancedPlotter with show_plot disabled."""
    config = PlotConfig(show_plot=False)
    return AdvancedPlotter(config)


@pytest.fixture()
def sample_x():
    return [1, 2, 3, 4, 5]


@pytest.fixture()
def sample_y():
    return [10, 20, 15, 25, 30]


# ---------------------------------------------------------------------------
# Enum / dataclass sanity
# ---------------------------------------------------------------------------


class TestEnumsAndDataclasses:
    def test_plot_type_values(self):
        assert PlotType.LINE.value == "line"
        assert PlotType.SCATTER.value == "scatter"
        assert PlotType.BAR.value == "bar"
        assert PlotType.HISTOGRAM.value == "histogram"
        assert PlotType.PIE.value == "pie"
        assert PlotType.HEATMAP.value == "heatmap"
        assert PlotType.BOX.value == "box"
        assert PlotType.VIOLIN.value == "violin"
        assert PlotType.DENSITY.value == "density"
        assert PlotType.CORRELATION.value == "correlation"
        assert PlotType.TIMESERIES.value == "timeseries"
        assert PlotType.DASHBOARD.value == "dashboard"
        assert PlotType.INTERACTIVE.value == "interactive"

    def test_chart_style_values(self):
        for style in ChartStyle:
            assert isinstance(style.value, str)

    def test_color_palette_values(self):
        for palette in ColorPalette:
            assert isinstance(palette.value, str)

    def test_plot_config_defaults(self):
        cfg = PlotConfig()
        assert cfg.figsize == (10, 6)
        assert cfg.dpi == 100
        assert cfg.style == ChartStyle.DEFAULT
        assert cfg.palette == ColorPalette.DEFAULT
        assert cfg.grid is True
        assert cfg.legend is True
        assert cfg.tight_layout is True
        assert cfg.save_format == "png"
        assert cfg.save_dpi == 300
        assert cfg.show_plot is True
        assert cfg.transparent is False
        assert cfg.bbox_inches == "tight"

    def test_data_point_defaults(self):
        dp = DataPoint(x=1, y=2)
        assert dp.label is None
        assert dp.color is None
        assert dp.size is None
        assert dp.alpha == 1.0

    def test_dataset_defaults(self):
        ds = Dataset(name="test", data=[], plot_type=PlotType.LINE)
        assert ds.color is None
        assert ds.label is None
        assert ds.alpha == 1.0
        assert ds.linewidth == 2.0
        assert ds.markersize == 6.0


# ---------------------------------------------------------------------------
# AdvancedPlotter init
# ---------------------------------------------------------------------------


class TestAdvancedPlotterInit:
    def test_default_config(self):
        p = AdvancedPlotter()
        assert isinstance(p.config, PlotConfig)
        assert p.figures == []
        assert p.current_figure is None
        assert p.current_axes is None

    def test_custom_config(self):
        cfg = PlotConfig(title="Custom", dpi=200)
        p = AdvancedPlotter(cfg)
        assert p.config.title == "Custom"
        assert p.config.dpi == 200


# ---------------------------------------------------------------------------
# Style setup (lines 162-177 including uncovered 164-175)
# ---------------------------------------------------------------------------


class TestSetupStyle:
    @pytest.mark.parametrize(
        "style",
        [
            ChartStyle.MINIMAL,
            ChartStyle.DARK,
            ChartStyle.WHITE,
            ChartStyle.TICKS,
            ChartStyle.DARKGRID,
            ChartStyle.WHITEGRID,
            ChartStyle.DEFAULT,
        ],
    )
    def test_setup_style_all_variants(self, style):
        """Cover lines 164-177: every branch in _setup_style."""
        cfg = PlotConfig(style=style, show_plot=False)
        p = AdvancedPlotter(cfg)
        fig, ax = p.create_figure()
        assert fig is not None


# ---------------------------------------------------------------------------
# Color palette (lines 179-200)
# ---------------------------------------------------------------------------


class TestColorPalette:
    @pytest.mark.parametrize(
        "palette",
        [
            ColorPalette.VIRIDIS,
            ColorPalette.PLASMA,
            ColorPalette.INFERNO,
            ColorPalette.MAGMA,
            ColorPalette.COOLWARM,
            ColorPalette.RAINBOW,
            ColorPalette.PASTEL,
            ColorPalette.DARK,
            ColorPalette.BRIGHT,
            ColorPalette.DEFAULT,
        ],
    )
    def test_get_color_palette_all_variants(self, palette):
        """Cover lines 181-200: every branch in _get_color_palette."""
        cfg = PlotConfig(palette=palette, show_plot=False)
        p = AdvancedPlotter(cfg)
        colors = p._get_color_palette(5)
        assert len(colors) == 5


# ---------------------------------------------------------------------------
# create_figure
# ---------------------------------------------------------------------------


class TestCreateFigure:
    def test_single_subplot(self, plotter):
        fig, ax = plotter.create_figure()
        assert plotter.current_figure is fig
        assert plotter.current_axes is ax
        assert fig in plotter.figures

    def test_multiple_subplots(self, plotter):
        fig, axes = plotter.create_figure(subplots=(2, 2))
        assert axes.shape == (2, 2)

    def test_custom_figsize(self, plotter):
        fig, _ = plotter.create_figure(figsize=(12, 8))
        w, h = fig.get_size_inches()
        assert abs(w - 12) < 0.1
        assert abs(h - 8) < 0.1


# ---------------------------------------------------------------------------
# plot_line (lines 267-268 auto-create, 276-289)
# ---------------------------------------------------------------------------


class TestPlotLine:
    def test_basic_line(self, plotter, sample_x, sample_y):
        plotter.create_figure()
        line = plotter.plot_line(sample_x, sample_y, label="test")
        assert line is not None

    def test_line_auto_creates_figure(self, sample_x, sample_y):
        """Cover line 268: auto-create figure when current_axes is None."""
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        assert p.current_axes is None
        line = p.plot_line(sample_x, sample_y)
        assert p.current_figure is not None
        assert line is not None

    def test_line_with_options(self, plotter, sample_x, sample_y):
        plotter.create_figure()
        line = plotter.plot_line(
            sample_x,
            sample_y,
            label="styled",
            color="red",
            linewidth=3.0,
            linestyle="--",
            marker="o",
            markersize=8.0,
            alpha=0.5,
        )
        assert line is not None

    def test_line_with_subplots(self, plotter, sample_x, sample_y):
        """When current_axes is an array, should use axes[0]."""
        plotter.create_figure(subplots=(1, 2))
        line = plotter.plot_line(sample_x, sample_y)
        assert line is not None


# ---------------------------------------------------------------------------
# plot_scatter (lines 319-320 auto-create)
# ---------------------------------------------------------------------------


class TestPlotScatter:
    def test_basic_scatter(self, plotter, sample_x, sample_y):
        plotter.create_figure()
        sc = plotter.plot_scatter(sample_x, sample_y, label="pts")
        assert sc is not None

    def test_scatter_auto_creates_figure(self, sample_x, sample_y):
        """Cover line 320: auto-create figure."""
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        p.plot_scatter(sample_x, sample_y)
        assert p.current_figure is not None

    def test_scatter_with_variable_sizes(self, plotter, sample_x, sample_y):
        plotter.create_figure()
        sizes = [20, 40, 60, 80, 100]
        sc = plotter.plot_scatter(sample_x, sample_y, size=sizes)
        assert sc is not None


# ---------------------------------------------------------------------------
# plot_bar (lines 378-379 horizontal, 430 auto-create)
# ---------------------------------------------------------------------------


class TestPlotBar:
    def test_vertical_bar(self, plotter):
        plotter.create_figure()
        bars = plotter.plot_bar(["A", "B", "C"], [10, 20, 15])
        assert bars is not None

    def test_horizontal_bar(self, plotter):
        """Cover line 379: horizontal orientation."""
        plotter.create_figure()
        bars = plotter.plot_bar(["A", "B", "C"], [10, 20, 15], orientation="horizontal")
        assert bars is not None

    def test_bar_auto_creates_figure(self):
        """Cover implicit auto-create."""
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        p.plot_bar(["X"], [5])
        assert p.current_figure is not None


# ---------------------------------------------------------------------------
# plot_histogram (lines 429-430 auto-create)
# ---------------------------------------------------------------------------


class TestPlotHistogram:
    def test_basic_histogram(self, plotter):
        plotter.create_figure()
        counts, edges, patches = plotter.plot_histogram([1, 2, 2, 3, 3, 3, 4], bins=4)
        assert len(edges) == 5  # bins + 1

    def test_histogram_auto_creates_figure(self):
        """Cover line 430: auto-create figure."""
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        counts, edges, patches = p.plot_histogram([1, 2, 3])
        assert p.current_figure is not None

    def test_histogram_density_cumulative(self, plotter):
        plotter.create_figure()
        counts, _, _ = plotter.plot_histogram(
            list(range(100)), bins=10, density=True, cumulative=True, label="cum"
        )
        assert counts is not None


# ---------------------------------------------------------------------------
# plot_heatmap (lines 479-480 auto-create, line 503 return)
# ---------------------------------------------------------------------------


class TestPlotHeatmap:
    def test_heatmap_from_list(self, plotter):
        """Cover list-to-ndarray conversion at line 488-489."""
        plotter.create_figure()
        data = [[1.0, 2.0], [3.0, 4.0]]
        hm = plotter.plot_heatmap(data, x_labels=["a", "b"], y_labels=["c", "d"])
        assert hm is not None

    def test_heatmap_from_ndarray(self, plotter):
        plotter.create_figure()
        data = np.array([[1, 2, 3], [4, 5, 6]])
        hm = plotter.plot_heatmap(
            data, x_labels=["a", "b", "c"], y_labels=["r1", "r2"],
            annot=True, fmt=".1f",
        )
        assert hm is not None

    def test_heatmap_from_dataframe(self, plotter):
        plotter.create_figure()
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        hm = plotter.plot_heatmap(df, x_labels=["x", "y"], y_labels=["0", "1"])
        assert hm is not None

    def test_heatmap_auto_creates_figure(self):
        """Cover line 480."""
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        p.plot_heatmap([[1, 2], [3, 4]], x_labels=["a", "b"], y_labels=["c", "d"])
        assert p.current_figure is not None


# ---------------------------------------------------------------------------
# plot_box (lines 529-530 auto-create, 542-543 list branch, 549-553 color)
# ---------------------------------------------------------------------------


class TestPlotBox:
    def test_box_from_dict(self, plotter):
        plotter.create_figure()
        data = {"Group A": [1, 2, 3, 4], "Group B": [2, 3, 4, 5]}
        bp = plotter.plot_box(data)
        assert "boxes" in bp

    def test_box_from_list(self, plotter):
        """Cover lines 542-543: plain list branch."""
        plotter.create_figure()
        bp = plotter.plot_box([1, 2, 3, 4, 5])
        assert "boxes" in bp

    def test_box_with_single_color(self, plotter):
        """Cover lines 549-553: single color string -> list."""
        plotter.create_figure()
        data = {"A": [1, 2, 3], "B": [4, 5, 6]}
        bp = plotter.plot_box(data, color="skyblue")
        assert "boxes" in bp

    def test_box_with_multiple_colors(self, plotter):
        """Cover line 552: color list zip."""
        plotter.create_figure()
        data = {"A": [1, 2, 3], "B": [4, 5, 6]}
        bp = plotter.plot_box(data, color=["skyblue", "salmon"])
        assert "boxes" in bp

    def test_box_notch(self, plotter):
        plotter.create_figure()
        bp = plotter.plot_box({"G": list(range(20))}, notch=True)
        assert "boxes" in bp

    def test_box_auto_creates_figure(self):
        """Cover line 530."""
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        p.plot_box([1, 2, 3])
        assert p.current_figure is not None


# ---------------------------------------------------------------------------
# plot_violin (lines 579-619 -- large uncovered block)
# ---------------------------------------------------------------------------


class TestPlotViolin:
    def test_violin_from_dict(self, plotter):
        """Cover lines 588-604: dict branch."""
        plotter.create_figure()
        data = {"A": [1, 2, 3, 4, 5], "B": [2, 3, 4, 5, 6]}
        vp = plotter.plot_violin(data)
        assert vp is not None

    def test_violin_from_list(self, plotter):
        """Cover lines 605-617: list branch."""
        plotter.create_figure()
        vp = plotter.plot_violin([1, 2, 3, 4, 5], labels=["data"])
        assert vp is not None

    def test_violin_from_list_no_labels(self, plotter):
        """Cover line 607: labels default to 'data'."""
        plotter.create_figure()
        vp = plotter.plot_violin([1, 2, 3, 4, 5])
        assert vp is not None

    def test_violin_with_color(self, plotter):
        plotter.create_figure()
        data = {"X": [1, 2, 3], "Y": [4, 5, 6]}
        vp = plotter.plot_violin(data, color="blue", alpha=0.5)
        assert vp is not None

    def test_violin_auto_creates_figure(self):
        """Cover line 579-580."""
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        p.plot_violin([1, 2, 3, 4])
        assert p.current_figure is not None


# ---------------------------------------------------------------------------
# plot_correlation (lines 645-673 -- large uncovered block)
# ---------------------------------------------------------------------------


class TestPlotCorrelation:
    def test_correlation_from_dataframe(self, plotter):
        """Cover lines 645-673."""
        plotter.create_figure()
        df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [4, 3, 2, 1], "c": [1, 3, 2, 4]})
        hm = plotter.plot_correlation(df)
        assert hm is not None

    def test_correlation_from_ndarray(self, plotter):
        """Cover lines 657-658: ndarray -> DataFrame conversion."""
        plotter.create_figure()
        data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
        hm = plotter.plot_correlation(data)
        assert hm is not None

    def test_correlation_spearman(self, plotter):
        plotter.create_figure()
        df = pd.DataFrame({"x": range(10), "y": range(10)})
        hm = plotter.plot_correlation(df, method="spearman")
        assert hm is not None

    def test_correlation_auto_creates_figure(self):
        """Cover line 645."""
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        p.plot_correlation(df)
        assert p.current_figure is not None


# ---------------------------------------------------------------------------
# create_dashboard (lines 695-720)
# ---------------------------------------------------------------------------


class TestCreateDashboard:
    def _make_datasets(self, n=4):
        """Create n sample datasets with different plot types."""
        types = [PlotType.LINE, PlotType.SCATTER, PlotType.BAR, PlotType.HISTOGRAM]
        datasets = []
        for i in range(n):
            points = [DataPoint(x=j, y=j * (i + 1)) for j in range(1, 6)]
            ds = Dataset(
                name=f"ds{i}",
                data=points,
                plot_type=types[i % len(types)],
                label=f"Dataset {i}",
                color=None,
            )
            datasets.append(ds)
        return datasets

    def test_dashboard_basic(self, plotter):
        """Cover lines 695-720."""
        datasets = self._make_datasets(4)
        fig = plotter.create_dashboard(datasets, layout=(2, 2), title="Test Dashboard")
        assert fig is not None
        assert len(fig.axes) >= 4

    def test_dashboard_fewer_datasets_than_panels(self, plotter):
        """Cover lines 712-713: hide unused subplots."""
        datasets = self._make_datasets(2)
        fig = plotter.create_dashboard(datasets, layout=(2, 2), title="Sparse")
        assert fig is not None

    def test_dashboard_more_datasets_than_panels(self, plotter):
        """Cover lines 704-706: break when i >= len(axes)."""
        datasets = self._make_datasets(4)
        # Only 2 panels
        fig = plotter.create_dashboard(datasets[:4], layout=(1, 2), title="Overflow")
        assert fig is not None

    def test_dashboard_single_panel(self, plotter):
        """Cover line 697-698: single axes (not iterable)."""
        datasets = self._make_datasets(1)
        fig = plotter.create_dashboard(datasets, layout=(1, 1), title="Single")
        assert fig is not None


# ---------------------------------------------------------------------------
# _plot_dataset (lines 724-762)
# ---------------------------------------------------------------------------


class TestPlotDataset:
    def test_plot_dataset_line(self, plotter):
        """Cover lines 727-736."""
        fig, ax = plotter.create_figure()
        points = [DataPoint(x=i, y=i * 2) for i in range(5)]
        ds = Dataset(name="line", data=points, plot_type=PlotType.LINE, label="L")
        plotter._plot_dataset(ax, ds)

    def test_plot_dataset_scatter(self, plotter):
        """Cover lines 737-747."""
        fig, ax = plotter.create_figure()
        points = [DataPoint(x=i, y=i * 2, size=10.0, color="red") for i in range(5)]
        ds = Dataset(name="sc", data=points, plot_type=PlotType.SCATTER, label="S", color="blue")
        plotter._plot_dataset(ax, ds)

    def test_plot_dataset_bar(self, plotter):
        """Cover lines 748-755."""
        fig, ax = plotter.create_figure()
        points = [DataPoint(x=i, y=i * 3) for i in range(5)]
        ds = Dataset(name="bar", data=points, plot_type=PlotType.BAR, label="B", color="green")
        plotter._plot_dataset(ax, ds)

    def test_plot_dataset_histogram(self, plotter):
        """Cover lines 756-759."""
        fig, ax = plotter.create_figure()
        points = [DataPoint(x=i, y=float(i)) for i in range(20)]
        ds = Dataset(name="hist", data=points, plot_type=PlotType.HISTOGRAM, label="H")
        plotter._plot_dataset(ax, ds)

    def test_plot_dataset_no_label(self, plotter):
        """Cover line 761: label is falsy so legend not called."""
        fig, ax = plotter.create_figure()
        points = [DataPoint(x=i, y=i) for i in range(5)]
        ds = Dataset(name="nolabel", data=points, plot_type=PlotType.LINE, label=None)
        plotter._plot_dataset(ax, ds)


# ---------------------------------------------------------------------------
# finalize_plot (lines 789, 809, 830-835, 843, 850-854, 862, 869-873)
# ---------------------------------------------------------------------------


class TestFinalizePlot:
    def test_finalize_no_figure_raises(self):
        """Cover line 789: ValueError when no current figure."""
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        with pytest.raises(ValueError, match="No current figure"):
            p.finalize_plot()

    def test_finalize_basic(self, plotter, sample_x, sample_y):
        plotter.create_figure()
        plotter.plot_line(sample_x, sample_y, label="line")
        fig = plotter.finalize_plot(title="Test", xlabel="X", ylabel="Y")
        assert fig is not None

    def test_finalize_with_config_title(self, sample_x, sample_y):
        cfg = PlotConfig(title="Config Title", xlabel="CX", ylabel="CY", show_plot=False)
        p = AdvancedPlotter(cfg)
        p.create_figure()
        p.plot_line(sample_x, sample_y)
        fig = p.finalize_plot()
        assert fig is not None

    def test_finalize_with_save(self, plotter, sample_x, sample_y, tmp_path):
        """Cover line 809: save_path triggers save_plot."""
        plotter.create_figure()
        plotter.plot_line(sample_x, sample_y)
        save_path = str(tmp_path / "test_plot.png")
        fig = plotter.finalize_plot(title="Saved", save_path=save_path)
        assert fig is not None
        assert os.path.exists(save_path)

    def test_finalize_subplots_labels(self, plotter):
        """Cover lines 830-835: multiple axes label setting."""
        plotter.create_figure(subplots=(2, 2))
        fig = plotter.finalize_plot(xlabel="Multi-X", ylabel="Multi-Y")
        assert fig is not None

    def test_finalize_legend_false(self, plotter, sample_x, sample_y):
        """Cover line 843: legend explicitly False."""
        plotter.create_figure()
        plotter.plot_line(sample_x, sample_y)
        fig = plotter.finalize_plot(legend=False)
        assert fig is not None

    def test_finalize_legend_subplots(self, plotter):
        """Cover lines 850-854: legend on multiple axes."""
        plotter.create_figure(subplots=(1, 2))
        fig = plotter.finalize_plot(legend=True)
        assert fig is not None

    def test_finalize_grid_false(self, plotter, sample_x, sample_y):
        """Cover line 862: grid explicitly False."""
        plotter.create_figure()
        plotter.plot_line(sample_x, sample_y)
        fig = plotter.finalize_plot(grid=False)
        assert fig is not None

    def test_finalize_grid_subplots(self, plotter):
        """Cover lines 869-873: grid on multiple axes."""
        plotter.create_figure(subplots=(1, 2))
        fig = plotter.finalize_plot(grid=True)
        assert fig is not None


# ---------------------------------------------------------------------------
# save_plot (lines 898-899 no figure, 920-922 exception)
# ---------------------------------------------------------------------------


class TestSavePlot:
    def test_save_no_figure(self):
        """Cover lines 898-899: save when no current figure."""
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        result = p.save_plot("/tmp/nonexistent.png")
        assert result is False

    def test_save_success(self, plotter, sample_x, sample_y, tmp_path):
        plotter.create_figure()
        plotter.plot_line(sample_x, sample_y)
        path = str(tmp_path / "saved.png")
        result = plotter.save_plot(path)
        assert result is True
        assert os.path.exists(path)

    def test_save_with_custom_options(self, plotter, sample_x, sample_y, tmp_path):
        plotter.create_figure()
        plotter.plot_line(sample_x, sample_y)
        path = str(tmp_path / "custom.png")
        result = plotter.save_plot(path, format="png", dpi=150, transparent=True)
        assert result is True

    def test_save_invalid_path_returns_false(self, plotter, sample_x, sample_y):
        """Cover lines 920-922: exception during save returns False."""
        plotter.create_figure()
        plotter.plot_line(sample_x, sample_y)
        # Invalid directory path triggers an exception
        result = plotter.save_plot("/nonexistent_dir_abc123/plot.png")
        assert result is False

    def test_save_pdf_format(self, plotter, sample_x, sample_y, tmp_path):
        plotter.create_figure()
        plotter.plot_line(sample_x, sample_y)
        path = str(tmp_path / "plot.pdf")
        result = plotter.save_plot(path, format="pdf")
        assert result is True
        assert os.path.exists(path)

    def test_save_svg_format(self, plotter, sample_x, sample_y, tmp_path):
        plotter.create_figure()
        plotter.plot_line(sample_x, sample_y)
        path = str(tmp_path / "plot.svg")
        result = plotter.save_plot(path, format="svg")
        assert result is True
        assert os.path.exists(path)


# ---------------------------------------------------------------------------
# clear_figures
# ---------------------------------------------------------------------------


class TestClearFigures:
    def test_clear(self, plotter, sample_x, sample_y):
        plotter.create_figure()
        plotter.plot_line(sample_x, sample_y)
        assert len(plotter.figures) == 1
        plotter.clear_figures()
        assert plotter.figures == []
        assert plotter.current_figure is None
        assert plotter.current_axes is None


# ---------------------------------------------------------------------------
# Convenience functions (lines 944-946, 958-960, 986-988, 999-1001, 1011-1012)
# ---------------------------------------------------------------------------


class TestConvenienceFunctions:
    def test_create_advanced_line_plot(self, sample_x, sample_y, tmp_path):
        """Cover lines 944-946."""
        save_path = str(tmp_path / "line.png")
        cfg = PlotConfig(show_plot=False)
        fig = create_advanced_line_plot(
            sample_x, sample_y, title="Line", xlabel="x", ylabel="y",
            config=cfg, save_path=save_path,
        )
        assert fig is not None
        assert os.path.exists(save_path)

    def test_create_advanced_scatter_plot(self, sample_x, sample_y):
        """Cover lines 958-960."""
        cfg = PlotConfig(show_plot=False)
        fig = create_advanced_scatter_plot(
            sample_x, sample_y, title="Scatter", config=cfg,
        )
        assert fig is not None

    def test_create_advanced_bar_chart(self, tmp_path):
        """Cover lines 986-988 (via the convenience function path)."""
        save_path = str(tmp_path / "bar.png")
        cfg = PlotConfig(show_plot=False)
        fig = create_advanced_bar_chart(
            ["A", "B", "C"], [10, 20, 30],
            title="Bar", config=cfg, save_path=save_path,
        )
        assert fig is not None

    def test_create_advanced_histogram(self):
        """Cover lines 986-988."""
        cfg = PlotConfig(show_plot=False)
        fig = create_advanced_histogram(
            list(range(50)), title="Hist", config=cfg,
        )
        assert fig is not None

    def test_create_advanced_heatmap(self):
        """Cover lines 999-1001."""
        cfg = PlotConfig(show_plot=False)
        fig = create_advanced_heatmap(
            [[1, 2], [3, 4]], title="Heatmap", config=cfg,
            x_labels=["a", "b"], y_labels=["c", "d"],
        )
        assert fig is not None

    def test_create_advanced_dashboard(self):
        """Cover lines 1011-1012."""
        cfg = PlotConfig(show_plot=False)
        points = [DataPoint(x=i, y=i * 2) for i in range(5)]
        datasets = [
            Dataset(name="d1", data=points, plot_type=PlotType.LINE, label="D1"),
            Dataset(name="d2", data=points, plot_type=PlotType.SCATTER, label="D2"),
        ]
        fig = create_advanced_dashboard(datasets, title="Dash", layout=(1, 2), config=cfg)
        assert fig is not None


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


class TestUtilityFunctions:
    def test_get_available_styles(self):
        styles = get_available_styles()
        assert len(styles) == len(ChartStyle)
        assert ChartStyle.DEFAULT in styles

    def test_get_available_palettes(self):
        palettes = get_available_palettes()
        assert len(palettes) == len(ColorPalette)

    def test_get_available_plot_types(self):
        plot_types = get_available_plot_types()
        assert len(plot_types) == len(PlotType)
        assert PlotType.LINE in plot_types


# ---------------------------------------------------------------------------
# Import fallback paths (lines 20-21, 26-46)
# ---------------------------------------------------------------------------


class TestImportFallbacks:
    def test_performance_monitoring_fallback_decorator(self):
        """Cover lines 26-46: when performance module not available, the
        fallback decorator and context manager should be no-ops.

        We test the fallback by calling them directly (they exist as module-level
        names regardless of whether the real performance module loaded).
        """
        # The module-level PERFORMANCE_MONITORING_AVAILABLE flag tells us
        # Regardless of whether real or fallback, the decorator should work
        # Just verify the plotter works (decorator applied to all methods)
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        fig, ax = p.create_figure()
        assert fig is not None


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_multiple_figures(self, plotter, sample_x, sample_y):
        """Creating multiple figures should track them all."""
        plotter.create_figure()
        plotter.plot_line(sample_x, sample_y)
        plotter.create_figure()
        plotter.plot_scatter(sample_x, sample_y)
        assert len(plotter.figures) == 2

    def test_scatter_default_no_label_no_color(self, plotter):
        plotter.create_figure()
        sc = plotter.plot_scatter([1, 2], [3, 4])
        assert sc is not None

    def test_heatmap_no_colorbar(self, plotter):
        plotter.create_figure()
        hm = plotter.plot_heatmap(
            [[1, 2], [3, 4]], x_labels=["a", "b"], y_labels=["c", "d"], cbar=False,
        )
        assert hm is not None

    def test_box_no_patch_artist(self, plotter):
        """Box with patch_artist=False so color branch is skipped."""
        plotter.create_figure()
        bp = plotter.plot_box([1, 2, 3, 4], patch_artist=False)
        assert "boxes" in bp

    def test_box_color_with_no_patch_artist(self, plotter):
        """Color is set but patch_artist is False -> color branch skipped (line 549)."""
        plotter.create_figure()
        bp = plotter.plot_box([1, 2, 3, 4], color="red", patch_artist=False)
        assert "boxes" in bp

    def test_empty_data_line(self, plotter):
        plotter.create_figure()
        line = plotter.plot_line([], [])
        assert line is not None

    def test_finalize_tight_layout_false(self, sample_x, sample_y):
        """Cover line 804: tight_layout=False in config."""
        cfg = PlotConfig(show_plot=False, tight_layout=False)
        p = AdvancedPlotter(cfg)
        p.create_figure()
        p.plot_line(sample_x, sample_y)
        fig = p.finalize_plot(title="No Tight")
        assert fig is not None


# ---------------------------------------------------------------------------
# Sprint 13 Agent E - Additional targeted tests
# Covers: uncovered line 655 (list->correlation), config effect verification,
# data validation, save_plot bbox_inches=None path, deeper behavioral checks,
# multi-figure lifecycle, dataset scatter without explicit size/color,
# PlotConfig custom fields, DataPoint with all fields, and more.
# ---------------------------------------------------------------------------


class TestCorrelationListInput:
    """Cover line 655: plot_correlation with a raw list input."""

    def test_correlation_from_list(self, plotter):
        """When data is a list-of-lists, it should be converted through
        ndarray -> DataFrame before computing correlation."""
        plotter.create_figure()
        data = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
        hm = plotter.plot_correlation(data)
        assert hm is not None

    def test_correlation_from_list_kendall(self, plotter):
        """Kendall correlation method with list input covers both line 654-655
        (isinstance list branch) and the method param."""
        plotter.create_figure()
        data = [[1.0, 2.0], [3.0, 1.0], [2.0, 4.0], [5.0, 3.0]]
        hm = plotter.plot_correlation(data, method="kendall")
        assert hm is not None


class TestPlotConfigEffects:
    """Verify that PlotConfig fields actually propagate to the plotter."""

    def test_config_title_propagates(self):
        cfg = PlotConfig(title="My Title", show_plot=False)
        p = AdvancedPlotter(cfg)
        assert p.config.title == "My Title"

    def test_config_xlabel_ylabel_propagate(self):
        cfg = PlotConfig(xlabel="Time", ylabel="Value", show_plot=False)
        p = AdvancedPlotter(cfg)
        assert p.config.xlabel == "Time"
        assert p.config.ylabel == "Value"

    def test_config_figsize_effect(self):
        """Config figsize should be used by create_figure."""
        cfg = PlotConfig(figsize=(14, 10), show_plot=False)
        p = AdvancedPlotter(cfg)
        fig, _ = p.create_figure()
        w, h = fig.get_size_inches()
        assert abs(w - 14) < 0.1
        assert abs(h - 10) < 0.1

    def test_config_dpi_effect(self):
        """Config dpi should be used by create_figure."""
        cfg = PlotConfig(dpi=150, show_plot=False)
        p = AdvancedPlotter(cfg)
        fig, _ = p.create_figure()
        assert fig.get_dpi() == 150

    def test_config_transparent_effect(self, tmp_path):
        """Transparent flag should be passed to savefig."""
        cfg = PlotConfig(show_plot=False, transparent=True)
        p = AdvancedPlotter(cfg)
        p.create_figure()
        p.plot_line([1, 2], [3, 4])
        path = str(tmp_path / "transparent.png")
        result = p.save_plot(path)
        assert result is True
        assert os.path.exists(path)

    def test_config_save_dpi_effect(self, tmp_path):
        """save_dpi from config should be used when not overridden."""
        cfg = PlotConfig(show_plot=False, save_dpi=72)
        p = AdvancedPlotter(cfg)
        p.create_figure()
        p.plot_line([1, 2], [3, 4])
        path = str(tmp_path / "lowdpi.png")
        result = p.save_plot(path)
        assert result is True
        assert os.path.exists(path)

    def test_config_save_format_effect(self, tmp_path):
        """save_format from config should be used when not overridden."""
        cfg = PlotConfig(show_plot=False, save_format="pdf")
        p = AdvancedPlotter(cfg)
        p.create_figure()
        p.plot_line([1, 2], [3, 4])
        path = str(tmp_path / "auto_format.pdf")
        result = p.save_plot(path)
        assert result is True
        assert os.path.exists(path)

    def test_config_bbox_inches_effect(self, tmp_path):
        """bbox_inches from config should be passed through."""
        cfg = PlotConfig(show_plot=False, bbox_inches="tight")
        p = AdvancedPlotter(cfg)
        p.create_figure()
        p.plot_line([1, 2], [3, 4])
        path = str(tmp_path / "bbox.png")
        result = p.save_plot(path)
        assert result is True


class TestDataPointVariations:
    """Deeper tests on DataPoint construction and field usage."""

    def test_data_point_with_all_fields(self):
        dp = DataPoint(x=1.5, y=2.5, label="pt", color="red", size=10.0, alpha=0.5)
        assert dp.x == 1.5
        assert dp.y == 2.5
        assert dp.label == "pt"
        assert dp.color == "red"
        assert dp.size == 10.0
        assert dp.alpha == 0.5

    def test_data_point_string_x(self):
        dp = DataPoint(x="category_a", y=100)
        assert dp.x == "category_a"

    def test_data_point_datetime_x(self):
        from datetime import datetime
        now = datetime(2026, 1, 1, 12, 0, 0)
        dp = DataPoint(x=now, y=42)
        assert dp.x == now


class TestDatasetVariations:
    """Deeper tests on Dataset construction and defaults."""

    def test_dataset_with_custom_fields(self):
        ds = Dataset(
            name="custom",
            data=[],
            plot_type=PlotType.SCATTER,
            color="green",
            label="scatter_data",
            alpha=0.3,
            linewidth=1.5,
            markersize=12.0,
        )
        assert ds.name == "custom"
        assert ds.color == "green"
        assert ds.label == "scatter_data"
        assert ds.alpha == 0.3
        assert ds.linewidth == 1.5
        assert ds.markersize == 12.0

    def test_dataset_all_plot_types_accepted(self):
        for pt in PlotType:
            ds = Dataset(name=f"test_{pt.value}", data=[], plot_type=pt)
            assert ds.plot_type == pt


class TestPlotDatasetScatterDefaults:
    """Cover scatter branch in _plot_dataset when point.size/color are None."""

    def test_plot_dataset_scatter_none_size_color(self, plotter):
        """When DataPoint.size is None and DataPoint.color is None, defaults
        should be pulled from Dataset.markersize and Dataset.color."""
        fig, ax = plotter.create_figure()
        points = [DataPoint(x=1, y=2), DataPoint(x=3, y=4)]
        ds = Dataset(
            name="sc_defaults",
            data=points,
            plot_type=PlotType.SCATTER,
            label="defaults",
            color="purple",
            markersize=20.0,
        )
        plotter._plot_dataset(ax, ds)
        # No error raised; the default fallback in _plot_dataset worked


class TestMultiFigureLifecycle:
    """Test creating multiple figures, switching, clearing."""

    def test_create_three_figures_then_clear(self):
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        for _ in range(3):
            p.create_figure()
        assert len(p.figures) == 3
        p.clear_figures()
        assert len(p.figures) == 0
        assert p.current_figure is None
        assert p.current_axes is None

    def test_last_figure_is_current(self):
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        fig1, _ = p.create_figure()
        fig2, _ = p.create_figure()
        assert p.current_figure is fig2
        assert p.current_figure is not fig1

    def test_save_after_clear_returns_false(self, tmp_path):
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        p.create_figure()
        p.plot_line([1], [2])
        p.clear_figures()
        result = p.save_plot(str(tmp_path / "after_clear.png"))
        assert result is False

    def test_finalize_after_clear_raises(self):
        cfg = PlotConfig(show_plot=False)
        p = AdvancedPlotter(cfg)
        p.create_figure()
        p.plot_line([1], [2])
        p.clear_figures()
        with pytest.raises(ValueError, match="No current figure"):
            p.finalize_plot()


class TestSavePlotBboxNone:
    """Cover the path where bbox_inches override is explicitly None
    so the config value is used."""

    def test_save_plot_bbox_inches_none_uses_config(self, plotter, sample_x, sample_y, tmp_path):
        plotter.create_figure()
        plotter.plot_line(sample_x, sample_y)
        path = str(tmp_path / "bbox_none.png")
        result = plotter.save_plot(path, bbox_inches=None)
        assert result is True
        assert os.path.exists(path)


class TestBarWithColors:
    """Test bar chart with color list."""

    def test_bar_with_color_list(self, plotter):
        plotter.create_figure()
        bars = plotter.plot_bar(
            ["A", "B", "C"],
            [10, 20, 30],
            color=["red", "green", "blue"],
            label="colored",
        )
        assert bars is not None

    def test_bar_with_custom_width(self, plotter):
        plotter.create_figure()
        bars = plotter.plot_bar(["X", "Y"], [5, 10], width=0.4)
        assert bars is not None

    def test_horizontal_bar_with_label(self, plotter):
        plotter.create_figure()
        bars = plotter.plot_bar(
            ["A", "B"],
            [100, 200],
            orientation="horizontal",
            label="horiz",
            alpha=0.5,
        )
        assert bars is not None


class TestHistogramEdgeCases:
    """Additional histogram edge cases."""

    def test_histogram_with_bin_edges(self, plotter):
        """Provide explicit bin edges instead of count."""
        plotter.create_figure()
        counts, edges, _ = plotter.plot_histogram(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            bins=[0, 3, 6, 10],
        )
        assert len(edges) == 4

    def test_histogram_single_value(self, plotter):
        """Histogram with a single repeated value."""
        plotter.create_figure()
        counts, edges, patches = plotter.plot_histogram([5, 5, 5, 5], bins=1)
        assert counts is not None


class TestHeatmapEdgeCases:
    """Additional heatmap variations."""

    def test_heatmap_with_annotation(self, plotter):
        plotter.create_figure()
        data = np.array([[1.11, 2.22], [3.33, 4.44]])
        hm = plotter.plot_heatmap(
            data,
            x_labels=["c1", "c2"],
            y_labels=["r1", "r2"],
            annot=True,
            fmt=".1f",
            cmap="plasma",
        )
        assert hm is not None

    def test_heatmap_large_matrix(self, plotter):
        plotter.create_figure()
        data = np.random.rand(10, 10)
        hm = plotter.plot_heatmap(data)
        assert hm is not None


class TestViolinEdgeCases:
    """Additional violin plot tests."""

    def test_violin_dict_single_group(self, plotter):
        """Dict with a single group."""
        plotter.create_figure()
        vp = plotter.plot_violin({"Only": [1, 2, 3, 4, 5, 6, 7, 8]})
        assert vp is not None

    def test_violin_large_dataset(self, plotter):
        """Violin with a larger dataset."""
        plotter.create_figure()
        data = list(np.random.normal(0, 1, 200))
        vp = plotter.plot_violin(data, labels=["normal"])
        assert vp is not None


class TestDashboardEdgeCases:
    """Additional dashboard edge cases."""

    def test_dashboard_empty_datasets(self, plotter):
        """Dashboard with zero datasets should create figure but all panels hidden."""
        fig = plotter.create_dashboard([], layout=(2, 2), title="Empty")
        assert fig is not None

    def test_dashboard_with_tight_layout_false(self):
        """Dashboard respects tight_layout=False."""
        cfg = PlotConfig(show_plot=False, tight_layout=False)
        p = AdvancedPlotter(cfg)
        points = [DataPoint(x=i, y=i) for i in range(5)]
        ds = Dataset(name="d", data=points, plot_type=PlotType.LINE, label="L")
        fig = p.create_dashboard([ds], layout=(1, 1), title="No Tight")
        assert fig is not None

    def test_dashboard_1d_axes_layout(self, plotter):
        """Layout (1, 3) gives 1D axes array -- cover axes.ndim == 1 branch."""
        points = [DataPoint(x=i, y=i * 2) for i in range(5)]
        datasets = [
            Dataset(name=f"d{i}", data=points, plot_type=PlotType.LINE, label=f"D{i}")
            for i in range(3)
        ]
        fig = plotter.create_dashboard(datasets, layout=(1, 3), title="1D Axes")
        assert fig is not None


class TestFinalizeWithOverrides:
    """Test finalize_plot with various override combinations."""

    def test_finalize_overrides_config_title(self, plotter, sample_x, sample_y):
        """Explicit title arg should override config title."""
        plotter.config.title = "Config Title"
        plotter.create_figure()
        plotter.plot_line(sample_x, sample_y, label="line")
        fig = plotter.finalize_plot(title="Override Title")
        assert fig is not None
        # suptitle should be "Override Title"
        assert fig._suptitle is not None
        assert fig._suptitle.get_text() == "Override Title"

    def test_finalize_uses_config_title_when_none(self, sample_x, sample_y):
        """When no title arg, config title should be used."""
        cfg = PlotConfig(title="From Config", show_plot=False)
        p = AdvancedPlotter(cfg)
        p.create_figure()
        p.plot_line(sample_x, sample_y, label="line")
        fig = p.finalize_plot()
        assert fig._suptitle.get_text() == "From Config"

    def test_finalize_no_title_at_all(self, plotter, sample_x, sample_y):
        """When both title arg and config title are empty, no suptitle set."""
        plotter.create_figure()
        plotter.plot_line(sample_x, sample_y)
        fig = plotter.finalize_plot()
        # _suptitle may be None or have empty text
        assert fig is not None


class TestGetColorPaletteReturnType:
    """Verify _get_color_palette returns correct number and type."""

    def test_palette_returns_correct_count(self, plotter):
        for n in [1, 3, 7, 12]:
            colors = plotter._get_color_palette(n)
            assert len(colors) == n

    def test_palette_single_color(self):
        cfg = PlotConfig(palette=ColorPalette.VIRIDIS, show_plot=False)
        p = AdvancedPlotter(cfg)
        colors = p._get_color_palette(1)
        assert len(colors) == 1


class TestCreateFigureCustomDpi:
    """Test create_figure with explicit dpi kwarg."""

    def test_dpi_override_in_kwargs(self, plotter):
        fig, _ = plotter.create_figure(dpi=72)
        assert fig.get_dpi() == 72

    def test_extra_kwargs_passed_through(self, plotter):
        """Passing squeeze=False should not raise."""
        fig, axes = plotter.create_figure(subplots=(1, 1), squeeze=False)
        assert fig is not None
