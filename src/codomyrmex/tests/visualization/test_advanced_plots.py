import pytest
from codomyrmex.visualization.plots.histogram import Histogram
from codomyrmex.visualization.plots.pie import PieChart
from codomyrmex.visualization.plots.box import BoxPlot
from codomyrmex.visualization.plots.area import AreaPlot

def test_histogram_render():
    data = [1, 2, 2, 3, 3, 3]
    plot = Histogram("Test Hist", data, bins=3)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert "alt=\"Test Hist\"" in html

def test_pie_chart_render():
    labels = ['A', 'B']
    sizes = [30, 70]
    plot = PieChart("Test Pie", labels, sizes)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert "alt=\"Test Pie\"" in html

def test_box_plot_render():
    data = [[1, 2, 3], [2, 3, 4]]
    plot = BoxPlot("Test Box", data, labels=['G1', 'G2'])
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert "alt=\"Test Box\"" in html
    
def test_area_plot_render():
    x = [1, 2, 3]
    y = [10, 20, 15]
    plot = AreaPlot("Test Area", x, y)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert "alt=\"Test Area\"" in html
