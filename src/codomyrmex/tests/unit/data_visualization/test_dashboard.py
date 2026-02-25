from pathlib import Path

from codomyrmex.data_visualization import generate_report


def test_report_generation(tmp_path):
    """Test functionality: report generation."""
    path = generate_report(str(tmp_path))
    assert Path(path).exists()
    assert "Codomyrmex Executive Dashboard" in Path(path).read_text()
