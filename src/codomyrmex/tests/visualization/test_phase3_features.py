import pytest
from codomyrmex.visualization.plots.funnel import FunnelChart
from codomyrmex.visualization.plots.sankey import SankeyDiagram
from codomyrmex.visualization.components.timeline import Timeline, TimelineEvent
from codomyrmex.visualization.components.statbox import StatBox

def test_funnel_chart_render():
    stages = ["Leads", "Sales"]
    values = [100, 50]
    plot = FunnelChart("Test Funnel", stages, values)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert "alt=\"Test Funnel\"" in html

def test_sankey_diagram_render():
    links = [("A", "B", 10), ("B", "C", 5)]
    plot = SankeyDiagram("Test Sankey", links)
    html = plot.to_html()
    assert "mermaid" in html
    assert "sankey-beta" in html
    assert "A, B, 10" in html

def test_timeline_component():
    events = [
        TimelineEvent("2023-01-01", "Start", "Description")
    ]
    timeline = Timeline(events)
    html = str(timeline)
    assert "Start" in html
    assert "2023-01-01" in html
    assert "Description" in html

def test_statbox_component():
    stat = StatBox("Revenue", "$10k", "+5%", "up")
    html = str(stat)
    assert "Revenue" in html
    assert "$10k" in html
    assert "+5%" in html
    assert "color: green" in html
