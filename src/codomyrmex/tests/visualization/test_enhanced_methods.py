"""Tests for enhanced visualization methods added during the comprehensive audit.

Covers: submodule imports, BasePlot.save, BasePlot.__str__, BarChart, LinePlot,
BaseComponent.__str__, BaseReport.save, Dashboard.__str__, report .save(),
to_dict, __repr__.
"""
import pytest
from pathlib import Path


# ── Submodule import tests ────────────────────────────────────────

def test_plots_submodule_exports():
    from codomyrmex.data_visualization.plots import (
        BasePlot, ScatterPlot, Heatmap, MermaidDiagram, Histogram,
        PieChart, BoxPlot, AreaPlot, ViolinPlot, RadarChart,
        CandlestickChart, GanttChart, FunnelChart, SankeyDiagram,
        WordCloud, ConfusionMatrix, TreeMap, NetworkGraph,
        BarChart, LinePlot,
    )
    assert len(BasePlot.__dataclass_fields__) > 0


def test_components_submodule_exports():
    from codomyrmex.data_visualization.components import (
        BaseComponent, Alert, Badge, ChatBubble, CodeBlock,
        HeatmapTable, Image, JsonView, ProgressBar, StatBox,
        TextBlock, Timeline, TimelineEvent, Video,
    )
    assert BaseComponent is not None


def test_reports_submodule_exports():
    from codomyrmex.data_visualization.reports import (
        BaseReport, GeneralSystemReport, FinanceReport,
        MarketingReport, LogisticsReport,
    )
    assert BaseReport is not None


def test_main_module_exports():
    from codomyrmex.data_visualization import (
        Theme, DEFAULT_THEME, DARK_THEME, Grid, Section,
        Dashboard, Card, Table, render_html, generate_report,
        Report, GeneralSystemReport, FinanceReport,
        MarketingReport, LogisticsReport,
        BarPlot, BarChart, LinePlot,
    )
    assert BarPlot is BarChart


# ── BasePlot enhanced methods ─────────────────────────────────────

def test_base_plot_str():
    from codomyrmex.data_visualization.plots import BasePlot
    p = BasePlot(title="Test")
    s = str(p)
    assert "data:image/png;base64" in s
    assert 'alt="Test"' in s


def test_base_plot_repr():
    from codomyrmex.data_visualization.plots import BasePlot
    p = BasePlot(title="X", data=[1, 2, 3])
    assert repr(p) == "BasePlot(title='X', data_count=3)"


def test_base_plot_save(tmp_path):
    from codomyrmex.data_visualization.plots import BasePlot
    p = BasePlot(title="Save Test")
    out = tmp_path / "plot.html"
    result = p.save(str(out))
    assert result == str(out)
    assert out.exists()
    content = out.read_text()
    assert "data:image/png;base64" in content
    assert "<!DOCTYPE html>" in content


def test_base_plot_to_dict():
    from codomyrmex.data_visualization.plots import BasePlot
    p = BasePlot(title="D", data=[1, 2])
    d = p.to_dict()
    assert d["type"] == "BasePlot"
    assert d["title"] == "D"
    assert d["data_count"] == 2


# ── BarChart ──────────────────────────────────────────────────────

def test_bar_chart_categories():
    from codomyrmex.data_visualization.plots import BarChart
    p = BarChart(title="Bar", categories=["A", "B"], values=[10, 20])
    html = p.to_html()
    assert "data:image/png;base64" in html
    assert 'alt="Bar"' in html


def test_bar_chart_data_tuples():
    from codomyrmex.data_visualization.plots import BarChart
    p = BarChart(title="Bar2", data=[("A", 10), ("B", 20)])
    html = p.to_html()
    assert "data:image/png;base64" in html


def test_bar_chart_empty():
    from codomyrmex.data_visualization.plots import BarChart
    p = BarChart(title="Empty")
    html = p.to_html()
    assert "data:image/png;base64" in html  # Still renders an empty chart


# ── LinePlot ──────────────────────────────────────────────────────

def test_line_plot_xy():
    from codomyrmex.data_visualization.plots import LinePlot
    p = LinePlot(title="Line", x=[1, 2, 3], y=[10, 20, 15])
    html = p.to_html()
    assert "data:image/png;base64" in html
    assert 'alt="Line"' in html


def test_line_plot_data():
    from codomyrmex.data_visualization.plots import LinePlot
    p = LinePlot(title="Line2", data=[5, 10, 15])
    html = p.to_html()
    assert "data:image/png;base64" in html


# ── BaseComponent __str__ ─────────────────────────────────────────

def test_base_component_str():
    from codomyrmex.data_visualization.components import BaseComponent
    c = BaseComponent(css_class="test")
    assert 'class="test"' in str(c)
    assert "BaseComponent(css_class='test')" == repr(c)


# ── BaseReport save ──────────────────────────────────────────────

def test_base_report_save(tmp_path):
    from codomyrmex.data_visualization.reports import BaseReport
    r = BaseReport(title="Test Report")
    out = tmp_path / "report.html"
    result = r.save(str(out))
    assert result == str(out)
    assert out.exists()
    assert "Test Report" in out.read_text()


def test_base_report_str_repr():
    from codomyrmex.data_visualization.reports import BaseReport
    r = BaseReport(title="R")
    assert "<article>" in str(r)
    assert "BaseReport(title='R', sections=0)" == repr(r)


# ── Dashboard __str__ / __repr__ ─────────────────────────────────

def test_dashboard_str():
    from codomyrmex.data_visualization.core.ui import Dashboard
    d = Dashboard(title="Test Dash")
    s = str(d)
    assert "Test Dash" in s
    assert "<html>" in s


def test_dashboard_repr():
    from codomyrmex.data_visualization.core.ui import Dashboard
    d = Dashboard(title="Dash")
    assert repr(d) == "Dashboard(title='Dash', sections=0)"


# ── Report save methods ──────────────────────────────────────────

def test_finance_report_save(tmp_path):
    from codomyrmex.data_visualization.reports import FinanceReport
    r = FinanceReport()
    out = tmp_path / "fin.html"
    result = r.save(str(out))
    assert Path(result).exists()
    content = Path(result).read_text()
    assert "Net Profit" in content
    assert "Financial Overview" in content


def test_marketing_report_save(tmp_path):
    from codomyrmex.data_visualization.reports import MarketingReport
    r = MarketingReport()
    out = tmp_path / "mkt.html"
    result = r.save(str(out))
    assert Path(result).exists()
    content = Path(result).read_text()
    assert "Brand Awareness" in content


def test_logistics_report_save(tmp_path):
    from codomyrmex.data_visualization.reports import LogisticsReport
    r = LogisticsReport()
    out = tmp_path / "log.html"
    result = r.save(str(out))
    assert Path(result).exists()
    content = Path(result).read_text()
    assert "Shipment #1234" in content
    assert "sankey-beta" in content


def test_general_report_save(tmp_path):
    from codomyrmex.data_visualization.reports import GeneralSystemReport
    r = GeneralSystemReport()
    out = tmp_path / "gen.html"
    result = r.save(str(out))
    assert Path(result).exists()
    content = Path(result).read_text()
    assert "Codomyrmex Executive Dashboard" in content
    assert "Revenue" in content
