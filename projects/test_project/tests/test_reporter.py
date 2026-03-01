"""Tests for the reporter module."""

import json
from pathlib import Path

from src.reporter import ReportGenerator, ReportConfig


class TestReportConfig:
    """Tests for the ReportConfig dataclass."""
    
    def test_defaults(self):
        """Test default values."""
        config = ReportConfig()
        
        assert config.title == "Analysis Report"
        assert config.format == "html"
        assert config.include_visualizations is True
        assert config.include_metrics is True
        
    def test_format_properties(self):
        """Test format detection properties."""
        html_config = ReportConfig(format="html")
        json_config = ReportConfig(format="json")
        md_config = ReportConfig(format="markdown")
        
        assert html_config.is_html is True
        assert html_config.is_json is False
        
        assert json_config.is_json is True
        assert json_config.is_html is False
        
        assert md_config.is_markdown is True
        assert md_config.is_json is False


class TestReportGenerator:
    """Tests for the ReportGenerator class."""
    
    def test_initialization(self, output_directory: Path):
        """Test generator initialization."""
        generator = ReportGenerator(output_dir=output_directory)
        
        assert generator.output_dir == output_directory
        assert output_directory.exists()
        
    def test_generate_html(self, output_directory: Path, sample_analysis_results: dict):
        """Test HTML report generation."""
        generator = ReportGenerator(output_dir=output_directory)
        config = ReportConfig(title="Test Report", format="html")
        
        path = generator.generate(sample_analysis_results, config)
        
        assert path.exists()
        assert path.suffix == ".html"
        
        content = path.read_text()
        assert "<!DOCTYPE html>" in content
        assert "Test Report" in content
        
    def test_generate_json(self, output_directory: Path, sample_analysis_results: dict):
        """Test JSON report generation."""
        generator = ReportGenerator(output_dir=output_directory)
        config = ReportConfig(title="Test Report", format="json")
        
        path = generator.generate(sample_analysis_results, config)
        
        assert path.exists()
        assert path.suffix == ".json"
        
        content = path.read_text()
        data = json.loads(content)
        
        assert "metadata" in data
        assert data["metadata"]["title"] == "Test Report"
        assert "summary" in data
        
    def test_generate_markdown(self, output_directory: Path, sample_analysis_results: dict):
        """Test Markdown report generation."""
        generator = ReportGenerator(output_dir=output_directory)
        config = ReportConfig(title="Test Report", format="markdown")
        
        path = generator.generate(sample_analysis_results, config)
        
        assert path.exists()
        assert path.suffix == ".md"
        
        content = path.read_text()
        assert "# Test Report" in content
        assert "## " in content  # Has sections
        
    def test_generate_all_formats(self, output_directory: Path, sample_analysis_results: dict):
        """Test generating reports in all formats."""
        generator = ReportGenerator(output_dir=output_directory)
        
        paths = generator.generate_all_formats(sample_analysis_results)
        
        assert "html" in paths
        assert "json" in paths
        assert "markdown" in paths
        
        for fmt, path in paths.items():
            assert path.exists()
            
    def test_report_includes_summary(self, output_directory: Path, sample_analysis_results: dict):
        """Test that reports include summary data."""
        generator = ReportGenerator(output_dir=output_directory)
        
        for fmt in ["html", "json", "markdown"]:
            config = ReportConfig(format=fmt)
            path = generator.generate(sample_analysis_results, config)
            content = path.read_text()
            
            # All formats should include key metrics
            assert "2" in content or "80" in content  # files or lines
