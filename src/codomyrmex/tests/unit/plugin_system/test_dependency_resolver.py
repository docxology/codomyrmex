"""Unit tests for DependencyResolver.

Pure-Python module — no external dependencies, no skip guards needed.
Tests cover: empty graph, linear chains, cycles, missing deps, conflicts,
add_many, clear, get, node_count.
"""

import pytest

from codomyrmex.plugin_system.dependency_resolver import (
    DependencyNode,
    DependencyResolver,
    ResolutionResult,
    ResolutionStatus,
)


@pytest.mark.unit
class TestDependencyNode:
    """Tests for DependencyNode dataclass."""

    def test_minimal_node(self):
        """Node with only a name uses sensible defaults."""
        node = DependencyNode("auth")
        assert node.name == "auth"
        assert node.version == "0.0.0"
        assert node.dependencies == []
        assert node.optional_dependencies == []
        assert node.conflicts == []

    def test_node_with_all_fields(self):
        """Node accepts all optional fields."""
        node = DependencyNode(
            name="web",
            version="1.2.3",
            dependencies=["auth", "db"],
            optional_dependencies=["cache"],
            conflicts=["legacy-web"],
        )
        assert node.version == "1.2.3"
        assert "auth" in node.dependencies
        assert "db" in node.dependencies
        assert "cache" in node.optional_dependencies
        assert "legacy-web" in node.conflicts


@pytest.mark.unit
class TestResolutionResult:
    """Tests for ResolutionResult dataclass defaults."""

    def test_defaults_are_empty(self):
        result = ResolutionResult(status=ResolutionStatus.RESOLVED)
        assert result.load_order == []
        assert result.missing == []
        assert result.circular == []
        assert result.conflicts == []


@pytest.mark.unit
class TestDependencyResolverBasic:
    """Basic DependencyResolver operations."""

    def test_empty_resolver(self):
        """Empty resolver resolves to empty load order."""
        r = DependencyResolver()
        assert r.node_count == 0
        result = r.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        assert result.load_order == []

    def test_single_node_no_deps(self):
        """Single node with no dependencies resolves immediately."""
        r = DependencyResolver()
        r.add(DependencyNode("db"))
        result = r.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        assert result.load_order == ["db"]

    def test_get_registered_node(self):
        """get() returns registered node by name."""
        r = DependencyResolver()
        node = DependencyNode("auth")
        r.add(node)
        assert r.get("auth") is node

    def test_get_missing_node_returns_none(self):
        """get() returns None for unknown names."""
        r = DependencyResolver()
        assert r.get("nonexistent") is None

    def test_node_count_reflects_registered_nodes(self):
        """node_count updates as nodes are added."""
        r = DependencyResolver()
        assert r.node_count == 0
        r.add(DependencyNode("a"))
        assert r.node_count == 1
        r.add(DependencyNode("b"))
        assert r.node_count == 2

    def test_add_many(self):
        """add_many registers multiple nodes at once."""
        r = DependencyResolver()
        nodes = [DependencyNode("a"), DependencyNode("b"), DependencyNode("c")]
        r.add_many(nodes)
        assert r.node_count == 3
        for name in ("a", "b", "c"):
            assert r.get(name) is not None

    def test_clear_removes_all_nodes(self):
        """clear() resets the resolver to empty state."""
        r = DependencyResolver()
        r.add_many([DependencyNode("x"), DependencyNode("y")])
        r.clear()
        assert r.node_count == 0
        result = r.resolve()
        assert result.load_order == []

    def test_add_overwrites_existing_node(self):
        """Adding a node with the same name replaces the old entry."""
        r = DependencyResolver()
        r.add(DependencyNode("db", version="1.0.0"))
        r.add(DependencyNode("db", version="2.0.0"))
        assert r.node_count == 1
        assert r.get("db").version == "2.0.0"


@pytest.mark.unit
class TestDependencyResolverLoadOrder:
    """Tests that verify correct topological ordering."""

    def test_linear_chain_orders_dependencies_first(self):
        """B depends on A → load order must be [A, B]."""
        r = DependencyResolver()
        r.add(DependencyNode("B", dependencies=["A"]))
        r.add(DependencyNode("A"))
        result = r.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        assert result.load_order.index("A") < result.load_order.index("B")

    def test_diamond_dependency(self):
        """Diamond: D→B→A, D→C→A resolves with A first, D last."""
        r = DependencyResolver()
        r.add(DependencyNode("A"))
        r.add(DependencyNode("B", dependencies=["A"]))
        r.add(DependencyNode("C", dependencies=["A"]))
        r.add(DependencyNode("D", dependencies=["B", "C"]))
        result = r.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        order = result.load_order
        assert order.index("A") < order.index("B")
        assert order.index("A") < order.index("C")
        assert order.index("B") < order.index("D")
        assert order.index("C") < order.index("D")

    def test_independent_nodes_all_included(self):
        """Nodes with no mutual dependency all appear in load order."""
        r = DependencyResolver()
        r.add_many([DependencyNode("x"), DependencyNode("y"), DependencyNode("z")])
        result = r.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        assert set(result.load_order) == {"x", "y", "z"}

    def test_deep_chain(self):
        """Chain of 5: E→D→C→B→A resolves from A to E."""
        chain = ["A", "B", "C", "D", "E"]
        r = DependencyResolver()
        for i, name in enumerate(chain):
            deps = [chain[i - 1]] if i > 0 else []
            r.add(DependencyNode(name, dependencies=deps))
        result = r.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        for i in range(len(chain) - 1):
            assert result.load_order.index(chain[i]) < result.load_order.index(
                chain[i + 1]
            )


@pytest.mark.unit
class TestDependencyResolverErrors:
    """Tests that verify error conditions are reported correctly."""

    def test_missing_dependency_reported(self):
        """Requiring an unregistered plugin → MISSING status."""
        r = DependencyResolver()
        r.add(DependencyNode("web", dependencies=["db"]))
        # "db" is not registered
        result = r.resolve()
        assert result.status == ResolutionStatus.MISSING
        assert "db" in result.missing

    def test_multiple_missing_dependencies(self):
        """All unregistered dependencies are listed in missing."""
        r = DependencyResolver()
        r.add(DependencyNode("app", dependencies=["auth", "db", "cache"]))
        result = r.resolve()
        assert result.status == ResolutionStatus.MISSING
        assert set(result.missing) == {"auth", "db", "cache"}

    def test_circular_dependency_detected(self):
        """A→B→A circular dependency → CIRCULAR status."""
        r = DependencyResolver()
        r.add(DependencyNode("A", dependencies=["B"]))
        r.add(DependencyNode("B", dependencies=["A"]))
        result = r.resolve()
        assert result.status == ResolutionStatus.CIRCULAR
        assert len(result.circular) > 0

    def test_three_node_cycle(self):
        """A→B→C→A cycle → CIRCULAR with cycle members listed."""
        r = DependencyResolver()
        r.add(DependencyNode("A", dependencies=["B"]))
        r.add(DependencyNode("B", dependencies=["C"]))
        r.add(DependencyNode("C", dependencies=["A"]))
        result = r.resolve()
        assert result.status == ResolutionStatus.CIRCULAR
        # All three nodes should appear in at least one cycle
        all_cycle_nodes = {n for cycle in result.circular for n in cycle}
        assert all_cycle_nodes.issuperset({"A", "B", "C"})

    def test_conflict_detected(self):
        """Plugin declaring a conflict with a present plugin → CONFLICT status."""
        r = DependencyResolver()
        r.add(DependencyNode("new-auth", conflicts=["old-auth"]))
        r.add(DependencyNode("old-auth"))
        result = r.resolve()
        assert result.status == ResolutionStatus.CONFLICT
        assert len(result.conflicts) > 0

    def test_conflict_not_triggered_when_target_absent(self):
        """Conflict with an absent plugin is not reported."""
        r = DependencyResolver()
        r.add(DependencyNode("new-auth", conflicts=["old-auth"]))
        # "old-auth" is NOT registered
        result = r.resolve()
        assert result.status == ResolutionStatus.RESOLVED

    def test_missing_takes_precedence_over_cycle(self):
        """Missing dependency check runs before cycle detection."""
        r = DependencyResolver()
        r.add(DependencyNode("A", dependencies=["B", "external"]))
        r.add(DependencyNode("B", dependencies=["A"]))
        # "external" is not registered → should report MISSING first
        result = r.resolve()
        assert result.status == ResolutionStatus.MISSING
