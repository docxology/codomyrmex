import pytest
from codomyrmex.data_visualization.components.badge import Badge
from codomyrmex.data_visualization.components.alert import Alert
from codomyrmex.data_visualization.components.progress import ProgressBar

def test_badge_component():
    badge = Badge("Success", "success")
    html = str(badge)
    assert "Success" in html
    assert "background-color: #5cb85c" in html

def test_alert_component():
    alert = Alert("Warning!", "warning")
    html = str(alert)
    assert "Warning!" in html
    assert "background-color: #fcf8e3" in html

def test_progress_bar():
    bar = ProgressBar(50, 100, label="Halfway")
    html = str(bar)
    assert "width: 50.0%" in html
    assert "Halfway" in html
