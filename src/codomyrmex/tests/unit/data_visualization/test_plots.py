import pytest
from codomyrmex.data_visualization.plots.scatter import ScatterPlot
from codomyrmex.data_visualization.plots.heatmap import Heatmap
from codomyrmex.data_visualization.plots.mermaid import MermaidDiagram

def test_scatterplot_render():
    """Test functionality: scatterplot render."""
    plot = ScatterPlot(title="Test Plot", data=[1, 4, 2, 5, 3, 6])
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert 'alt="Test Plot"' in html

def test_heatmap_render():
    """Test functionality: heatmap render."""
    data = [[1, 2], [3, 4]]
    plot = Heatmap(title="Heatmap Test", data=data)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert 'alt="Heatmap Test"' in html

def test_mermaid_render():
    """Test functionality: mermaid render."""
    definition = "graph TD; A-->B;"
    plot = MermaidDiagram(title="Flowchart", definition=definition)
    html = plot.to_html()
    assert '<div class="mermaid">graph TD; A-->B;</div>' in html
