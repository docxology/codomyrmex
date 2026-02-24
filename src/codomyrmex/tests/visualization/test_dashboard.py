from codomyrmex.data_visualization import generate_report
from pathlib import Path

def test_report_generation(tmp_path):
    """Test functionality: report generation."""
    path = generate_report(str(tmp_path))
    assert Path(path).exists()
    assert "Codomyrmex Executive Dashboard" in Path(path).read_text()
