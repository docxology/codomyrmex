import pytest
from pathlib import Path
from codomyrmex.data_visualization.core.theme import Theme
from codomyrmex.data_visualization.core.layout import Grid, Section
from codomyrmex.data_visualization.core.export import render_html

def test_theme_generation():
    """Test functionality: theme generation."""
    theme = Theme(primary="red", background="black")
    css = theme.css
    assert "--primary: red" in css
    assert "--bg: black" in css

def test_grid_layout():
    """Test functionality: grid layout."""
    grid = Grid(columns=3)
    grid.add_section("Test Section", "Content")
    assert len(grid.sections) == 1
    assert grid.sections[0].width == f"{100/3}%"

    grid.add_section("Full Width", "Content", full_width=True)
    assert grid.sections[1].width == "100%"

def test_export_html(tmp_path):
    """Test functionality: export html."""
    out_file = tmp_path / "test_report.html"
    html = render_html("<h1>Hello</h1>", title="Test Report", output_path=out_file)

    assert Path(out_file).exists()
    content = Path(out_file).read_text()
    assert "<h1>Hello</h1>" in content
    assert "Test Report" in content
