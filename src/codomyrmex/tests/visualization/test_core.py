import pytest
from pathlib import Path
from codomyrmex.data_visualization.core.theme import Theme
from codomyrmex.data_visualization.core.layout import Grid, Section
from codomyrmex.data_visualization.core.export import render_html

def test_theme_generation():
    theme = Theme(primary="red", background="black")
    css = theme.css
    assert "color: red" in css
    assert "background-color: black" in css

def test_grid_layout():
    grid = Grid(columns=3)
    grid.add_section("Test Section", "Content")
    assert len(grid.sections) == 1
    assert grid.sections[0].width == "33%"
    
    grid.add_section("Full Width", "Content", full_width=True)
    assert grid.sections[1].width == "100%"

def test_export_html(tmp_path):
    grid = Grid()
    grid.add_section("Test", "<h1>Hello</h1>")
    
    out_file = tmp_path / "test_report.html"
    result_path = render_html(grid, "Test Report", out_file)
    
    assert Path(result_path).exists()
    content = Path(result_path).read_text()
    assert "<h1>Hello</h1>" in content
    assert "Test Report" in content
