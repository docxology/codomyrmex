"""Tests for fractal task models."""

from codomyrmex.orchestrator.fractals.models import TaskNode, TaskStatus
from codomyrmex.orchestrator.fractals.planner import build_tree, propagate_status


def test_build_tree_creates_root_node() -> None:
    """Test that build_tree initializes a valid root node."""
    root = build_tree("Build a web app")

    assert root.id == "1"
    assert root.description == "Build a web app"
    assert root.depth == 0
    assert root.lineage == []
    assert root.status == TaskStatus.PENDING
    assert root.kind is None
    assert root.is_leaf()


def test_task_node_leaf_collection() -> None:
    """Test gathering all leaf nodes representing actionable atomic tasks."""
    root = TaskNode(id="1", description="Root")
    child1 = TaskNode(id="1.1", description="Child 1")
    child2 = TaskNode(id="1.2", description="Child 2")

    # 1.1 has its own children
    grandchild1 = TaskNode(id="1.1.1", description="GC 1")
    grandchild2 = TaskNode(id="1.1.2", description="GC 2")
    child1.children = [grandchild1, grandchild2]

    root.children = [child1, child2]

    # Leaves should be GC1, GC2, and Child2
    leaves = root.get_leaves()
    assert len(leaves) == 3
    assert {leaf.id for leaf in leaves} == {"1.1.1", "1.1.2", "1.2"}


def test_is_subtree_done() -> None:
    """Test subtree completion check."""
    root = TaskNode(id="1", description="Root")
    child1 = TaskNode(id="1.1", description="Child 1", status=TaskStatus.DONE)
    child2 = TaskNode(id="1.2", description="Child 2", status=TaskStatus.DONE)
    root.children = [child1, child2]

    assert root.is_subtree_done()

    child2.status = TaskStatus.RUNNING
    assert not root.is_subtree_done()


def test_propagate_status() -> None:
    """Test propagating statuses from leaves to root."""
    root = TaskNode(id="1", description="Root", status=TaskStatus.PENDING)
    child1 = TaskNode(id="1.1", description="Child 1", status=TaskStatus.DONE)
    child2 = TaskNode(id="1.2", description="Child 2", status=TaskStatus.DONE)
    root.children = [child1, child2]

    propagate_status(root)
    assert root.status == TaskStatus.DONE

    child2.status = TaskStatus.FAILED
    propagate_status(root)
    assert root.status == TaskStatus.FAILED

    child2.status = TaskStatus.RUNNING
    propagate_status(root)
    assert root.status == TaskStatus.RUNNING
