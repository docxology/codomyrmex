from codomyrmex.data_visualization.components.alert import Alert
from codomyrmex.data_visualization.components.badge import Badge
from codomyrmex.data_visualization.components.progress import ProgressBar


def test_badge_component():
    """Test functionality: badge component."""
    badge = Badge(label="Success", color="success")
    html = str(badge)
    assert "Success" in html
    assert "background-color: #5cb85c" in html

def test_alert_component():
    """Test functionality: alert component."""
    alert = Alert(message="Warning!", level="warning")
    html = str(alert)
    assert "Warning!" in html
    assert "background-color: #fcf8e3" in html

def test_progress_bar():
    """Test functionality: progress bar."""
    bar = ProgressBar(value=50, max_value=100, label="Halfway")
    html = str(bar)
    assert "width: 50.0%" in html
    assert "Halfway" in html
