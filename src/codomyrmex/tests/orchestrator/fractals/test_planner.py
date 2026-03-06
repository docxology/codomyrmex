"""Tests for pure functions in the fractals planner."""

from codomyrmex.orchestrator.fractals.models import TaskNode
from codomyrmex.orchestrator.fractals.planner import find_task, format_lineage


def test_format_lineage() -> None:
    """Test formatting the recursive task lineage into a readable string limit."""
    lineage = ["Build an app", "Implement backend", "Write tests"]
    current = "Test Auth API"

    out = format_lineage(lineage, current)
    lines = out.split("\n")

    assert len(lines) == 4
    assert lines[0] == "- Build an app"
    assert lines[1] == "  - Implement backend"
    assert lines[2] == "    - Write tests"
    assert lines[3] == "      - Test Auth API (current)"


def test_find_task() -> None:
    """Test finding a specific node deeply nested in the task tree."""
    root = TaskNode(id="1", description="A")
    c1 = TaskNode(id="1.1", description="B")
    c11 = TaskNode(id="1.1.1", description="C")

    c1.children = [c11]
    root.children = [c1]

    assert find_task(root, "1") is root
    assert find_task(root, "1.1") is c1
    assert find_task(root, "1.1.1") is c11
    assert find_task(root, "nonexistent") is None
