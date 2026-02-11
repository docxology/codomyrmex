import pytest
from codomyrmex.visualization.plots.scatter import ScatterPlot
from codomyrmex.visualization.plots.heatmap import Heatmap
from codomyrmex.visualization.plots.mermaid import MermaidDiagram

def test_scatterplot_render():
    plot = ScatterPlot("Test Plot", [1, 2, 3], [4, 5, 6])
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert "alt=\"Test Plot\"" in html

def test_heatmap_render():
    data = [[1, 2], [3, 4]]
    plot = Heatmap("Heatmap Test", data)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert "alt=\"Heatmap Test\"" in html

def test_mermaid_render():
    definition = "graph TD; A-->B;"
    plot = MermaidDiagram("Flowchart", definition)
    html = plot.to_html()
    assert '<div class="mermaid">graph TD; A-->B;</div>' in html
