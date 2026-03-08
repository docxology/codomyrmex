"""Tests for codomyrmex.utils.graph module."""

import pytest

from codomyrmex.utils.graph import kahn_topological_sort


@pytest.mark.unit
class TestKahnTopologicalSort:
    """Tests for kahn_topological_sort function."""

    def test_basic_linear_dependency(self):
        """Test simple linear dependency: A -> B -> C"""
        nodes = ["A", "B", "C"]
        deps = {"B": ["A"], "C": ["B"], "A": []}

        def get_deps(node):
            return deps.get(node, [])

        result = kahn_topological_sort(nodes, get_deps)
        assert result == ["A", "B", "C"]

    def test_diamond_dependency(self):
        """Test diamond dependency: A -> B, A -> C, B -> D, C -> D"""
        nodes = ["A", "B", "C", "D"]
        # D depends on B and C, B depends on A, C depends on A
        deps = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}

        def get_deps(node):
            return deps.get(node, [])

        result = kahn_topological_sort(nodes, get_deps)

        # A must be first, D must be last. B and C can be in any order in between.
        assert result[0] == "A"
        assert result[-1] == "D"
        assert set(result[1:3]) == {"B", "C"}
        assert len(result) == 4

    def test_independent_nodes(self):
        """Test nodes with no dependencies."""
        nodes = ["A", "B", "C"]

        def get_deps(node):
            return []

        result = kahn_topological_sort(nodes, get_deps)
        assert set(result) == {"A", "B", "C"}
        assert len(result) == 3

    def test_cycle_detection_simple(self):
        """Test that a simple cycle raises ValueError."""
        nodes = ["A", "B"]
        # A -> B -> A
        deps = {"B": ["A"], "A": ["B"]}

        def get_deps(node):
            return deps.get(node, [])

        with pytest.raises(ValueError, match="Cycle detected"):
            kahn_topological_sort(nodes, get_deps)

    def test_cycle_detection_complex(self):
        """Test that a larger cycle is detected."""
        nodes = ["A", "B", "C", "D"]
        # A -> B -> C -> A, D -> C
        deps = {"B": ["A"], "C": ["B"], "A": ["C"], "D": ["C"]}

        def get_deps(node):
            return deps.get(node, [])

        with pytest.raises(ValueError, match="Cycle detected"):
            kahn_topological_sort(nodes, get_deps)

    def test_empty_graph(self):
        """Test with empty nodes list."""
        nodes = []

        def get_deps(node):
            return []

        result = kahn_topological_sort(nodes, get_deps)
        assert result == []

    def test_unknown_dependency_ignored(self):
        """Test that dependencies not in the node list are ignored."""
        nodes = ["A", "B"]
        # B depends on A and some unknown 'Z'
        deps = {"B": ["A", "Z"], "A": []}

        def get_deps(node):
            return deps.get(node, [])

        result = kahn_topological_sort(nodes, get_deps)
        assert result == ["A", "B"]

    def test_disconnected_components(self):
        """Test graph with disconnected components."""
        nodes = ["A", "B", "C", "D"]
        # A -> B and C -> D (two separate chains)
        deps = {"B": ["A"], "D": ["C"], "A": [], "C": []}

        def get_deps(node):
            return deps.get(node, [])

        result = kahn_topological_sort(nodes, get_deps)

        # A before B, C before D
        assert result.index("A") < result.index("B")
        assert result.index("C") < result.index("D")
        assert len(result) == 4
