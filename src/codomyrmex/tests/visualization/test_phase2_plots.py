import pytest
from codomyrmex.data_visualization.plots.violin import ViolinPlot
from codomyrmex.data_visualization.plots.radar import RadarChart
from codomyrmex.data_visualization.plots.candlestick import CandlestickChart
from codomyrmex.data_visualization.plots.gantt import GanttChart

def test_violin_plot_render():
    data = [[1, 2, 3], [2, 3, 4]]
    plot = ViolinPlot("Test Violin", data, labels=['G1', 'G2'])
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert 'alt="Test Violin"' in html

def test_radar_chart_render():
    categories = ['A', 'B', 'C']
    values = [4, 5, 3]
    plot = RadarChart("Test Radar", categories, values)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert 'alt="Test Radar"' in html

def test_candlestick_chart_render():
    dates = ["2023-01-01", "2023-01-02"]
    opens = [10, 11]
    highs = [12, 13]
    lows = [9, 10]
    closes = [11, 12]
    plot = CandlestickChart("Test Candle", dates, opens, highs, lows, closes)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert 'alt="Test Candle"' in html

def test_gantt_chart_render():
    tasks = ["Task 1", "Task 2"]
    starts = [1, 2]
    durations = [3, 2]
    plot = GanttChart("Test Gantt", tasks, starts, durations)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert 'alt="Test Gantt"' in html
