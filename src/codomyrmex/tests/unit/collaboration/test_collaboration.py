"""Unit tests for collaboration module."""

import warnings

import pytest

# Import from the new canonical path (not the deprecated protocols.swarm)

# Legacy AgentProxy still lives in the compatibility shim; import with suppression
with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    from codomyrmex.collaboration.protocols.swarm import (
        AgentProxy,
        SwarmManager,
        TaskDecomposer,
    )


@pytest.mark.unit
def test_swarm_execution():
    """Test mission distribution across a swarm of agents."""
    manager = SwarmManager()
    agent1 = AgentProxy("A1", "Builder")
    agent2 = AgentProxy("A2", "Reviewer")

    manager.add_agent(agent1)
    manager.add_agent(agent2)
    assert manager.pool.size == 2

    results = manager.execute("Build a feature")

    assert isinstance(results, dict)


@pytest.mark.unit
def test_task_decomposition():
    """Test mission splitting."""
    # Legacy TaskDecomposer is just a shim
    tasks = TaskDecomposer.decompose("Design and Build")
    assert len(tasks) == 2
    assert "Design" in tasks[0]
    assert "Build" in tasks[1]


@pytest.mark.unit
def test_consensus():
    """Test voting logic."""
    manager = SwarmManager()
    # AgentProxy uses register_agent through add_agent shim
    manager.add_agent(AgentProxy("A1", "Voter"))
    manager.add_agent(AgentProxy("A2", "Voter"))
    manager.add_agent(AgentProxy("A3", "Voter"))

    # Majority vote
    assert manager.consensus_vote("Upgrade") is True


class TestDependencyGraph:
    """Tests for DependencyGraph dependency tracking and cycle detection."""

    def test_empty_graph_has_no_ready_tasks(self):
        """An empty graph returns no ready tasks."""
        from codomyrmex.collaboration.coordination.task_manager import DependencyGraph

        g = DependencyGraph()
        assert g.get_ready_tasks(completed=set()) == []

    def test_add_and_get_deps(self):
        """add_task records declared dependencies for later retrieval."""
        from codomyrmex.collaboration.coordination.task_manager import DependencyGraph
        from codomyrmex.collaboration.models import Task

        g = DependencyGraph()
        t = Task(name="build", dependencies=["compile"])
        g.add_task(t)
        deps = g.get_dependencies(t.id)
        assert deps == {"compile"}

    def test_has_cycle_acyclic(self):
        """Linear dependency chain a→b is not a cycle."""
        from codomyrmex.collaboration.coordination.task_manager import DependencyGraph
        from codomyrmex.collaboration.models import Task

        g = DependencyGraph()
        t1 = Task(name="a")
        t2 = Task(name="b", dependencies=[t1.id])
        g.add_task(t1)
        g.add_task(t2)
        assert g.has_cycle() is False

    def test_has_cycle_detects_cycle(self):
        """has_cycle() returns True when a → b → a mutual dependency exists."""
        from codomyrmex.collaboration.coordination.task_manager import DependencyGraph

        g = DependencyGraph()
        # Directly inject a cycle without the Task constructor (which can't encode
        # a cycle since we'd need both IDs before either Task is created).
        g._dependencies["a"] = {"b"}
        g._dependencies["b"] = {"a"}
        g._dependents["b"] = {"a"}
        g._dependents["a"] = {"b"}
        assert g.has_cycle() is True

    def test_get_ready_tasks_respects_deps(self):
        """Only tasks with all dependencies satisfied appear in ready list."""
        from codomyrmex.collaboration.coordination.task_manager import DependencyGraph
        from codomyrmex.collaboration.models import Task

        g = DependencyGraph()
        t1 = Task(name="a")
        t2 = Task(name="b", dependencies=[t1.id])
        g.add_task(t1)
        g.add_task(t2)
        # Before completing t1, only t1 is ready
        ready_before = g.get_ready_tasks(completed=set())
        assert t1.id in ready_before
        assert t2.id not in ready_before
        # After completing t1, t2 becomes ready
        ready_after = g.get_ready_tasks(completed={t1.id})
        assert t2.id in ready_after


class TestTaskManagerDeep:
    """Behavioral tests for TaskManager submit and scheduling strategy."""

    def test_submit_returns_task_id(self):
        """submit() enqueues the task and returns its ID."""
        from codomyrmex.collaboration.coordination.task_manager import TaskManager
        from codomyrmex.collaboration.models import Task

        tm = TaskManager()
        task = Task(name="build")
        task_id = tm.submit(task)
        assert task_id == task.id
        assert len(tm._queue) == 1

    def test_strategy_defaults_to_priority(self):
        """TaskManager defaults to PRIORITY scheduling strategy."""
        from codomyrmex.collaboration.coordination.task_manager import (
            SchedulingStrategy,
            TaskManager,
        )

        tm = TaskManager()
        assert tm._strategy == SchedulingStrategy.PRIORITY

    def test_scheduling_strategy_all_values(self):
        """SchedulingStrategy enum exposes all four expected strategies."""
        from codomyrmex.collaboration.coordination.task_manager import (
            SchedulingStrategy,
        )

        names = {s.name for s in SchedulingStrategy}
        assert {"FIFO", "PRIORITY", "SHORTEST_FIRST", "ROUND_ROBIN"}.issubset(names)


class TestTaskQueue:
    """Tests for TaskQueue priority ordering and basic operations."""

    def test_empty_queue_length_zero(self):
        """A freshly created TaskQueue has length 0."""
        from codomyrmex.collaboration.coordination.task_manager import TaskQueue

        q = TaskQueue()
        assert len(q) == 0
        assert not q  # __bool__ returns False when empty

    def test_push_pop_priority_ordering(self):
        """TaskQueue pops the highest-priority task first."""
        from codomyrmex.collaboration.coordination.task_manager import TaskQueue
        from codomyrmex.collaboration.models import Task

        q = TaskQueue()
        low = Task(name="low-priority", priority=1)
        high = Task(name="high-priority", priority=10)
        q.push(low)
        q.push(high)
        assert len(q) == 2
        popped = q.pop()
        assert popped is not None
        assert popped.priority == 10  # max-heap: higher priority dequeued first

    def test_peek_does_not_remove(self):
        """peek() returns the top item without removing it."""
        from codomyrmex.collaboration.coordination.task_manager import TaskQueue
        from codomyrmex.collaboration.models import Task

        q = TaskQueue()
        t = Task(name="work")
        q.push(t)
        peeked = q.peek()
        assert peeked is not None
        assert peeked.id == t.id
        assert len(q) == 1  # still in queue
