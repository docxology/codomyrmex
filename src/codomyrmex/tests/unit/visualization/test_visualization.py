"""Tests for the visualization module.

Tests cover:
- Module import and __all__ exports
- Theme creation and CSS generation
- Theme to_dict serialization
- Grid construction and section addition
- Dashboard construction with title and theme
- Card component rendering
- Table component rendering
- TextBlock component rendering
- CodeBlock component rendering
- Report subclass save mechanism
- BarPlot construction
- ScatterPlot construction
"""

import pytest

from codomyrmex.data_visualization import (
    BarPlot,
    Card,
    Dashboard,
    GeneralSystemReport,
    Grid,
    ScatterPlot,
    Table,
    Theme,
)
from codomyrmex.data_visualization.components.text import CodeBlock, TextBlock
from codomyrmex.data_visualization.core.theme import DEFAULT_THEME


@pytest.mark.unit
def test_module_import():
    """visualization module is importable."""
    import codomyrmex.data_visualization as visualization
    assert hasattr(visualization, "__all__")


@pytest.mark.unit
def test_module_exports():
    """visualization __all__ contains key classes."""
    import codomyrmex.data_visualization as visualization
    assert "Dashboard" in visualization.__all__
    assert "Grid" in visualization.__all__
    assert "Theme" in visualization.__all__
    assert "BarPlot" in visualization.__all__
    assert "ScatterPlot" in visualization.__all__


# --- Theme Tests ---


@pytest.mark.unit
def test_theme_defaults():
    """Theme has sensible default colors."""
    theme = Theme()
    assert theme.primary == "#2c3e50"
    assert theme.background == "#ecf0f1"
    assert theme.font_family == "'Segoe UI', sans-serif"


@pytest.mark.unit
def test_theme_css_generation():
    """Theme.css generates valid CSS string."""
    theme = Theme(primary="#ff0000", accent="#00ff00")
    css = theme.css
    assert "#ff0000" in css
    assert "#00ff00" in css
    assert "body" in css


@pytest.mark.unit
def test_theme_to_dict():
    """Theme.to_dict returns all fields."""
    theme = Theme()
    d = theme.to_dict()
    assert d["primary"] == "#2c3e50"
    assert d["secondary"] == "#95a5a6"
    assert "font_family" in d


@pytest.mark.unit
def test_default_theme_exists():
    """DEFAULT_THEME singleton is available."""
    assert isinstance(DEFAULT_THEME, Theme)
    assert DEFAULT_THEME.primary == "#2c3e50"


# --- Grid Tests ---


@pytest.mark.unit
def test_grid_construction():
    """Grid starts with default columns and no sections."""
    grid = Grid()
    assert grid.columns == 2
    assert grid.sections == []


@pytest.mark.unit
def test_grid_add_section():
    """Grid.add_section appends a Section."""
    grid = Grid(columns=3)
    grid.add_section("Test Section", "Content here", description="A description")
    assert len(grid.sections) == 1
    assert grid.sections[0].title == "Test Section"
    assert grid.sections[0].description == "A description"


@pytest.mark.unit
def test_grid_full_width_section():
    """Grid full_width section has 100% width."""
    grid = Grid()
    grid.add_section("Wide", "Wide content", full_width=True)
    assert grid.sections[0].width == "100%"


# --- Dashboard Tests ---


@pytest.mark.unit
def test_dashboard_construction():
    """Dashboard initializes with title, theme, and empty grid."""
    dash = Dashboard(title="Test Dash")
    assert dash.title == "Test Dash"
    assert isinstance(dash.theme, Theme)
    assert isinstance(dash.grid, Grid)
    assert dash.grid.sections == []


@pytest.mark.unit
def test_dashboard_add_section():
    """Dashboard.add_section delegates to its grid."""
    dash = Dashboard()
    dash.add_section("Metrics", "Some data")
    assert len(dash.grid.sections) == 1


# --- Component Tests ---


@pytest.mark.unit
def test_card_component():
    """Card renders title and value into HTML."""
    card = Card(title="Users", value=42, description="Active users")
    html = str(card)
    assert "Users" in html
    assert "42" in html
    assert "Active users" in html


@pytest.mark.unit
def test_table_component():
    """Table renders headers and rows into HTML."""
    table = Table(headers=["Name", "Age"], rows=[["Alice", 30], ["Bob", 25]])
    html = str(table)
    assert "Name" in html
    assert "Age" in html
    assert "Alice" in html
    assert "30" in html


@pytest.mark.unit
def test_text_block_plain():
    """TextBlock renders plain text."""
    block = TextBlock(content="Hello world")
    html = str(block)
    assert "Hello world" in html
    assert "component-text" in html


@pytest.mark.unit
def test_text_block_markdown():
    """TextBlock with markdown flag renders differently."""
    block = TextBlock(content="Line one\nLine two", is_markdown=True)
    html = str(block)
    assert "markdown" in html


@pytest.mark.unit
def test_code_block():
    """CodeBlock renders code with language class."""
    block = CodeBlock(code="print('hi')", language="python")
    html = str(block)
    assert "language-python" in html
    assert "print" in html


# --- Plot Tests ---


@pytest.mark.unit
def test_bar_plot_construction():
    """BarPlot initializes with categories and values."""
    plot = BarPlot(
        title="Sales",
        categories=["Q1", "Q2", "Q3"],
        values=[100, 200, 150],
    )
    assert plot.title == "Sales"
    assert plot.data["x"] == ["Q1", "Q2", "Q3"]
    assert plot.data["y"] == [100, 200, 150]


@pytest.mark.unit
def test_scatter_plot_construction():
    """ScatterPlot initializes with x and y data."""
    plot = ScatterPlot(
        title="Correlation",
        x_data=[1.0, 2.0, 3.0],
        y_data=[4.0, 5.0, 6.0],
        x_label="Feature A",
        y_label="Feature B",
    )
    assert plot.title == "Correlation"
    assert plot.x_label == "Feature A"
    assert plot.y_label == "Feature B"
    assert plot.data["x"] == [1.0, 2.0, 3.0]


# --- Report Tests ---


@pytest.mark.unit
def test_general_report_construction():
    """GeneralSystemReport initializes with dashboard."""
    report = GeneralSystemReport()
    assert isinstance(report.dashboard, Dashboard)
    assert report.dashboard.title == "Codomyrmex Executive Dashboard"


@pytest.mark.unit
def test_general_report_generate():
    """GeneralSystemReport.generate populates dashboard sections."""
    report = GeneralSystemReport()
    report.generate()
    assert len(report.dashboard.grid.sections) > 0
