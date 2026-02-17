import pytest
from codomyrmex.data_visualization.plots.funnel import FunnelChart
from codomyrmex.data_visualization.plots.sankey import SankeyDiagram
from codomyrmex.data_visualization.components.timeline import Timeline, TimelineEvent
from codomyrmex.data_visualization.components.statbox import StatBox

def test_funnel_chart_render():
    stages = ["Leads", "Sales"]
    values = [100, 50]
    plot = FunnelChart("Test Funnel", stages, values)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert 'alt="Test Funnel"' in html

def test_sankey_diagram_render():
    links = [("A", "B", 10), ("B", "C", 5)]
    plot = SankeyDiagram(title="Test Sankey", links=links)
    html = plot.to_html()
    assert "mermaid" in html
    assert "sankey-beta" in html
    assert "A, B, 10" in html

def test_timeline_component():
    events = [
        TimelineEvent(timestamp="2023-01-01", label="Start", description="Description")
    ]
    timeline = Timeline(events=events)
    html = str(timeline)
    assert "Start" in html
    assert "2023-01-01" in html
    assert "Description" in html

def test_statbox_component():
    stat = StatBox(label="Revenue", value="$10k", delta="+5%", direction="up")
    html = str(stat)
    assert "Revenue" in html
    assert "$10k" in html
    assert "+5%" in html
    assert "color: green" in html
