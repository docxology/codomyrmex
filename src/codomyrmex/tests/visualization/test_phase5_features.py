import pytest
from codomyrmex.visualization.plots.treemap import TreeMap
from codomyrmex.visualization.plots.network import NetworkGraph
from codomyrmex.visualization.components.heatmap_table import HeatmapTable

def test_treemap_render():
    data = [
        {"label": "A", "value": 10},
        {"label": "B", "value": 20},
        {"label": "C", "value": 5}
    ]
    plot = TreeMap("Test Tree", data)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert "alt=\"Test Tree\"" in html

def test_network_graph_render():
    nodes = ["A", "B", "C"]
    edges = [("A", "B"), ("B", "C"), ("C", "A")]
    plot = NetworkGraph("Test Net", nodes, edges)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert "alt=\"Test Net\"" in html

def test_heatmap_table_component():
    headers = ["Col A", "Col B"]
    rows = [
        [10, 20],
        [5, 40]
    ]
    table = HeatmapTable(headers, rows, "Test Heatmap")
    html = str(table)
    assert "Test Heatmap" in html
    assert "Col A" in html
    assert "40" in html # Check content
    assert "rgba(0, 123, 255" in html # Check coloring
