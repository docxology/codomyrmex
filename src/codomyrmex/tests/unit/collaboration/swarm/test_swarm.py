"""Tests for Sprint 15: Swarm Protocol.

Tests for protocol.py, pool.py, decomposer.py, consensus.py, message_bus.py.
"""

from __future__ import annotations

import pytest

from codomyrmex.collaboration.swarm.consensus import (
    ConsensusEngine,
    ConsensusResult,
    Decision,
    Vote,
)
from codomyrmex.collaboration.swarm.decomposer import (
    CyclicDependencyError,
    SubTask,
    TaskDecomposer,
)
from codomyrmex.collaboration.swarm.message_bus import (
    MessageBus,
)
from codomyrmex.collaboration.swarm.pool import (
    AgentPool,
    AssignmentError,
)
from codomyrmex.collaboration.swarm.protocol import (
    AgentRole,
    SwarmAgent,
    SwarmMessage,
    SwarmMessageType,
    TaskAssignment,
    TaskStatus,
)

# ── Protocol ─────────────────────────────────────────────────────


class TestSwarmMessage:
    """Test suite for SwarmMessage."""

    def test_auto_id(self) -> None:
        """SwarmMessage auto-assigns a non-empty message_id and positive timestamp on construction."""
        msg = SwarmMessage(SwarmMessageType.TASK_ASSIGNMENT, sender="alice")
        assert msg.message_id
        assert msg.timestamp > 0

    def test_to_dict(self) -> None:
        """to_dict() serialises sender, recipient, and message_type to plain dict keys."""
        msg = SwarmMessage(SwarmMessageType.RESULT, sender="bob", recipient="alice")
        d = msg.to_dict()
        assert d["message_type"] == "result"
        assert d["sender"] == "bob"


class TestSwarmAgent:
    """Test suite for SwarmAgent."""

    def test_available(self) -> None:
        """available is True when active_tasks < max_concurrent and False when at capacity."""
        agent = SwarmAgent("a1", AgentRole.CODER, max_concurrent=2)
        assert agent.available
        agent.active_tasks = 2
        assert not agent.available

    def test_load(self) -> None:
        """load returns active_tasks / max_concurrent as a 0.0–1.0 float."""
        agent = SwarmAgent("a1", AgentRole.CODER, max_concurrent=4)
        agent.active_tasks = 2
        assert agent.load == 0.5

    def test_to_dict(self) -> None:
        """to_dict() includes role as string and capabilities as a list."""
        agent = SwarmAgent("a1", AgentRole.REVIEWER, {"python", "security"})
        d = agent.to_dict()
        assert d["role"] == "reviewer"
        assert "python" in d["capabilities"]


class TestTaskAssignment:
    """Test suite for TaskAssignment."""

    def test_auto_id(self) -> None:
        """TaskAssignment auto-assigns a task_id and sets initial status to PENDING."""
        task = TaskAssignment(description="test")
        assert task.task_id
        assert task.status == TaskStatus.PENDING

    def test_to_dict(self) -> None:
        """to_dict() includes required_role as a string value."""
        task = TaskAssignment(description="x", required_role=AgentRole.TESTER)
        d = task.to_dict()
        assert d["required_role"] == "tester"


# ── Pool ─────────────────────────────────────────────────────────


class TestAgentPool:
    """Test suite for AgentPool."""

    def test_register_and_size(self) -> None:
        """size reflects the number of registered agents."""
        pool = AgentPool()
        pool.register(SwarmAgent("a1", AgentRole.CODER))
        assert pool.size == 1

    def test_unregister(self) -> None:
        """unregister removes the agent and returns True; size decrements."""
        pool = AgentPool()
        pool.register(SwarmAgent("a1", AgentRole.CODER))
        assert pool.unregister("a1") is True
        assert pool.size == 0

    def test_assign_by_role(self) -> None:
        """assign selects an agent whose role matches the task required_role."""
        pool = AgentPool()
        pool.register(SwarmAgent("coder1", AgentRole.CODER))
        pool.register(SwarmAgent("reviewer1", AgentRole.REVIEWER))
        task = TaskAssignment(description="code", required_role=AgentRole.CODER)
        agent = pool.assign(task)
        assert agent.agent_id == "coder1"
        assert task.status == TaskStatus.ASSIGNED

    def test_assign_by_capability(self) -> None:
        """assign selects the agent with the required capability when multiple roles match."""
        pool = AgentPool()
        pool.register(SwarmAgent("a1", AgentRole.CODER, {"python"}))
        pool.register(SwarmAgent("a2", AgentRole.CODER, {"javascript"}))
        task = TaskAssignment(
            description="py task",
            required_role=AgentRole.CODER,
            required_capabilities={"python"},
        )
        agent = pool.assign(task)
        assert agent.agent_id == "a1"

    def test_assign_least_loaded(self) -> None:
        """assign selects the least-loaded available agent when capability is equal."""
        pool = AgentPool()
        busy = SwarmAgent("a1", AgentRole.CODER, max_concurrent=5)
        busy.active_tasks = 3
        fresh = SwarmAgent("a2", AgentRole.CODER, max_concurrent=5)
        pool.register(busy)
        pool.register(fresh)
        task = TaskAssignment(required_role=AgentRole.CODER)
        agent = pool.assign(task)
        assert agent.agent_id == "a2"

    def test_assign_no_available(self) -> None:
        """assign raises AssignmentError when all matching agents are at capacity."""
        pool = AgentPool()
        full = SwarmAgent("a1", AgentRole.CODER, max_concurrent=1)
        full.active_tasks = 1
        pool.register(full)
        with pytest.raises(AssignmentError):
            pool.assign(TaskAssignment(required_role=AgentRole.CODER))

    def test_release(self) -> None:
        """release decrements active_tasks for the given agent_id."""
        pool = AgentPool()
        pool.register(SwarmAgent("a1", AgentRole.CODER))
        pool.assign(TaskAssignment(required_role=AgentRole.CODER))
        agent = pool.get("a1")
        assert isinstance(agent, SwarmAgent)
        assert agent.active_tasks == 1
        pool.release("a1")
        assert agent.active_tasks == 0

    def test_status(self) -> None:
        """status() returns totals and a by_role breakdown for the registered agents."""
        pool = AgentPool()
        pool.register(SwarmAgent("a1", AgentRole.CODER))
        pool.register(SwarmAgent("a2", AgentRole.REVIEWER))
        s = pool.status()
        assert s["total"] == 2
        assert "coder" in s["by_role"]


# ── Decomposer ───────────────────────────────────────────────────


class TestSubTask:
    """Test suite for SubTask."""

    def test_auto_id(self) -> None:
        """SubTask auto-assigns a task_id and defaults role to CODER."""
        st = SubTask(description="test")
        assert st.task_id
        assert st.role == AgentRole.CODER

    def test_to_dict(self) -> None:
        """to_dict() serialises role as a string."""
        st = SubTask(description="x", role=AgentRole.TESTER)
        d = st.to_dict()
        assert d["role"] == "tester"


class TestTaskDecomposer:
    """Test suite for TaskDecomposer."""

    def test_decompose_code_task(self) -> None:
        """decompose produces at least one subtask containing a CODER role for a coding description."""
        d = TaskDecomposer()
        subs = d.decompose("implement user authentication")
        assert len(subs) >= 1
        roles = [s.role for s in subs]
        assert AgentRole.CODER in roles

    def test_decompose_multi_phase(self) -> None:
        """decompose returns at least 3 subtasks when description includes design, implement, and test phases."""
        d = TaskDecomposer()
        subs = d.decompose("design and implement and test new feature")
        assert len(subs) >= 3

    def test_dependencies_are_sequential(self) -> None:
        """each subtask depends on the previous one, forming a sequential dependency chain."""
        d = TaskDecomposer()
        subs = d.decompose("implement and test feature")
        for i in range(1, len(subs)):
            assert subs[i - 1].task_id in subs[i].depends_on

    def test_execution_order(self) -> None:
        """execution_order returns all subtasks in a topologically valid sequence."""
        d = TaskDecomposer()
        subs = d.decompose("design and code and test feature")
        order = d.execution_order(subs)
        assert len(order) == len(subs)

    def test_cyclic_dependency_detected(self) -> None:
        """execution_order raises CyclicDependencyError when subtask dependencies form a cycle."""
        s1 = SubTask(task_id="a", depends_on=["b"])
        s2 = SubTask(task_id="b", depends_on=["a"])
        with pytest.raises(CyclicDependencyError):
            TaskDecomposer.execution_order([s1, s2])

    def test_leaf_tasks(self) -> None:
        """leaf_tasks returns only the subtasks with no dependents (the final tasks)."""
        d = TaskDecomposer()
        subs = d.decompose("implement and test")
        leaves = d.leaf_tasks(subs)
        assert len(leaves) == 1  # Last task is the leaf

    def test_default_decomposition(self) -> None:
        """decompose returns at least one subtask even for descriptions without keyword phase markers."""
        d = TaskDecomposer()
        subs = d.decompose("fix the broken thing")
        assert len(subs) >= 1


# ── Consensus ────────────────────────────────────────────────────


class TestConsensusEngine:
    """Test suite for ConsensusEngine."""

    def test_majority_approve(self) -> None:
        """majority strategy approves when more than half of votes are True."""
        engine = ConsensusEngine()
        votes = [Vote("a", True), Vote("b", True), Vote("c", False)]
        result = engine.resolve(votes, strategy="majority")
        assert result.decision == Decision.APPROVED

    def test_majority_reject(self) -> None:
        """majority strategy rejects when fewer than half of votes are True."""
        engine = ConsensusEngine()
        votes = [Vote("a", False), Vote("b", False), Vote("c", True)]
        result = engine.resolve(votes, strategy="majority")
        assert result.decision == Decision.REJECTED

    def test_weighted_approve(self) -> None:
        """weighted strategy approves when the sum of True-voter weights exceeds False-voter weights."""
        engine = ConsensusEngine()
        votes = [
            Vote("senior", True, weight=3.0),
            Vote("junior", False, weight=1.0),
        ]
        result = engine.resolve(votes, strategy="weighted")
        assert result.decision == Decision.APPROVED

    def test_veto_reject(self) -> None:
        """veto strategy returns VETOED when any vote is False."""
        engine = ConsensusEngine()
        votes = [Vote("a", True), Vote("b", False)]
        result = engine.resolve(votes, strategy="veto")
        assert result.decision == Decision.VETOED

    def test_veto_approve(self) -> None:
        """veto strategy returns APPROVED when all votes are True."""
        engine = ConsensusEngine()
        votes = [Vote("a", True), Vote("b", True)]
        result = engine.resolve(votes, strategy="veto")
        assert result.decision == Decision.APPROVED

    def test_empty_votes(self) -> None:
        """resolving with zero votes returns DEADLOCK decision."""
        engine = ConsensusEngine()
        result = engine.resolve([], strategy="majority")
        assert result.decision == Decision.DEADLOCK

    def test_result_to_dict(self) -> None:
        """to_dict() includes decision as string, votes_for count, and strategy name."""
        result = ConsensusResult(
            decision=Decision.APPROVED,
            votes=[Vote("a", True)],
            approval_score=1.0,
            strategy="majority",
        )
        d = result.to_dict()
        assert d["decision"] == "approved"
        assert d["votes_for"] == 1


# ── MessageBus ───────────────────────────────────────────────────


class TestMessageBus:
    """Test suite for MessageBus."""

    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self) -> None:
        """publishing to a subscribed topic delivers the message to all matching subscribers."""
        bus = MessageBus()
        received: list[SwarmMessage] = []
        bus.subscribe("alice", "task.assigned", lambda m: received.append(m))
        msg = SwarmMessage(SwarmMessageType.TASK_ASSIGNMENT, sender="system")
        await bus.publish("task.assigned", msg)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_wildcard_match(self) -> None:
        """wildcard subscriptions (e.g. "task.*") match any sub-topic under the prefix."""
        bus = MessageBus()
        received: list[SwarmMessage] = []
        bus.subscribe("alice", "task.*", lambda m: received.append(m))
        msg = SwarmMessage(SwarmMessageType.RESULT, sender="bob")
        await bus.publish("task.completed", msg)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_no_match(self) -> None:
        """publishing to a different topic does not trigger unrelated subscriptions."""
        bus = MessageBus()
        received: list[SwarmMessage] = []
        bus.subscribe("alice", "task.assigned", lambda m: received.append(m))
        await bus.publish(
            "review.requested",
            SwarmMessage(SwarmMessageType.REVIEW_REQUEST, "bob"),
        )
        assert len(received) == 0

    def test_unsubscribe(self) -> None:
        """unsubscribe(agent, topic) removes only the specified subscription and returns count removed."""
        bus = MessageBus()
        bus.subscribe("alice", "t1", lambda m: None)
        bus.subscribe("alice", "t2", lambda m: None)
        removed = bus.unsubscribe("alice", "t1")
        assert removed == 1
        assert bus.subscription_count == 1

    def test_unsubscribe_all(self) -> None:
        """unsubscribe(agent) without a topic removes all subscriptions for that agent."""
        bus = MessageBus()
        bus.subscribe("alice", "t1", lambda m: None)
        bus.subscribe("alice", "t2", lambda m: None)
        removed = bus.unsubscribe("alice")
        assert removed == 2

    @pytest.mark.asyncio
    async def test_history(self) -> None:
        """published messages are stored and retrievable via get_history()."""
        bus = MessageBus()
        await bus.publish("topic", SwarmMessage(SwarmMessageType.STATUS_UPDATE, "a"))
        await bus.publish("topic", SwarmMessage(SwarmMessageType.RESULT, "b"))
        assert bus.history_size == 2
        recent = bus.recent_messages(1)
        assert len(recent) == 1

    @pytest.mark.asyncio
    async def test_multi_segment_wildcard(self) -> None:
        """Test functionality: multi segment wildcard."""
        bus = MessageBus()
        received: list[SwarmMessage] = []
        bus.subscribe("alice", "task.#", lambda m: received.append(m))
        await bus.publish("task.sub.deep", SwarmMessage(SwarmMessageType.RESULT, "x"))
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_handler_error_isolated(self) -> None:
        """Test functionality: handler error isolated."""
        bus = MessageBus()
        good: list[SwarmMessage] = []
        bus.subscribe("bad", "topic", lambda m: 1 / 0)  # Will raise
        bus.subscribe("good", "topic", lambda m: good.append(m))
        count = await bus.publish(
            "topic", SwarmMessage(SwarmMessageType.STATUS_UPDATE, "x")
        )
        assert count == 1  # Only good handler counted
        assert len(good) == 1
