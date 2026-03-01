"""Tests for the visualizer module."""

from pathlib import Path

from src.visualizer import DataVisualizer, ChartConfig


class TestChartConfig:
    """Tests for the ChartConfig dataclass."""
    
    def test_defaults(self):
        """Test default values."""
        config = ChartConfig(title="Test Chart")
        
        assert config.title == "Test Chart"
        assert config.chart_type == "bar"
        assert config.theme == "dark"
        assert config.output_format == "html"
        
    def test_is_interactive(self):
        """Test interactivity detection."""
        html_config = ChartConfig(title="Test", output_format="html")
        png_config = ChartConfig(title="Test", output_format="png")
        
        assert html_config.is_interactive is True
        assert png_config.is_interactive is False


class TestDataVisualizer:
    """Tests for the DataVisualizer class."""
    
    def test_initialization(self, output_directory: Path):
        """Test visualizer initialization."""
        visualizer = DataVisualizer(output_dir=output_directory)
        
        assert visualizer.output_dir == output_directory
        assert output_directory.exists()
        
    def test_initialization_creates_directory(self, tmp_path: Path):
        """Test that initialization creates output directory."""
        output_dir = tmp_path / "new" / "nested" / "dir"
        visualizer = DataVisualizer(output_dir=output_dir)
        
        assert output_dir.exists()
        
    def test_create_dashboard(self, output_directory: Path, sample_analysis_results: dict):
        """Test dashboard creation."""
        visualizer = DataVisualizer(output_dir=output_directory)
        
        dashboard_path = visualizer.create_dashboard(sample_analysis_results)
        
        assert dashboard_path.exists()
        assert dashboard_path.suffix == ".html"
        
        content = dashboard_path.read_text()
        assert "<!DOCTYPE html>" in content
        assert "dashboard" in content.lower() or "analysis" in content.lower()
        
    def test_dashboard_contains_metrics(self, output_directory: Path, sample_analysis_results: dict):
        """Test that dashboard contains metrics from results."""
        visualizer = DataVisualizer(output_dir=output_directory)
        dashboard_path = visualizer.create_dashboard(sample_analysis_results)
        
        content = dashboard_path.read_text()
        
        # Should contain summary metrics
        assert "2" in content  # total_files
        assert "80" in content  # total_lines
        
    def test_visualize_metrics(self, output_directory: Path):
        """Test metrics visualization."""
        visualizer = DataVisualizer(output_dir=output_directory)
        metrics = {"lines": 100, "functions": 10, "classes": 2}
        config = ChartConfig(title="Test Metrics")
        
        path = visualizer.visualize_metrics(metrics, config)
        
        assert path.exists()
        assert path.suffix == ".html"
        
    def test_empty_results_handling(self, output_directory: Path):
        """Test handling of empty results."""
        visualizer = DataVisualizer(output_dir=output_directory)
        
        dashboard_path = visualizer.create_dashboard({})
        
        assert dashboard_path.exists()
        content = dashboard_path.read_text()
        assert "<!DOCTYPE html>" in content
