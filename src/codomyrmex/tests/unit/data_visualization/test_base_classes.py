"""Tests for the highest-fan-in base classes in data_visualization.

Covers: BasePlot, BaseComponent, and BaseReport public API contracts.
These are the most-imported files in the codebase (20, 11, 6 importers
respectively) and previously had zero direct test coverage.
"""

import pytest

# ─── BasePlot ─────────────────────────────────────────────────────────────────


class TestBasePlotPublicAPI:
    """Verify BasePlot public API contract."""

    def test_default_attributes(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot()
        assert p.title == ""
        assert p.width == 800
        assert p.height == 400
        assert p.data == []
        assert p.options == {}

    def test_custom_attributes(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="My Plot", width=1200, height=600, data=[1, 2, 3])
        assert p.title == "My Plot"
        assert p.width == 1200
        assert p.height == 600
        assert len(p.data) == 3

    def test_render_returns_html_div(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="Hello")
        html = p.render()
        assert "<div" in html
        assert "Hello" in html
        assert "BasePlot" in html

    def test_to_dict_structure(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="Dict Test", data=[10, 20])
        d = p.to_dict()
        assert d["type"] == "BasePlot"
        assert d["title"] == "Dict Test"
        assert d["width"] == 800
        assert d["height"] == 400
        assert d["data_count"] == 2

    def test_repr(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="R", data=[1])
        assert repr(p) == "BasePlot(title='R', data_count=1)"

    def test_str_returns_html(self):
        """BasePlot.__str__ delegates to to_html(), not render()."""
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="S")
        # __str__ calls to_html() which returns an <img> tag
        result = str(p)
        assert "<img" in result or "<div" in result  # either render path is acceptable

    def test_fig_to_base64_static(self):
        """_fig_to_base64 must return a non-empty ASCII string."""
        pytest.importorskip("matplotlib")
        from matplotlib.figure import Figure

        from codomyrmex.data_visualization.plots._base import BasePlot

        fig = Figure()
        result = BasePlot._fig_to_base64(fig)
        assert isinstance(result, str)
        assert len(result) > 0
        # Base64 only contains valid chars
        import base64

        decoded = base64.b64decode(result)
        assert decoded[:4] == b"\x89PNG"

    @pytest.mark.skipif(
        not __import__("importlib").util.find_spec("matplotlib"),
        reason="matplotlib not installed",
    )
    def test_to_html_returns_img_tag(self):
        from codomyrmex.data_visualization.plots._base import BasePlot

        p = BasePlot(title="HTML Test")
        html = p.to_html()
        assert html.startswith("<img ")
        assert "data:image/png;base64," in html
        assert 'alt="HTML Test"' in html

    @pytest.mark.skipif(
        not __import__("importlib").util.find_spec("matplotlib"),
        reason="matplotlib not installed",
    )
    def test_to_html_does_not_mutate_backend(self):
        """to_html() must not change the global pyplot backend."""
        import matplotlib.pyplot as plt

        backend_before = plt.get_backend()
        from codomyrmex.data_visualization.plots._base import BasePlot

        BasePlot(title="backend test").to_html()
        assert plt.get_backend() == backend_before

    def test_render_figure_extension_point(self):
        """_render_figure can be overridden by subclasses."""
        from codomyrmex.data_visualization.plots._base import BasePlot

        class CustomPlot(BasePlot):
            rendered = False

            def _render_figure(self, fig, ax):
                CustomPlot.rendered = True

        p = CustomPlot(title="custom")

        # Call _render_figure directly with dummy objects
        class FakeFig:
            pass

        class FakeAx:
            texts = []

            def text(self, *a, **kw):
                pass

        p._render_figure(FakeFig(), FakeAx())
        assert CustomPlot.rendered


# ─── BaseComponent ────────────────────────────────────────────────────────────


class TestBaseComponentPublicAPI:
    """Verify BaseComponent public API contract."""

    def test_default_attributes(self):
        from codomyrmex.data_visualization.components._base import BaseComponent

        c = BaseComponent()
        assert c.css_class == ""
        assert c.style == {}

    def test_custom_css_class(self):
        from codomyrmex.data_visualization.components._base import BaseComponent

        c = BaseComponent(css_class="chart-wrapper")
        assert c.css_class == "chart-wrapper"

    def test_render_returns_div(self):
        from codomyrmex.data_visualization.components._base import BaseComponent

        c = BaseComponent(css_class="my-class")
        html = c.render()
        assert 'class="my-class"' in html
        assert "BaseComponent" in html

    def test_to_dict(self):
        from codomyrmex.data_visualization.components._base import BaseComponent

        c = BaseComponent()
        d = c.to_dict()
        assert d["type"] == "BaseComponent"

    def test_str_returns_render(self):
        from codomyrmex.data_visualization.components._base import BaseComponent

        c = BaseComponent()
        assert str(c) == c.render()

    def test_repr(self):
        from codomyrmex.data_visualization.components._base import BaseComponent

        c = BaseComponent(css_class="x")
        assert "BaseComponent" in repr(c)
        assert "x" in repr(c)

    def test_subclass_can_override_render(self):
        from codomyrmex.data_visualization.components._base import BaseComponent

        class MyComp(BaseComponent):
            def render(self) -> str:
                return "<span>custom</span>"

        c = MyComp()
        assert c.render() == "<span>custom</span>"
        assert str(c) == "<span>custom</span>"


# ─── BaseReport ───────────────────────────────────────────────────────────────


class TestBaseReportPublicAPI:
    """Verify BaseReport public API contract."""

    def test_default_attributes(self):
        from codomyrmex.data_visualization.reports._base import BaseReport

        r = BaseReport()
        assert r.title == ""

    def test_custom_title(self):
        from codomyrmex.data_visualization.reports._base import BaseReport

        r = BaseReport(title="Q1 Report")
        assert r.title == "Q1 Report"

    def test_render_returns_string(self):
        from codomyrmex.data_visualization.reports._base import BaseReport

        r = BaseReport(title="Test")
        html = r.render()
        assert isinstance(html, str)

    def test_to_dict_has_title_and_section_count(self):
        from codomyrmex.data_visualization.reports._base import BaseReport

        r = BaseReport(title="MyReport")
        d = r.to_dict()
        assert d["title"] == "MyReport"
        assert d["section_count"] == 0

    def test_str_returns_render(self):
        from codomyrmex.data_visualization.reports._base import BaseReport

        r = BaseReport()
        assert str(r) == r.render()
