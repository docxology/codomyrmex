"""Tests for the GeneralSystemReport class in data_visualization.reports."""

from pathlib import Path

import pytest

from codomyrmex.data_visualization.reports.general import GeneralSystemReport


@pytest.mark.unit
class TestGeneralSystemReport:
    """Tests for GeneralSystemReport generation and serialization."""

    def test_generation_creates_file(self, tmp_path):
        """save() creates an HTML file at the given path."""
        report = GeneralSystemReport()
        out_file = tmp_path / "system_report.html"
        saved_path = report.save(str(out_file))
        assert Path(saved_path).exists()

    def test_output_contains_required_sections(self, tmp_path):
        """Generated HTML includes all expected section headings."""
        report = GeneralSystemReport()
        out_file = tmp_path / "report.html"
        saved_path = report.save(str(out_file))
        content = Path(saved_path).read_text()
        assert "Finance: Key Metrics" in content
        assert "Bio-Sim: Population" in content
        assert "Relations: Social Graph" in content
        assert "Education: Learning Path" in content

    def test_save_auto_generates(self, tmp_path):
        """save() calls generate() implicitly when not yet generated."""
        report = GeneralSystemReport()
        out_file = tmp_path / "auto.html"
        # Do NOT call report.generate() — save should do it automatically
        saved_path = report.save(str(out_file))
        assert Path(saved_path).exists()
        assert len(Path(saved_path).read_text()) > 0

    def test_two_fresh_instances_produce_same_output(self, tmp_path):
        """Two independently created reports produce identical HTML."""
        report1 = GeneralSystemReport()
        out1 = tmp_path / "r1.html"
        report1.save(str(out1))

        report2 = GeneralSystemReport()
        out2 = tmp_path / "r2.html"
        report2.save(str(out2))

        assert out1.read_text() == out2.read_text()

    def test_save_returns_string_path(self, tmp_path):
        """save() returns a str, not a Path object."""
        report = GeneralSystemReport()
        result = report.save(str(tmp_path / "out.html"))
        assert isinstance(result, str)

    def test_title_in_output(self, tmp_path):
        """Generated HTML contains the report title."""
        report = GeneralSystemReport()
        out_file = tmp_path / "titled.html"
        report.save(str(out_file))
        content = out_file.read_text()
        assert "Codomyrmex Executive Dashboard" in content
