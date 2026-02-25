from codomyrmex.data_visualization.components.heatmap_table import HeatmapTable
from codomyrmex.data_visualization.plots.network import NetworkGraph
from codomyrmex.data_visualization.plots.treemap import TreeMap


def test_treemap_render():
    """Test functionality: treemap render."""
    data = [
        {"label": "A", "value": 10},
        {"label": "B", "value": 20},
        {"label": "C", "value": 5}
    ]
    plot = TreeMap("Test Tree", data)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert 'alt="Test Tree"' in html

def test_network_graph_render():
    """Test functionality: network graph render."""
    nodes = ["A", "B", "C"]
    edges = [("A", "B"), ("B", "C"), ("C", "A")]
    plot = NetworkGraph("Test Net", nodes, edges)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert 'alt="Test Net"' in html

def test_heatmap_table_component():
    """Test functionality: heatmap table component."""
    headers = ["Col A", "Col B"]
    rows = [
        [10, 20],
        [5, 40]
    ]
    table = HeatmapTable(headers=headers, rows=rows, title="Test Heatmap")
    html = str(table)
    assert "Test Heatmap" in html
    assert "Col A" in html
    assert "40" in html  # Check content
    assert "rgba(0, 123, 255" in html  # Check coloring
