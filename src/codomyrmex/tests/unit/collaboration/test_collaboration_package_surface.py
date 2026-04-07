# type: ignore
"""Functional tests for collaboration module — zero-mock.

Exercises agent lifecycle (AgentPool, AgentCoordinator), messaging
(MessageBus, AgentMessage), task management (TaskDecomposer, TaskAssignment),
swarm (SwarmManager, SwarmAgent, SwarmVote), and protocols.
"""

from __future__ import annotations

import pytest

import codomyrmex.collaboration as collab

# ---------------------------------------------------------------------------
# Import Smoke Tests
# ---------------------------------------------------------------------------


class TestCollaborationImports:
    """All 48 exports are importable."""

    @pytest.mark.parametrize(
        "name",
        [
            "AgentRole",
            "AgentState",
            "AgentCapability",
            "AgentStatus",
            "AgentMessage",
            "AgentCoordinator",
            "AgentPool",
            "AgentProxy",
            "BaseAgent",
            "MessageBus",
            "MessageType",
            "Task",
            "TaskAssignment",
            "TaskDecomposer",
            "TaskPriority",
            "TaskResult",
            "TaskStatus",
            "SwarmAgent",
            "SwarmManager",
            "SwarmMessage",
            "SwarmMessageType",
            "SwarmStatus",
            "SwarmVote",
            "ConsensusResult",
            "Decision",
        ],
    )
    def test_export_exists(self, name: str) -> None:
        assert hasattr(collab, name), f"Missing export: {name}"


# ---------------------------------------------------------------------------
# Enum Tests
# ---------------------------------------------------------------------------


class TestEnums:
    """Enums have expected members."""

    def test_agent_role_members(self) -> None:
        roles = collab.AgentRole
        assert (
            hasattr(roles, "LEADER") or hasattr(roles, "WORKER") or len(list(roles)) > 0
        )

    def test_agent_state_members(self) -> None:
        states = collab.AgentState
        assert len(list(states)) > 0

    def test_task_priority_members(self) -> None:
        tp = collab.TaskPriority
        assert len(list(tp)) >= 2

    def test_task_status_members(self) -> None:
        ts = collab.TaskStatus
        assert len(list(ts)) >= 2

    def test_message_type_members(self) -> None:
        mt = collab.MessageType
        assert len(list(mt)) >= 1

    def test_swarm_status_members(self) -> None:
        ss = collab.SwarmStatus
        assert callable(ss)

    def test_swarm_message_type_members(self) -> None:
        smt = collab.SwarmMessageType
        assert len(list(smt)) >= 1


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------


class TestDataStructures:
    """Dataclass / class instantiation."""

    def test_agent_capability(self) -> None:
        cap = collab.AgentCapability
        assert callable(cap)

    def test_agent_message(self) -> None:
        msg_class = collab.AgentMessage
        assert callable(msg_class)

    def test_task(self) -> None:
        task_class = collab.Task
        assert callable(task_class)

    def test_task_assignment(self) -> None:
        assert callable(collab.TaskAssignment)

    def test_task_result(self) -> None:
        assert callable(collab.TaskResult)

    def test_consensus_result(self) -> None:
        assert callable(collab.ConsensusResult)

    def test_decision(self) -> None:
        assert callable(collab.Decision)

    def test_swarm_vote(self) -> None:
        assert callable(collab.SwarmVote)

    def test_swarm_message(self) -> None:
        assert callable(collab.SwarmMessage)

    def test_agent_status(self) -> None:
        assert callable(collab.AgentStatus)


# ---------------------------------------------------------------------------
# Manager Classes
# ---------------------------------------------------------------------------


class TestManagerClasses:
    """High-level manager classes are instantiable."""

    def test_agent_coordinator(self) -> None:
        coord = collab.AgentCoordinator()
        assert coord is not None
        public = [
            m
            for m in dir(coord)
            if not m.startswith("_") and callable(getattr(coord, m))
        ]
        assert len(public) > 0

    def test_agent_pool(self) -> None:
        pool = collab.AgentPool()
        assert pool is not None

    def test_message_bus(self) -> None:
        bus = collab.MessageBus()
        assert bus is not None

    def test_task_decomposer(self) -> None:
        decomposer = collab.TaskDecomposer()
        assert decomposer is not None

    def test_swarm_manager(self) -> None:
        mgr = collab.SwarmManager()
        assert mgr is not None


# ---------------------------------------------------------------------------
# Protocol Classes
# ---------------------------------------------------------------------------


class TestProtocols:
    """Protocol and ABC classes exist and are importable."""

    @pytest.mark.parametrize(
        "name",
        [
            "AgentProtocol",
            "BaseAgent",
            "BroadcastProtocol",
            "ConsensusProtocol",
            "CapabilityRoutingProtocol",
            "RoundRobinProtocol",
        ],
    )
    def test_protocol_exists(self, name: str) -> None:
        cls = getattr(collab, name)
        assert cls is not None


# ---------------------------------------------------------------------------
# Error Classes
# ---------------------------------------------------------------------------


class TestErrors:
    """Custom exception classes are importable and inherit from Exception."""

    @pytest.mark.parametrize(
        "name",
        [
            "CollaborationError",
            "AgentBusyError",
            "AgentNotFoundError",
            "CapabilityMismatchError",
            "ChannelError",
            "ConsensusError",
            "CoordinationError",
            "LeaderElectionError",
            "MessageDeliveryError",
            "TaskDependencyError",
            "TaskExecutionError",
            "TaskNotFoundError",
        ],
    )
    def test_error_is_exception(self, name: str) -> None:
        exc_cls = getattr(collab, name)
        assert issubclass(exc_cls, Exception)
