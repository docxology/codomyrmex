"""Unit tests for codomyrmex.data_visualization.plots._base.

Covers BasePlot public API including construction, render(), to_dict(),
__repr__, save(), to_html(), _fig_to_base64(), and _render_figure().

The import of BasePlot is deferred to test-method level to avoid triggering
the data_visualization package __init__.py circular import that exists in the
engines/scatter_plot circular dependency chain.

matplotlib-dependent tests are skipped when the library is not installed.
"""

from __future__ import annotations

import base64

import pytest

try:
    import matplotlib as mpl

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


# ---------------------------------------------------------------------------
# Construction and dataclass defaults
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBasePlotConstruction:
    """BasePlot construction and default attribute values."""

    def test_default_title_is_empty_string(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot()
        assert p.title == ""

    def test_default_width(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot()
        assert p.width == 800

    def test_default_height(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot()
        assert p.height == 400

    def test_default_data_is_empty_list(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot()
        assert p.data == []

    def test_custom_title(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="Sales Q1")
        assert p.title == "Sales Q1"

    def test_custom_dimensions(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(width=1920, height=1080)
        assert p.width == 1920
        assert p.height == 1080

    def test_custom_data(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(data=[10, 20, 30])
        assert len(p.data) == 3
        assert p.data[1] == 20

    def test_data_lists_are_independent(self):
        """Different instances must not share the same list object."""
        from codomyrmex.data_visualization.plots._base import BasePlot

        p1 = BasePlot()
        p2 = BasePlot()
        p1.data.append(99)
        assert p2.data == []

    def test_can_be_subclassed(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        class MyPlot(BasePlot):
            pass

        p = MyPlot(title="Sub", data=[1, 2])
        assert p.title == "Sub"
        assert len(p.data) == 2


# ---------------------------------------------------------------------------
# render()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBasePlotRender:
    """render() returns a self-contained HTML div."""

    def test_render_returns_string(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot()
        assert isinstance(p.render(), str)

    def test_render_contains_div_tag(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot()
        assert "<div" in p.render()

    def test_render_includes_title(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="Monthly Revenue")
        assert "Monthly Revenue" in p.render()

    def test_render_includes_class_name(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="T")
        assert "BasePlot" in p.render()

    def test_render_subclass_name_appears(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        class BarPlot(BasePlot):
            pass

        p = BarPlot(title="Bar")
        assert "BarPlot" in p.render()

    def test_render_empty_title(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot()
        html = p.render()
        assert "<div" in html


# ---------------------------------------------------------------------------
# to_dict()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBasePlotToDict:
    """to_dict() serialises metadata correctly."""

    def test_to_dict_returns_dict(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot()
        assert isinstance(p.to_dict(), dict)

    def test_to_dict_type_field(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot()
        assert p.to_dict()["type"] == "BasePlot"

    def test_to_dict_title_field(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="Revenue")
        assert p.to_dict()["title"] == "Revenue"

    def test_to_dict_width_and_height(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(width=640, height=480)
        d = p.to_dict()
        assert d["width"] == 640
        assert d["height"] == 480

    def test_to_dict_data_count(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(data=[1, 2, 3, 4, 5])
        assert p.to_dict()["data_count"] == 5

    def test_to_dict_empty_data_count_zero(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot()
        assert p.to_dict()["data_count"] == 0

    def test_to_dict_subclass_type_field(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        class LinePlot(BasePlot):
            pass

        p = LinePlot()
        assert p.to_dict()["type"] == "LinePlot"

    def test_to_dict_keys_present(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot()
        keys = set(p.to_dict().keys())
        assert {"type", "title", "width", "height", "data_count"}.issubset(keys)


# ---------------------------------------------------------------------------
# __repr__ and __str__
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBasePlotReprStr:
    """repr() and str() output contracts."""

    def test_repr_includes_class_name(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot()
        assert "BasePlot" in repr(p)

    def test_repr_includes_title(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="My Title")
        assert "My Title" in repr(p)

    def test_repr_includes_data_count(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(data=[1, 2])
        assert "data_count=2" in repr(p)

    def test_repr_format(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="T", data=[1])
        assert repr(p) == "BasePlot(title='T', data_count=1)"

    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed")
    def test_str_delegates_to_to_html(self):
        """__str__ calls to_html() which produces an <img> tag."""
        import matplotlib.pyplot as plt

        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="S")
        result = str(p)
        plt.close("all")
        assert "<img" in result


# ---------------------------------------------------------------------------
# save()
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed")
class TestBasePlotSave:
    """save() writes HTML to disk and returns the output path."""

    def test_save_returns_output_path(self, tmp_path):
        import matplotlib.pyplot as plt

        from codomyrmex.data_visualization.plots._base import BasePlot

        output = str(tmp_path / "plot.html")
        p = BasePlot(title="Save Test")
        result = p.save(output)
        plt.close("all")
        assert result == output

    def test_save_creates_file(self, tmp_path):
        from pathlib import Path

        import matplotlib.pyplot as plt

        from codomyrmex.data_visualization.plots._base import BasePlot

        output = str(tmp_path / "chart.html")
        BasePlot(title="File Created").save(output)
        plt.close("all")
        assert Path(output).exists()

    def test_save_file_contains_img_tag(self, tmp_path):
        from pathlib import Path

        import matplotlib.pyplot as plt

        from codomyrmex.data_visualization.plots._base import BasePlot

        output = str(tmp_path / "out.html")
        BasePlot(title="IMG Tag").save(output)
        plt.close("all")
        content = Path(output).read_text()
        assert "<img" in content

    def test_save_file_is_valid_html_document(self, tmp_path):
        from pathlib import Path

        import matplotlib.pyplot as plt

        from codomyrmex.data_visualization.plots._base import BasePlot

        output = str(tmp_path / "valid.html")
        BasePlot(title="Valid HTML").save(output)
        plt.close("all")
        content = Path(output).read_text()
        assert "<!DOCTYPE html>" in content
        assert "<html>" in content
        assert "<body>" in content

    def test_save_title_appears_in_file(self, tmp_path):
        from pathlib import Path

        import matplotlib.pyplot as plt

        from codomyrmex.data_visualization.plots._base import BasePlot

        output = str(tmp_path / "titled.html")
        BasePlot(title="My Unique Title").save(output)
        plt.close("all")
        content = Path(output).read_text()
        assert "My Unique Title" in content

    def test_save_returns_string_type(self, tmp_path):
        import matplotlib.pyplot as plt

        from codomyrmex.data_visualization.plots._base import BasePlot

        output = str(tmp_path / "type_check.html")
        p = BasePlot()
        result = p.save(output)
        plt.close("all")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# to_html()
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed")
class TestBasePlotToHtml:
    """to_html() returns a well-formed base64 PNG img tag."""

    def test_to_html_returns_string(self):
        import matplotlib.pyplot as plt

        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="T")
        result = p.to_html()
        plt.close("all")
        assert isinstance(result, str)

    def test_to_html_starts_with_img_tag(self):
        import matplotlib.pyplot as plt

        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="T")
        result = p.to_html()
        plt.close("all")
        assert result.startswith("<img ")

    def test_to_html_contains_base64_data_url(self):
        import matplotlib.pyplot as plt

        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="T")
        result = p.to_html()
        plt.close("all")
        assert "data:image/png;base64," in result

    def test_to_html_alt_attribute_matches_title(self):
        import matplotlib.pyplot as plt

        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="My Chart")
        result = p.to_html()
        plt.close("all")
        assert 'alt="My Chart"' in result

    def test_to_html_does_not_mutate_pyplot_backend(self):
        """Uses FigureCanvasAgg directly — global backend must be unchanged."""
        import matplotlib.pyplot as plt

        from codomyrmex.data_visualization.plots._base import BasePlot

        backend_before = plt.get_backend()
        BasePlot(title="backend").to_html()
        plt.close("all")
        assert plt.get_backend() == backend_before


# ---------------------------------------------------------------------------
# _fig_to_base64 static method
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed")
class TestFigToBase64:
    """_fig_to_base64() converts a Figure to a base64 PNG string."""

    def test_returns_string(self):
        from matplotlib.figure import Figure

        from codomyrmex.data_visualization.plots._base import BasePlot

        fig = Figure()
        result = BasePlot._fig_to_base64(fig)
        assert isinstance(result, str)

    def test_returns_non_empty_string(self):
        from matplotlib.figure import Figure

        from codomyrmex.data_visualization.plots._base import BasePlot

        fig = Figure()
        result = BasePlot._fig_to_base64(fig)
        assert len(result) > 0

    def test_result_is_valid_base64(self):
        from matplotlib.figure import Figure

        from codomyrmex.data_visualization.plots._base import BasePlot

        fig = Figure()
        result = BasePlot._fig_to_base64(fig)
        decoded = base64.b64decode(result)
        assert decoded[:4] == b"\x89PNG"

    def test_result_is_ascii_safe(self):
        from matplotlib.figure import Figure

        from codomyrmex.data_visualization.plots._base import BasePlot

        fig = Figure()
        result = BasePlot._fig_to_base64(fig)
        result.encode("ascii")  # raises if non-ASCII present

    def test_different_figure_sizes_produce_different_outputs(self):
        from matplotlib.figure import Figure

        from codomyrmex.data_visualization.plots._base import BasePlot

        small = Figure(figsize=(1, 1))
        large = Figure(figsize=(20, 20))
        small_b64 = BasePlot._fig_to_base64(small)
        large_b64 = BasePlot._fig_to_base64(large)
        assert small_b64 != large_b64


# ---------------------------------------------------------------------------
# _render_figure extension point
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRenderFigureExtensionPoint:
    """Subclasses can override _render_figure to customise drawing."""

    def test_default_render_figure_draws_text(self):
        """Default implementation calls ax.text without raising."""
        from codomyrmex.data_visualization.plots._base import BasePlot

        calls: list = []

        class FakeAx:
            def text(self, *args, **kwargs):
                calls.append((args, kwargs))

        class FakeFig:
            pass

        p = BasePlot(title="Ext")
        p._render_figure(FakeFig(), FakeAx())
        assert len(calls) == 1

    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed")
    def test_subclass_override_is_called_by_to_html(self):
        """When to_html() runs, it calls the subclass's _render_figure."""
        import matplotlib.pyplot as plt

        from codomyrmex.data_visualization.plots._base import BasePlot

        class TrackingPlot(BasePlot):
            called = False

            def _render_figure(self, fig, ax):
                TrackingPlot.called = True

        p = TrackingPlot(title="track")
        p.to_html()
        plt.close("all")
        assert TrackingPlot.called
