"""Tests for the data_visualization.generate_report() top-level function."""

from pathlib import Path

import pytest

from codomyrmex.data_visualization import generate_report


@pytest.mark.unit
class TestGenerateReport:
    """Tests for the generate_report() convenience function."""

    def test_generates_html_file(self, tmp_path):
        """generate_report creates a file at the returned path."""
        path = generate_report(str(tmp_path))
        assert Path(path).exists()

    def test_returns_string_path(self, tmp_path):
        """generate_report returns a str, not a Path object."""
        path = generate_report(str(tmp_path))
        assert isinstance(path, str)

    def test_default_report_type_creates_general(self, tmp_path):
        """Default report_type produces 'general_report.html'."""
        path = generate_report(str(tmp_path))
        assert Path(path).name == "general_report.html"

    def test_output_filename_matches_report_type(self, tmp_path):
        """report_type is reflected in the output filename."""
        path = generate_report(str(tmp_path), report_type="finance")
        assert Path(path).name == "finance_report.html"
        assert Path(path).exists()

    def test_file_contains_dashboard_content(self, tmp_path):
        """Generated file contains expected dashboard title."""
        path = generate_report(str(tmp_path))
        html = Path(path).read_text()
        assert "Codomyrmex Executive Dashboard" in html

    def test_output_dir_created_if_missing(self, tmp_path):
        """generate_report creates output_dir if it does not exist."""
        new_dir = tmp_path / "subdir" / "nested"
        path = generate_report(str(new_dir))
        assert Path(path).exists()

    def test_multiple_report_types(self, tmp_path):
        """All four supported report types can be generated."""
        for report_type in ("general", "finance", "marketing", "logistics"):
            path = generate_report(str(tmp_path), report_type=report_type)
            assert Path(path).exists(), f"{report_type} report not generated"
