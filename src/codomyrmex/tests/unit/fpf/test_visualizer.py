"""Tests for FPF visualizer."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from codomyrmex.fpf import FPFVisualizer, FPFSpec, Pattern, PatternStatus


def test_visualizer_initialization():
    """Test visualizer initialization."""
    visualizer = FPFVisualizer()
    assert visualizer is not None


def test_visualize_pattern_hierarchy():
    """Test pattern hierarchy visualization."""
    visualizer = FPFVisualizer()
    patterns = [
        Pattern(
            id="A.1",
            title="Pattern 1",
            status=PatternStatus.STABLE,
            dependencies={"builds_on": ["A.0"]},
            content="",
        ),
        Pattern(
            id="A.0",
            title="Pattern 0",
            status=PatternStatus.STABLE,
            content="",
        ),
    ]
    
    diagram = visualizer.visualize_pattern_hierarchy(patterns)
    assert isinstance(diagram, str)
    assert "graph TD" in diagram or "graph" in diagram


def test_visualize_dependencies():
    """Test dependency visualization."""
    visualizer = FPFVisualizer()
    patterns = [
        Pattern(
            id="A.1",
            title="Pattern 1",
            status=PatternStatus.STABLE,
            dependencies={"builds_on": ["A.0"]},
            content="",
        ),
    ]
    
    diagram = visualizer.visualize_dependencies(patterns)
    assert isinstance(diagram, str)
    assert "graph" in diagram


def test_generate_report():
    """Test report generation."""
    visualizer = FPFVisualizer()
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Test Pattern",
                status=PatternStatus.STABLE,
                content="",
                part="A",
            )
        ]
    )
    
    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "report.md"
        visualizer.generate_report(spec, output_path)
        assert output_path.exists()
        content = output_path.read_text()
        assert "FPF Specification Report" in content


def test_create_pattern_card():
    """Test pattern card creation."""
    visualizer = FPFVisualizer()
    pattern = Pattern(
        id="A.1",
        title="Test Pattern",
        status=PatternStatus.STABLE,
        keywords=["test", "pattern"],
        dependencies={"builds_on": ["A.0"]},
        sections={"problem": "Test problem", "solution": "Test solution"},
        content="",
    )
    
    card = visualizer.create_pattern_card(pattern)
    assert isinstance(card, str)
    assert "A.1" in card
    assert "Test Pattern" in card


