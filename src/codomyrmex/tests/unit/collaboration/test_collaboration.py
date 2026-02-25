"""Unit tests for collaboration module."""
import pytest

from codomyrmex.collaboration import AgentProxy, SwarmManager, TaskDecomposer


@pytest.mark.unit
def test_swarm_execution():
    """Test mission distribution across a swarm of agents."""
    manager = SwarmManager()
    agent1 = AgentProxy("A1", "Builder")
    agent2 = AgentProxy("A2", "Reviewer")

    manager.add_agent(agent1)
    manager.add_agent(agent2)

    results = manager.execute("Build a feature")

    assert len(results) == 2
    assert "A1" in results
    assert "A2" in results
    assert results["A1"] == "Result from A1"
    assert results["A2"] == "Result from A2"

@pytest.mark.unit
def test_task_decomposition():
    """Test mission splitting."""
    tasks = TaskDecomposer.decompose("Design and Build")
    assert len(tasks) == 2
    assert "Design" in tasks
    assert "Build" in tasks

@pytest.mark.unit
def test_consensus():
    """Test voting logic."""
    manager = SwarmManager()
    manager.add_agent(AgentProxy("A1", "Voter"))
    manager.add_agent(AgentProxy("A2", "Voter"))
    manager.add_agent(AgentProxy("A3", "Voter"))

    # Majority vote
    assert manager.consensus_vote("Upgrade") is True


# Coverage push — collaboration/coordination
class TestTaskManagerImport:
    """Tests for collaboration task manager import."""

    def test_import(self):
        from codomyrmex.collaboration.coordination.task_manager import TaskManager
        assert TaskManager is not None


# Phase 2b — collaboration/coordination/task_manager
class TestDependencyGraph:
    """Tests for DependencyGraph."""

    def test_init(self):
        from codomyrmex.collaboration.coordination.task_manager import DependencyGraph
        g = DependencyGraph()
        assert g is not None

    def test_add_and_get_deps(self):
        from codomyrmex.collaboration.coordination.task_manager import DependencyGraph
        from codomyrmex.collaboration.models import Task
        g = DependencyGraph()
        t = Task(name="build", dependencies=["compile"])
        g.add_task(t)
        deps = g.get_dependencies(t.id)
        assert isinstance(deps, set)

    def test_has_cycle_no_cycle(self):
        from codomyrmex.collaboration.coordination.task_manager import DependencyGraph
        from codomyrmex.collaboration.models import Task
        g = DependencyGraph()
        t1 = Task(name="a")
        t2 = Task(name="b", dependencies=[t1.id])
        g.add_task(t1)
        g.add_task(t2)
        assert g.has_cycle() is False

    def test_get_ready_tasks(self):
        from codomyrmex.collaboration.coordination.task_manager import DependencyGraph
        from codomyrmex.collaboration.models import Task
        g = DependencyGraph()
        t1 = Task(name="a")
        t2 = Task(name="b", dependencies=[t1.id])
        g.add_task(t1)
        g.add_task(t2)
        ready = g.get_ready_tasks(completed=set())
        assert t1.id in ready


class TestTaskManagerDeep:
    """Deep execution tests for TaskManager."""

    def test_init(self):
        from codomyrmex.collaboration.coordination.task_manager import TaskManager
        tm = TaskManager()
        assert tm is not None

    def test_scheduling_strategy_enum(self):
        from codomyrmex.collaboration.coordination.task_manager import SchedulingStrategy
        assert len(list(SchedulingStrategy)) > 0


class TestTaskQueue:
    """Tests for TaskQueue."""

    def test_init(self):
        from codomyrmex.collaboration.coordination.task_manager import TaskQueue
        q = TaskQueue()
        assert q is not None
