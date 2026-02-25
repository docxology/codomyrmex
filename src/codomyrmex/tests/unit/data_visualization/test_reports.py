from pathlib import Path

from codomyrmex.data_visualization.reports.general import GeneralSystemReport


def test_general_report_generation(tmp_path):
    """Test functionality: general report generation."""
    report = GeneralSystemReport()
    out_file = tmp_path / "system_report.html"

    # Generate and save
    saved_path = report.save(str(out_file))

    assert Path(saved_path).exists()
    content = Path(saved_path).read_text()

    # Check for presence of sections
    assert "Finance: Key Metrics" in content
    assert "Bio-Sim: Population" in content
    assert "Relations: Social Graph" in content
    assert "Education: Learning Path" in content
