"""Comprehensive zero-mock unit tests for the collaboration module.

Covers: models, exceptions, consensus engine, task decomposer, agent pool,
message bus, queue channel, agent protocols, and collaborative agent base.

Zero-mock policy enforced: no unittest.mock, MagicMock, patch, or monkeypatch.
"""

import asyncio
from typing import Any

import pytest

from codomyrmex.collaboration.exceptions import (
    AgentBusyError,
    AgentNotFoundError,
    CapabilityMismatchError,
    ChannelError,
    CollaborationError,
    ConsensusError,
    CoordinationError,
    LeaderElectionError,
    MessageDeliveryError,
    TaskDependencyError,
    TaskExecutionError,
    TaskNotFoundError,
)
from codomyrmex.collaboration.models import (
    AgentStatus,
    SwarmStatus,
    Task,
    TaskPriority,
    TaskResult,
    TaskStatus,
)
from codomyrmex.collaboration.protocols import (
    AgentCapability,
    AgentCoordinator,
    AgentMessage,
    AgentState,
    BaseAgent,
    BroadcastProtocol,
    CapabilityRoutingProtocol,
    MessageType,
    RoundRobinProtocol,
)
from codomyrmex.collaboration.swarm.consensus import (
    ConsensusEngine,
    Decision,
    SwarmVote as Vote,
)
from codomyrmex.collaboration.swarm.decomposer import (
    CyclicDependencyError,
    SubTask,
    TaskDecomposer,
)
from codomyrmex.collaboration.swarm.message_bus import MessageBus
from codomyrmex.collaboration.swarm.pool import AgentPool, AssignmentError
from codomyrmex.collaboration.swarm.protocol import (
    AgentRole,
    SwarmAgent,
    SwarmMessage,
    SwarmMessageType,
    TaskAssignment,
)
from codomyrmex.collaboration.swarm.protocol import (
    TaskStatus as SwarmTaskStatus,
)

# ---------------------------------------------------------------------------
# Concrete helpers (no mocks)
# ---------------------------------------------------------------------------


class EchoAgent(BaseAgent):
    """Concrete BaseAgent that returns the task payload as its result."""

    async def process_task(self, task: Any) -> Any:
        return {"echo": str(task)}


class FailingAgent(BaseAgent):
    """Concrete BaseAgent that always raises an error."""

    async def process_task(self, task: Any) -> Any:
        raise RuntimeError("intentional failure")


# ---------------------------------------------------------------------------
# TestCollaborationModels
# ---------------------------------------------------------------------------


class TestCollaborationModels:
    """Tests for Task, TaskResult, SwarmStatus, and AgentStatus dataclasses."""

    def test_task_to_dict_has_expected_keys(self):
        """Task.to_dict() returns a dict with all required keys."""
        t = Task(name="build", description="build the thing")
        d = t.to_dict()
        for key in ("id", "name", "description", "required_capabilities", "priority",
                    "dependencies", "metadata", "created_at", "status", "assigned_agent_id"):
            assert key in d, f"Missing key: {key}"

    def test_task_to_dict_status_is_string(self):
        """Task.to_dict() serializes status as a string, not an enum."""
        t = Task(name="x")
        d = t.to_dict()
        assert isinstance(d["status"], str)
        assert d["status"] == "pending"

    def test_task_from_dict_round_trip(self):
        """Task.from_dict(task.to_dict()) restores equivalent task."""
        original = Task(
            name="compile",
            description="compile src",
            required_capabilities=["python"],
            priority=8,
            dependencies=["dep-1"],
        )
        serialized = original.to_dict()
        restored = Task.from_dict(serialized)
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.priority == original.priority
        assert restored.dependencies == original.dependencies

    def test_task_is_ready_with_all_deps_satisfied(self):
        """Task.is_ready() returns True when all dependency IDs are in completed list."""
        t = Task(name="deploy", dependencies=["t1", "t2"])
        assert t.is_ready(["t1", "t2"]) is True

    def test_task_is_ready_with_missing_dep(self):
        """Task.is_ready() returns False when a dependency is not completed."""
        t = Task(name="deploy", dependencies=["t1", "t2"])
        assert t.is_ready(["t1"]) is False

    def test_task_is_ready_with_no_deps(self):
        """A task with no dependencies is always ready."""
        t = Task(name="standalone")
        assert t.is_ready([]) is True

    def test_task_auto_generates_unique_ids(self):
        """Two tasks created without an explicit ID get distinct UUIDs."""
        t1 = Task(name="a")
        t2 = Task(name="b")
        assert t1.id != t2.id

    def test_task_priority_enum_values(self):
        """TaskPriority enum has correct integer values."""
        assert TaskPriority.LOW.value == 1
        assert TaskPriority.NORMAL.value == 5
        assert TaskPriority.HIGH.value == 8
        assert TaskPriority.CRITICAL.value == 10

    def test_task_status_enum_values(self):
        """TaskStatus enum values are lowercase strings."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"

    def test_task_result_to_dict_keys(self):
        """TaskResult.to_dict() returns all required keys."""
        r = TaskResult(task_id="t1", success=True, output={"data": 1})
        d = r.to_dict()
        for key in ("task_id", "success", "output", "error", "duration", "agent_id", "completed_at"):
            assert key in d

    def test_task_result_from_dict_round_trip(self):
        """TaskResult.from_dict(result.to_dict()) restores identity."""
        r = TaskResult(task_id="t-abc", success=False, error="oops", duration=1.5, agent_id="agent-1")
        d = r.to_dict()
        r2 = TaskResult.from_dict(d)
        assert r2.task_id == "t-abc"
        assert r2.success is False
        assert r2.error == "oops"
        assert r2.duration == pytest.approx(1.5)
        assert r2.agent_id == "agent-1"

    def test_task_result_success_false_stores_error(self):
        """TaskResult with success=False stores the error message."""
        r = TaskResult(task_id="t2", success=False, error="timeout")
        assert r.error == "timeout"
        assert r.success is False

    def test_swarm_status_to_dict_all_keys(self):
        """SwarmStatus.to_dict() returns all 8 keys."""
        s = SwarmStatus(total_agents=5, active_agents=2, idle_agents=3)
        d = s.to_dict()
        for key in ("total_agents", "active_agents", "idle_agents", "pending_tasks",
                    "running_tasks", "completed_tasks", "failed_tasks", "uptime_seconds"):
            assert key in d

    def test_swarm_status_defaults_are_zero(self):
        """SwarmStatus default constructor produces all-zero fields."""
        s = SwarmStatus()
        assert s.total_agents == 0
        assert s.uptime_seconds == 0.0

    def test_agent_status_to_dict_keys(self):
        """AgentStatus.to_dict() contains all required keys."""
        a = AgentStatus(agent_id="a1", name="Worker", status="idle", capabilities=["python"])
        d = a.to_dict()
        for key in ("agent_id", "name", "status", "current_task_id", "capabilities",
                    "tasks_completed", "tasks_failed", "last_heartbeat"):
            assert key in d

    def test_agent_status_from_dict_round_trip(self):
        """AgentStatus.from_dict(status.to_dict()) restores identity."""
        original = AgentStatus(agent_id="a2", name="Coder", status="busy",
                               capabilities=["go"], tasks_completed=7)
        d = original.to_dict()
        restored = AgentStatus.from_dict(d)
        assert restored.agent_id == "a2"
        assert restored.name == "Coder"
        assert restored.status == "busy"
        assert restored.tasks_completed == 7


# ---------------------------------------------------------------------------
# TestCollaborationExceptions
# ---------------------------------------------------------------------------


class TestCollaborationExceptions:
    """Tests for all collaboration exception types and their attributes."""

    def test_collaboration_error_is_base(self):
        """CollaborationError is the base for all collaboration exceptions."""
        err = CollaborationError("base error")
        assert isinstance(err, Exception)
        assert err.message == "base error"
        assert isinstance(err.details, dict)

    def test_collaboration_error_stores_details(self):
        """CollaborationError stores the details dict."""
        err = CollaborationError("msg", details={"key": "val"})
        assert err.details["key"] == "val"

    def test_agent_not_found_error_stores_agent_id(self):
        """AgentNotFoundError stores the missing agent_id."""
        err = AgentNotFoundError("agent-xyz")
        assert err.agent_id == "agent-xyz"
        assert "agent-xyz" in str(err)
        assert isinstance(err, CollaborationError)

    def test_agent_not_found_error_custom_message(self):
        """AgentNotFoundError accepts a custom message override."""
        err = AgentNotFoundError("a1", message="custom msg")
        assert str(err) == "custom msg"

    def test_agent_busy_error_with_task(self):
        """AgentBusyError includes agent_id and current_task_id."""
        err = AgentBusyError("agent-1", current_task_id="task-42")
        assert err.agent_id == "agent-1"
        assert err.current_task_id == "task-42"
        assert "task-42" in str(err)

    def test_agent_busy_error_without_task(self):
        """AgentBusyError without a task_id still stores agent_id."""
        err = AgentBusyError("agent-2")
        assert err.agent_id == "agent-2"
        assert err.current_task_id is None

    def test_task_execution_error_attrs(self):
        """TaskExecutionError stores task_id, reason, and optional agent_id."""
        err = TaskExecutionError("t1", "disk full", agent_id="a1")
        assert err.task_id == "t1"
        assert err.reason == "disk full"
        assert err.agent_id == "a1"

    def test_task_not_found_error_stores_id(self):
        """TaskNotFoundError stores the task_id."""
        err = TaskNotFoundError("t-missing")
        assert err.task_id == "t-missing"
        assert "t-missing" in str(err)

    def test_task_dependency_error_stores_missing_deps(self):
        """TaskDependencyError stores the missing dependency list."""
        err = TaskDependencyError("t1", ["t-dep-a", "t-dep-b"])
        assert err.task_id == "t1"
        assert "t-dep-a" in err.missing_dependencies
        assert "t-dep-b" in err.missing_dependencies

    def test_consensus_error_stores_vote_counts(self):
        """ConsensusError stores vote counts and quorum."""
        err = ConsensusError("upgrade-db", votes_for=2, votes_against=3, quorum=0.6)
        assert err.proposal == "upgrade-db"
        assert err.votes_for == 2
        assert err.votes_against == 3
        assert err.quorum == pytest.approx(0.6)

    def test_channel_error_stores_channel_and_reason(self):
        """ChannelError stores channel_id and reason."""
        err = ChannelError("ch-1", "buffer full")
        assert err.channel_id == "ch-1"
        assert err.reason == "buffer full"

    def test_message_delivery_error_stores_parties(self):
        """MessageDeliveryError stores sender, receiver, and message_id."""
        err = MessageDeliveryError("msg-1", "alice", "bob", "unreachable")
        assert err.message_id == "msg-1"
        assert err.sender_id == "alice"
        assert err.receiver_id == "bob"
        assert err.reason == "unreachable"

    def test_coordination_error_stores_operation_and_reason(self):
        """CoordinationError stores operation and reason."""
        err = CoordinationError("leader-election", "no candidates")
        assert err.operation == "leader-election"
        assert err.reason == "no candidates"

    def test_leader_election_error_with_candidates(self):
        """LeaderElectionError stores reason and candidate list."""
        err = LeaderElectionError("tie", candidates=["a1", "a2"])
        assert err.reason == "tie"
        assert "a1" in err.candidates

    def test_capability_mismatch_error_stores_capabilities(self):
        """CapabilityMismatchError stores required and available capabilities."""
        err = CapabilityMismatchError(["rust"], available_capabilities=["python"])
        assert "rust" in err.required_capabilities
        assert "python" in err.available_capabilities

    def test_all_exceptions_inherit_collaboration_error(self):
        """Every concrete exception is a subclass of CollaborationError."""
        errors = [
            AgentNotFoundError("x"),
            AgentBusyError("x"),
            TaskExecutionError("x", "y"),
            TaskNotFoundError("x"),
            TaskDependencyError("x", []),
            ConsensusError("x", 1, 1, 0.5),
            ChannelError("x", "y"),
            MessageDeliveryError("x", "s", "r", "y"),
            CoordinationError("x", "y"),
            LeaderElectionError("x"),
            CapabilityMismatchError([]),
        ]
        for err in errors:
            assert isinstance(err, CollaborationError), f"{type(err)} not CollaborationError"


# ---------------------------------------------------------------------------
# TestConsensusEngine
# ---------------------------------------------------------------------------


class TestConsensusEngine:
    """Tests for ConsensusEngine majority, weighted, and veto strategies."""

    def test_majority_approved_when_2_of_3_yes(self):
        """2/3 votes approve → APPROVED with majority strategy."""
        engine = ConsensusEngine()
        votes = [Vote("a1", True), Vote("a2", True), Vote("a3", False)]
        result = engine.resolve(votes, strategy="majority")
        assert result.decision == Decision.APPROVED
        assert result.approval_score == pytest.approx(2 / 3)

    def test_majority_rejected_when_1_of_3_yes(self):
        """1/3 votes approve → REJECTED with majority strategy."""
        engine = ConsensusEngine()
        votes = [Vote("a1", True), Vote("a2", False), Vote("a3", False)]
        result = engine.resolve(votes, strategy="majority")
        assert result.decision == Decision.REJECTED

    def test_majority_deadlock_at_exactly_threshold(self):
        """2/4 votes (exactly 0.5) → DEADLOCK with default threshold=0.5."""
        engine = ConsensusEngine()
        votes = [Vote("a1", True), Vote("a2", True), Vote("a3", False), Vote("a4", False)]
        result = engine.resolve(votes, strategy="majority")
        assert result.decision == Decision.DEADLOCK

    def test_majority_unanimous_approval(self):
        """All votes approve → APPROVED."""
        engine = ConsensusEngine()
        votes = [Vote(f"a{i}", True) for i in range(5)]
        result = engine.resolve(votes)
        assert result.decision == Decision.APPROVED
        assert result.approval_score == pytest.approx(1.0)

    def test_majority_empty_votes_returns_deadlock(self):
        """Empty vote list → DEADLOCK regardless of strategy."""
        engine = ConsensusEngine()
        result = engine.resolve([])
        assert result.decision == Decision.DEADLOCK
        assert result.votes == []

    def test_weighted_higher_weight_wins(self):
        """Weighted vote: 1 heavy approver outweighs 2 light rejectors."""
        engine = ConsensusEngine()
        votes = [
            Vote("a1", True, weight=10.0),
            Vote("a2", False, weight=1.0),
            Vote("a3", False, weight=1.0),
        ]
        result = engine.resolve(votes, strategy="weighted")
        assert result.decision == Decision.APPROVED
        assert result.strategy == "weighted"

    def test_weighted_low_weight_approver_rejected(self):
        """Weighted vote: light approver loses to heavy rejector."""
        engine = ConsensusEngine()
        votes = [
            Vote("a1", True, weight=1.0),
            Vote("a2", False, weight=10.0),
        ]
        result = engine.resolve(votes, strategy="weighted")
        assert result.decision == Decision.REJECTED

    def test_veto_all_approve_gives_approved(self):
        """Veto strategy: all approve → APPROVED."""
        engine = ConsensusEngine()
        votes = [Vote("a1", True), Vote("a2", True), Vote("a3", True)]
        result = engine.resolve(votes, strategy="veto")
        assert result.decision == Decision.APPROVED
        assert result.strategy == "veto"

    def test_veto_one_reject_gives_vetoed(self):
        """Veto strategy: single reject → VETOED, regardless of approval count."""
        engine = ConsensusEngine()
        votes = [Vote("a1", True), Vote("a2", True), Vote("a3", False)]
        result = engine.resolve(votes, strategy="veto")
        assert result.decision == Decision.VETOED

    def test_consensus_result_to_dict_keys(self):
        """ConsensusResult.to_dict() contains all expected keys."""
        engine = ConsensusEngine()
        votes = [Vote("a1", True), Vote("a2", False)]
        result = engine.resolve(votes)
        d = result.to_dict()
        for key in ("decision", "approval_score", "strategy", "votes_for", "votes_against", "total_votes"):
            assert key in d

    def test_consensus_result_to_dict_counts_correct(self):
        """ConsensusResult.to_dict() vote counts match the vote list."""
        engine = ConsensusEngine()
        votes = [Vote("a1", True), Vote("a2", True), Vote("a3", False)]
        result = engine.resolve(votes)
        d = result.to_dict()
        assert d["votes_for"] == 2
        assert d["votes_against"] == 1
        assert d["total_votes"] == 3

    def test_unknown_strategy_falls_back_to_majority(self):
        """Unknown strategy name falls through to majority logic."""
        engine = ConsensusEngine()
        votes = [Vote("a1", True), Vote("a2", True), Vote("a3", False)]
        result = engine.resolve(votes, strategy="nonexistent")
        assert result.decision == Decision.APPROVED

    def test_vote_reason_stored(self):
        """Vote.reason is stored on the dataclass."""
        v = Vote("a1", True, reason="looks good")
        assert v.reason == "looks good"


# ---------------------------------------------------------------------------
# TestTaskDecomposer
# ---------------------------------------------------------------------------


class TestTaskDecomposer:
    """Tests for TaskDecomposer decompose(), execution_order(), and leaf_tasks()."""

    def test_decompose_no_keywords_returns_three_default_phases(self):
        """A task with no recognized keywords gets 3 default phases."""
        d = TaskDecomposer()
        subtasks = d.decompose("do something mysterious")
        assert len(subtasks) == 3

    def test_decompose_includes_coder_phase_for_build_keyword(self):
        """'build' keyword triggers a CODER phase subtask."""
        d = TaskDecomposer()
        subtasks = d.decompose("build the feature")
        roles = [st.role for st in subtasks]
        assert AgentRole.CODER in roles

    def test_decompose_includes_tester_phase_for_test_keyword(self):
        """'test' keyword triggers a TESTER phase subtask."""
        d = TaskDecomposer()
        subtasks = d.decompose("test everything")
        roles = [st.role for st in subtasks]
        assert AgentRole.TESTER in roles

    def test_decompose_includes_architect_phase_for_design_keyword(self):
        """'design' keyword triggers an ARCHITECT phase subtask."""
        d = TaskDecomposer()
        subtasks = d.decompose("design the system")
        roles = [st.role for st in subtasks]
        assert AgentRole.ARCHITECT in roles

    def test_decompose_subtasks_have_sequential_dependencies(self):
        """Each subtask (except first) depends on the previous one."""
        d = TaskDecomposer()
        subtasks = d.decompose("something")
        for i in range(1, len(subtasks)):
            assert len(subtasks[i].depends_on) == 1
            assert subtasks[i].depends_on[0] == subtasks[i - 1].task_id

    def test_decompose_first_subtask_has_no_deps(self):
        """The first subtask has an empty depends_on list."""
        d = TaskDecomposer()
        subtasks = d.decompose("something")
        assert subtasks[0].depends_on == []

    def test_execution_order_respects_dependencies(self):
        """execution_order() returns tasks topologically — deps before dependents."""
        d = TaskDecomposer()
        subtasks = d.decompose("something")
        order = d.execution_order(subtasks)
        seen: set[str] = set()
        for st in order:
            for dep_id in st.depends_on:
                assert dep_id in seen or dep_id == "", (
                    f"Task {st.task_id} came before its dependency {dep_id}"
                )
            seen.add(st.task_id)

    def test_execution_order_length_matches_input(self):
        """execution_order() returns the same number of subtasks as input."""
        d = TaskDecomposer()
        subtasks = d.decompose("build and test and review")
        order = d.execution_order(subtasks)
        assert len(order) == len(subtasks)

    def test_execution_order_raises_on_cycle(self):
        """execution_order() raises CyclicDependencyError on a dependency cycle."""
        st_a = SubTask(task_id="a", description="a", depends_on=["b"])
        st_b = SubTask(task_id="b", description="b", depends_on=["a"])
        with pytest.raises(CyclicDependencyError):
            TaskDecomposer.execution_order([st_a, st_b])

    def test_leaf_tasks_are_not_dependencies_of_others(self):
        """leaf_tasks() returns only tasks that no other task depends on."""
        d = TaskDecomposer()
        subtasks = d.decompose("something")
        leaves = TaskDecomposer.leaf_tasks(subtasks)
        # The last subtask in a chain has no dependents → it is a leaf
        last_id = subtasks[-1].task_id
        leaf_ids = {st.task_id for st in leaves}
        assert last_id in leaf_ids

    def test_leaf_tasks_single_task_is_leaf(self):
        """A single subtask with no deps and no dependents is a leaf."""
        st = SubTask(task_id="only", description="solo", depends_on=[])
        leaves = TaskDecomposer.leaf_tasks([st])
        assert len(leaves) == 1
        assert leaves[0].task_id == "only"

    def test_subtask_to_dict_keys(self):
        """SubTask.to_dict() contains all required keys."""
        st = SubTask(description="build it", role=AgentRole.CODER)
        d = st.to_dict()
        for key in ("task_id", "description", "role", "depends_on", "priority"):
            assert key in d

    def test_subtask_auto_assigns_task_id(self):
        """SubTask without explicit task_id gets an auto-generated 8-char ID."""
        st = SubTask(description="something")
        assert len(st.task_id) == 8
        assert st.task_id != ""


# ---------------------------------------------------------------------------
# TestAgentPool
# ---------------------------------------------------------------------------


class TestAgentPool:
    """Tests for AgentPool register, assign, release, and load-balancing."""

    def test_empty_pool_size_is_zero(self):
        """An empty pool has size 0."""
        pool = AgentPool()
        assert pool.size == 0

    def test_register_increases_size(self):
        """Registering an agent increases pool size by 1."""
        pool = AgentPool()
        pool.register(SwarmAgent("a1", AgentRole.CODER))
        assert pool.size == 1

    def test_get_returns_registered_agent(self):
        """get(agent_id) returns the registered SwarmAgent."""
        pool = AgentPool()
        agent = SwarmAgent("a1", AgentRole.CODER)
        pool.register(agent)
        result = pool.get("a1")
        assert result is agent

    def test_get_returns_none_for_missing_agent(self):
        """get() returns None for an unregistered agent_id."""
        pool = AgentPool()
        assert pool.get("ghost") is None

    def test_assign_raises_when_pool_empty(self):
        """assign() raises AssignmentError when no agents are in the pool."""
        pool = AgentPool()
        assignment = TaskAssignment(description="work", required_role=AgentRole.CODER)
        with pytest.raises(AssignmentError):
            pool.assign(assignment)

    def test_assign_raises_when_no_matching_role(self):
        """assign() raises AssignmentError when no agent has the required role."""
        pool = AgentPool()
        pool.register(SwarmAgent("a1", AgentRole.REVIEWER))
        assignment = TaskAssignment(description="code it", required_role=AgentRole.CODER)
        with pytest.raises(AssignmentError):
            pool.assign(assignment)

    def test_assign_selects_agent_by_role(self):
        """assign() returns an agent matching the required role."""
        pool = AgentPool()
        pool.register(SwarmAgent("coder-1", AgentRole.CODER))
        pool.register(SwarmAgent("rev-1", AgentRole.REVIEWER))
        assignment = TaskAssignment(description="code it", required_role=AgentRole.CODER)
        agent = pool.assign(assignment)
        assert agent.role == AgentRole.CODER

    def test_assign_increments_agent_active_tasks(self):
        """assign() increments the agent's active_tasks counter."""
        pool = AgentPool()
        pool.register(SwarmAgent("a1", AgentRole.CODER))
        assignment = TaskAssignment(description="work", required_role=AgentRole.CODER)
        agent = pool.assign(assignment)
        assert agent.active_tasks == 1

    def test_assign_marks_assignment_status_assigned(self):
        """assign() sets assignment.status to ASSIGNED."""
        pool = AgentPool()
        pool.register(SwarmAgent("a1", AgentRole.CODER))
        assignment = TaskAssignment(description="work", required_role=AgentRole.CODER)
        pool.assign(assignment)
        assert assignment.status == SwarmTaskStatus.ASSIGNED

    def test_release_decrements_active_tasks(self):
        """release() decrements the agent's active_tasks counter."""
        pool = AgentPool()
        pool.register(SwarmAgent("a1", AgentRole.CODER))
        assignment = TaskAssignment(description="work", required_role=AgentRole.CODER)
        agent = pool.assign(assignment)
        pool.release(agent.agent_id)
        assert agent.active_tasks == 0

    def test_assign_selects_least_loaded_agent(self):
        """assign() picks the agent with fewer active tasks (least load)."""
        pool = AgentPool()
        busy = SwarmAgent("busy", AgentRole.CODER)
        busy.active_tasks = 2
        idle = SwarmAgent("idle", AgentRole.CODER)
        idle.active_tasks = 0
        pool.register(busy)
        pool.register(idle)
        assignment = TaskAssignment(description="work", required_role=AgentRole.CODER)
        selected = pool.assign(assignment)
        assert selected.agent_id == "idle"

    def test_unregister_returns_true_on_success(self):
        """unregister() returns True for a known agent_id."""
        pool = AgentPool()
        pool.register(SwarmAgent("a1", AgentRole.CODER))
        assert pool.unregister("a1") is True
        assert pool.size == 0

    def test_unregister_returns_false_for_unknown(self):
        """unregister() returns False for an unknown agent_id."""
        pool = AgentPool()
        assert pool.unregister("ghost") is False

    def test_agents_by_role_filters_correctly(self):
        """agents_by_role() returns only agents matching the given role."""
        pool = AgentPool()
        pool.register(SwarmAgent("c1", AgentRole.CODER))
        pool.register(SwarmAgent("c2", AgentRole.CODER))
        pool.register(SwarmAgent("r1", AgentRole.REVIEWER))
        coders = pool.agents_by_role(AgentRole.CODER)
        assert len(coders) == 2
        assert all(a.role == AgentRole.CODER for a in coders)

    def test_status_returns_summary_dict(self):
        """status() returns a dict with total, available, by_role, and agents keys."""
        pool = AgentPool()
        pool.register(SwarmAgent("a1", AgentRole.CODER))
        s = pool.status()
        assert "total" in s
        assert "available" in s
        assert "by_role" in s
        assert "agents" in s
        assert s["total"] == 1

    def test_swarm_agent_available_when_below_max(self):
        """SwarmAgent.available is True when active_tasks < max_concurrent."""
        agent = SwarmAgent("a1", AgentRole.CODER, max_concurrent=3)
        agent.active_tasks = 2
        assert agent.available is True

    def test_swarm_agent_unavailable_at_max(self):
        """SwarmAgent.available is False when active_tasks == max_concurrent."""
        agent = SwarmAgent("a1", AgentRole.CODER, max_concurrent=2)
        agent.active_tasks = 2
        assert agent.available is False

    def test_swarm_agent_load_fraction(self):
        """SwarmAgent.load returns active_tasks / max_concurrent."""
        agent = SwarmAgent("a1", AgentRole.CODER, max_concurrent=4)
        agent.active_tasks = 2
        assert agent.load == pytest.approx(0.5)

    def test_swarm_agent_to_dict_keys(self):
        """SwarmAgent.to_dict() contains role, agent_id, capabilities, available."""
        agent = SwarmAgent("a1", AgentRole.TESTER, {"pytest"})
        d = agent.to_dict()
        for key in ("agent_id", "role", "capabilities", "active_tasks", "available", "load"):
            assert key in d


# ---------------------------------------------------------------------------
# TestMessageBus
# ---------------------------------------------------------------------------


class TestMessageBus:
    """Tests for MessageBus topic matching, subscribe, unsubscribe, and publish."""

    def _make_message(self, sender: str = "manager") -> SwarmMessage:
        return SwarmMessage(
            message_type=SwarmMessageType.STATUS_UPDATE,
            sender=sender,
            payload={"info": "test"},
        )

    def test_subscribe_increases_subscription_count(self):
        """subscribe() adds a subscription to the bus."""
        bus = MessageBus()
        bus.subscribe("alice", "tasks.*", lambda m: None)
        assert bus.subscription_count == 1

    def test_unsubscribe_removes_subscription(self):
        """unsubscribe() removes all subscriptions for a subscriber."""
        bus = MessageBus()
        bus.subscribe("alice", "tasks.*", lambda m: None)
        removed = bus.unsubscribe("alice")
        assert removed == 1
        assert bus.subscription_count == 0

    def test_unsubscribe_specific_topic(self):
        """unsubscribe() with topic only removes matching topic subscriptions."""
        bus = MessageBus()
        bus.subscribe("alice", "tasks.*", lambda m: None)
        bus.subscribe("alice", "results.#", lambda m: None)
        removed = bus.unsubscribe("alice", "tasks.*")
        assert removed == 1
        assert bus.subscription_count == 1

    def test_topic_matches_exact(self):
        """Exact topic string matches itself."""
        assert MessageBus._topic_matches("tasks.assigned", "tasks.assigned") is True

    def test_topic_matches_star_wildcard_single_segment(self):
        """'*' matches any single path segment but not dots."""
        assert MessageBus._topic_matches("tasks.*", "tasks.assigned") is True
        assert MessageBus._topic_matches("tasks.*", "tasks.assigned.detail") is False

    def test_topic_matches_hash_wildcard_multi_segment(self):
        """'#' matches multiple path segments."""
        assert MessageBus._topic_matches("tasks.#", "tasks.assigned.detail") is True
        assert MessageBus._topic_matches("results.#", "results.agent.a1") is True

    def test_topic_no_match_different_prefix(self):
        """Different prefix does not match."""
        assert MessageBus._topic_matches("tasks.*", "results.assigned") is False

    @pytest.mark.asyncio
    async def test_publish_delivers_to_matching_subscriber(self):
        """publish() invokes handler for subscribers with matching topic."""
        bus = MessageBus()
        received = []
        bus.subscribe("alice", "tasks.assigned", lambda m: received.append(m))
        msg = self._make_message()
        await bus.publish("tasks.assigned", msg)
        assert len(received) == 1
        assert received[0] is msg

    @pytest.mark.asyncio
    async def test_publish_does_not_deliver_to_non_matching_subscriber(self):
        """publish() does not invoke handler for non-matching topic."""
        bus = MessageBus()
        received = []
        bus.subscribe("alice", "tasks.completed", lambda m: received.append(m))
        msg = self._make_message()
        await bus.publish("tasks.assigned", msg)
        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_publish_delivers_to_wildcard_subscriber(self):
        """publish() matches wildcard subscription patterns."""
        bus = MessageBus()
        received = []
        bus.subscribe("mgr", "tasks.#", lambda m: received.append(m))
        msg = self._make_message()
        await bus.publish("tasks.assigned.urgent", msg)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_publish_returns_delivered_count(self):
        """publish() returns the count of handlers successfully invoked."""
        bus = MessageBus()
        bus.subscribe("a", "x.y", lambda m: None)
        bus.subscribe("b", "x.y", lambda m: None)
        msg = self._make_message()
        count = await bus.publish("x.y", msg)
        assert count == 2

    @pytest.mark.asyncio
    async def test_history_grows_on_publish(self):
        """Message history grows by 1 for each published message."""
        bus = MessageBus()
        assert bus.history_size == 0
        await bus.publish("topic", self._make_message())
        assert bus.history_size == 1

    @pytest.mark.asyncio
    async def test_recent_messages_respects_limit(self):
        """recent_messages(limit=2) returns at most 2 messages."""
        bus = MessageBus()
        for _ in range(5):
            await bus.publish("x", self._make_message())
        recent = bus.recent_messages(limit=2)
        assert len(recent) == 2

    def test_swarm_message_auto_assigns_id_and_timestamp(self):
        """SwarmMessage auto-populates message_id and timestamp in __post_init__."""
        msg = self._make_message()
        assert msg.message_id != ""
        assert msg.timestamp > 0

    def test_swarm_message_to_dict_keys(self):
        """SwarmMessage.to_dict() contains all required keys."""
        msg = self._make_message()
        d = msg.to_dict()
        for key in ("message_type", "sender", "recipient", "payload", "message_id", "timestamp"):
            assert key in d


# ---------------------------------------------------------------------------
# TestQueueChannel
# ---------------------------------------------------------------------------


class TestQueueChannel:
    """Tests for QueueChannel send, receive, state transitions, and ChannelManager."""

    def _make_message(self, sender: str = "s1", receiver: str = "r1") -> AgentMessage:
        return AgentMessage(sender_id=sender, receiver_id=receiver, content="hello")

    @pytest.mark.asyncio
    async def test_send_and_receive_message(self):
        """Messages sent through QueueChannel are retrievable via receive()."""
        from codomyrmex.collaboration.communication.channels import QueueChannel
        ch = QueueChannel(name="test-ch")
        msg = self._make_message()
        await ch.send(msg)
        received = await asyncio.wait_for(ch.receive(), timeout=1.0)
        assert received.id == msg.id

    @pytest.mark.asyncio
    async def test_send_on_closed_channel_raises_channel_error(self):
        """Sending to a closed channel raises ChannelError."""
        from codomyrmex.collaboration.communication.channels import QueueChannel
        ch = QueueChannel(name="closed-ch")
        ch.close()
        with pytest.raises(ChannelError):
            await ch.send(self._make_message())

    def test_channel_state_transitions(self):
        """Channel pause/resume/close transitions work correctly."""
        from codomyrmex.collaboration.communication.channels import (
            ChannelState,
            QueueChannel,
        )
        ch = QueueChannel(name="state-ch")
        assert ch.state == ChannelState.OPEN
        ch.pause()
        assert ch.state == ChannelState.PAUSED
        ch.resume()
        assert ch.state == ChannelState.OPEN
        ch.close()
        assert ch.state == ChannelState.CLOSED

    def test_get_info_returns_channel_info(self):
        """get_info() returns a ChannelInfo with correct channel_id and name."""
        from codomyrmex.collaboration.communication.channels import QueueChannel
        ch = QueueChannel(name="info-ch")
        info = ch.get_info()
        assert info.channel_id == ch.channel_id
        assert info.name == "info-ch"

    def test_get_info_to_dict_has_all_keys(self):
        """ChannelInfo.to_dict() contains all required keys."""
        from codomyrmex.collaboration.communication.channels import QueueChannel
        ch = QueueChannel(name="x")
        info = ch.get_info()
        d = info.to_dict()
        for key in ("channel_id", "name", "state", "subscriber_count", "message_count", "created_at"):
            assert key in d

    def test_channel_manager_creates_channel(self):
        """ChannelManager.create_channel() returns a channel with the given name."""
        from codomyrmex.collaboration.communication.channels import ChannelManager
        mgr = ChannelManager()
        ch = mgr.create_channel("my-channel")
        assert ch.name == "my-channel"

    def test_channel_manager_get_by_id(self):
        """ChannelManager.get_channel() retrieves channel by ID."""
        from codomyrmex.collaboration.communication.channels import ChannelManager
        mgr = ChannelManager()
        ch = mgr.create_channel("ch-by-id")
        retrieved = mgr.get_channel(ch.channel_id)
        assert retrieved is ch

    def test_channel_manager_get_by_name(self):
        """ChannelManager.get_channel_by_name() retrieves channel by name."""
        from codomyrmex.collaboration.communication.channels import ChannelManager
        mgr = ChannelManager()
        ch = mgr.create_channel("named-ch")
        retrieved = mgr.get_channel_by_name("named-ch")
        assert retrieved is ch

    def test_channel_manager_list_channels(self):
        """ChannelManager.list_channels() returns info for all created channels."""
        from codomyrmex.collaboration.communication.channels import ChannelManager
        mgr = ChannelManager()
        mgr.create_channel("ch-a")
        mgr.create_channel("ch-b")
        channels = mgr.list_channels()
        assert len(channels) == 2

    def test_channel_manager_close_channel(self):
        """close_channel() removes the channel from the manager."""
        from codomyrmex.collaboration.communication.channels import ChannelManager
        mgr = ChannelManager()
        ch = mgr.create_channel("close-me")
        result = mgr.close_channel(ch.channel_id)
        assert result is True
        assert mgr.get_channel(ch.channel_id) is None

    def test_channel_manager_close_all(self):
        """close_all() removes all channels."""
        from codomyrmex.collaboration.communication.channels import ChannelManager
        mgr = ChannelManager()
        mgr.create_channel("x")
        mgr.create_channel("y")
        mgr.close_all()
        assert mgr.list_channels() == []

    def test_channel_manager_unknown_type_raises(self):
        """create_channel() with unknown type raises ValueError."""
        from codomyrmex.collaboration.communication.channels import ChannelManager
        mgr = ChannelManager()
        with pytest.raises(ValueError):
            mgr.create_channel("bad-ch", channel_type="ftp")


class TestMessageQueue:
    """Tests for MessageQueue put/get/clear/is_empty/is_full operations."""

    @pytest.mark.asyncio
    async def test_put_and_get_roundtrip(self):
        """Messages put into the queue can be retrieved via get()."""
        from codomyrmex.collaboration.communication.channels import MessageQueue
        q = MessageQueue()
        msg = AgentMessage(sender_id="s", content="data")
        await q.put(msg)
        retrieved = await asyncio.wait_for(q.get(), timeout=1.0)
        assert retrieved.id == msg.id

    def test_put_nowait_on_full_queue_raises(self):
        """put_nowait() raises ChannelError when queue capacity is reached."""
        from codomyrmex.collaboration.communication.channels import MessageQueue
        q = MessageQueue(max_size=1)
        msg1 = AgentMessage(sender_id="s", content="1")
        msg2 = AgentMessage(sender_id="s", content="2")
        q.put_nowait(msg1)
        with pytest.raises(ChannelError):
            q.put_nowait(msg2)

    def test_is_empty_on_fresh_queue(self):
        """A fresh MessageQueue reports is_empty == True."""
        from codomyrmex.collaboration.communication.channels import MessageQueue
        q = MessageQueue()
        assert q.is_empty is True

    def test_clear_removes_all_messages(self):
        """clear() drains the queue and returns the count of removed messages."""
        from codomyrmex.collaboration.communication.channels import MessageQueue
        q = MessageQueue()
        for i in range(3):
            q.put_nowait(AgentMessage(sender_id="s", content=str(i)))
        count = q.clear()
        assert count == 3
        assert q.is_empty is True

    def test_get_nowait_returns_none_when_empty(self):
        """get_nowait() returns None on an empty queue (no exception)."""
        from codomyrmex.collaboration.communication.channels import MessageQueue
        q = MessageQueue()
        result = q.get_nowait()
        assert result is None


# ---------------------------------------------------------------------------
# TestAgentProtocols
# ---------------------------------------------------------------------------


class TestAgentProtocols:
    """Tests for AgentMessage, AgentCapability, RoundRobinProtocol, CapabilityRoutingProtocol."""

    def test_agent_message_to_dict_keys(self):
        """AgentMessage.to_dict() returns all expected keys."""
        msg = AgentMessage(sender_id="a1", content="hello")
        d = msg.to_dict()
        for key in ("id", "sender_id", "receiver_id", "message_type", "content",
                    "metadata", "timestamp", "reply_to"):
            assert key in d

    def test_agent_message_create_reply(self):
        """create_reply() returns a response message addressed to original sender."""
        original = AgentMessage(sender_id="a1", receiver_id="a2", content="request")
        reply = original.create_reply("response data")
        assert reply.receiver_id == "a1"
        assert reply.message_type == MessageType.RESPONSE
        assert reply.reply_to == original.id
        assert reply.content == "response data"

    def test_agent_capability_to_dict(self):
        """AgentCapability.to_dict() contains name, description, and schema fields."""
        cap = AgentCapability(name="code-review", description="Reviews code", input_schema={"code": "str"})
        d = cap.to_dict()
        assert d["name"] == "code-review"
        assert d["description"] == "Reviews code"
        assert d["input_schema"] == {"code": "str"}

    def test_agent_state_enum_values(self):
        """AgentState enum contains expected states."""
        states = {s.value for s in AgentState}
        assert {"idle", "busy", "waiting", "error", "terminated"}.issubset(states)

    def test_message_type_enum_values(self):
        """MessageType enum contains expected types."""
        types = {t.value for t in MessageType}
        assert {"request", "response", "broadcast", "handoff", "status", "error"}.issubset(types)

    def test_agent_coordinator_register_and_get_idle(self):
        """AgentCoordinator.register() adds agents; get_idle_agents() returns idle ones."""
        coordinator = AgentCoordinator()
        agent = EchoAgent(name="Echo")
        coordinator.register_agent(agent)
        idle = coordinator.get_idle_agents()
        assert any(a.agent_id == agent.agent_id for a in idle)

    def test_agent_coordinator_unregister(self):
        """unregister_agent() removes the agent from the coordinator."""
        coordinator = AgentCoordinator()
        agent = EchoAgent(name="Echo2")
        coordinator.register_agent(agent)
        coordinator.unregister_agent(agent.agent_id)
        idle = coordinator.get_idle_agents()
        assert not any(a.agent_id == agent.agent_id for a in idle)

    def test_agent_coordinator_find_by_capability(self):
        """find_agents_with_capability() returns agents that have the capability."""
        coordinator = AgentCoordinator()
        cap = AgentCapability(name="python", description="Runs Python")
        agent = EchoAgent(name="Py", capabilities=[cap])
        coordinator.register_agent(agent)
        matches = coordinator.find_agents_with_capability("python")
        assert len(matches) == 1
        assert matches[0].agent_id == agent.agent_id

    def test_round_robin_cycles_through_agents(self):
        """RoundRobinProtocol.select_agents() cycles through available agents."""
        protocol = RoundRobinProtocol()
        a1 = EchoAgent(name="A1")
        a2 = EchoAgent(name="A2")
        agents = [a1, a2]
        sel1 = protocol.select_agents("task", agents)
        sel2 = protocol.select_agents("task", agents)
        assert sel1[0].agent_id != sel2[0].agent_id

    def test_round_robin_returns_empty_for_empty_pool(self):
        """RoundRobinProtocol.select_agents() returns [] when no agents available."""
        protocol = RoundRobinProtocol()
        result = protocol.select_agents("task", [])
        assert result == []

    def test_broadcast_protocol_selects_all_agents(self):
        """BroadcastProtocol.select_agents() returns all available agents."""
        protocol = BroadcastProtocol()
        agents = [EchoAgent(name=f"Agent-{i}") for i in range(4)]
        selected = protocol.select_agents("task", agents)
        assert len(selected) == 4

    def test_capability_routing_filters_by_capability(self):
        """CapabilityRoutingProtocol only selects agents with required capability."""
        cap = AgentCapability(name="rust", description="Rust lang")
        agent_with = EchoAgent(name="Rustacean", capabilities=[cap])
        agent_without = EchoAgent(name="Pythonista", capabilities=[])
        protocol = CapabilityRoutingProtocol(required_capability="rust")
        selected = protocol.select_agents("task", [agent_with, agent_without])
        assert len(selected) == 1
        assert selected[0].agent_id == agent_with.agent_id

    @pytest.mark.asyncio
    async def test_round_robin_execute_calls_agent(self):
        """RoundRobinProtocol.execute() calls the agent's process_task and resets state."""
        protocol = RoundRobinProtocol()
        agent = EchoAgent(name="Echoer")
        result = await protocol.execute("test input", [agent])
        assert result == {"echo": "test input"}
        assert agent.state == AgentState.IDLE

    @pytest.mark.asyncio
    async def test_broadcast_protocol_execute_all_agents(self):
        """BroadcastProtocol.execute() calls all agents and returns a list."""
        protocol = BroadcastProtocol()
        agents = [EchoAgent(name=f"A{i}") for i in range(3)]
        results = await protocol.execute("ping", agents)
        assert len(results) == 3
        for r in results:
            assert r == {"echo": "ping"}

    @pytest.mark.asyncio
    async def test_capability_routing_raises_when_no_capable_agent(self):
        """CapabilityRoutingProtocol.execute() raises ValueError when no agents provided."""
        protocol = CapabilityRoutingProtocol(required_capability="magic")
        with pytest.raises(ValueError, match="No agents with capability"):
            await protocol.execute("task", [])


# ---------------------------------------------------------------------------
# TestTaskAssignment
# ---------------------------------------------------------------------------


class TestTaskAssignment:
    """Tests for TaskAssignment dataclass serialization and defaults."""

    def test_task_assignment_auto_generates_id(self):
        """TaskAssignment without explicit task_id gets an auto-generated 8-char ID."""
        ta = TaskAssignment(description="do work")
        assert len(ta.task_id) == 8

    def test_task_assignment_default_status_pending(self):
        """TaskAssignment default status is PENDING."""
        ta = TaskAssignment(description="do work")
        assert ta.status == SwarmTaskStatus.PENDING

    def test_task_assignment_to_dict_keys(self):
        """TaskAssignment.to_dict() contains all required keys."""
        ta = TaskAssignment(description="code review", required_role=AgentRole.REVIEWER)
        d = ta.to_dict()
        for key in ("task_id", "description", "assignee", "required_role", "status", "priority", "result"):
            assert key in d

    def test_task_assignment_required_role_serialized_as_string(self):
        """TaskAssignment.to_dict() serializes required_role as a string value."""
        ta = TaskAssignment(description="x", required_role=AgentRole.ARCHITECT)
        d = ta.to_dict()
        assert d["required_role"] == "architect"

    def test_task_assignment_none_role_serializes_as_none(self):
        """TaskAssignment with no required_role serializes required_role as None."""
        ta = TaskAssignment(description="any role")
        d = ta.to_dict()
        assert d["required_role"] is None
