"""Unit tests for collaboration/exceptions.py.

Verifies constructor signatures and attribute correctness for every
exception in the collaboration module. All exceptions must be raiseable,
catchable as CollaborationError, and expose the documented attributes.
"""

import pytest

from codomyrmex.collaboration.exceptions import (  # direct submodule, no __init__ side-effects
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

pytestmark = pytest.mark.unit


class TestCollaborationError:
    """Tests for the CollaborationError base class."""

    def test_message_attribute_is_set(self):
        assert CollaborationError("some failure").message == "some failure"

    def test_details_defaults_to_empty_dict(self):
        assert CollaborationError("failure").details == {}

    def test_details_can_be_set(self):
        exc = CollaborationError("failure", details={"key": "val"})
        assert exc.details == {"key": "val"}

    def test_is_exception_subclass(self):
        assert isinstance(CollaborationError("x"), Exception)

    def test_str_representation_contains_message(self):
        assert "specific message" in str(CollaborationError("specific message"))

    def test_raises_cleanly(self):
        with pytest.raises(CollaborationError):
            raise CollaborationError("base failure")


class TestAgentNotFoundError:
    """Tests for AgentNotFoundError."""

    def test_agent_id_attribute(self):
        assert AgentNotFoundError("agent-42").agent_id == "agent-42"

    def test_default_message_includes_agent_id(self):
        assert "agent-42" in str(AgentNotFoundError("agent-42"))

    def test_custom_message_overrides_default(self):
        exc = AgentNotFoundError("agent-42", message="custom message")
        assert "custom message" in str(exc)

    def test_details_contains_agent_id(self):
        assert AgentNotFoundError("agent-7").details["agent_id"] == "agent-7"

    def test_raises_cleanly(self):
        with pytest.raises(AgentNotFoundError):
            raise AgentNotFoundError("agent-42")


class TestAgentBusyError:
    """Tests for AgentBusyError."""

    def test_agent_id_attribute(self):
        assert AgentBusyError("agent-1").agent_id == "agent-1"

    def test_current_task_id_defaults_to_none(self):
        assert AgentBusyError("agent-1").current_task_id is None

    def test_current_task_id_included_in_message(self):
        exc = AgentBusyError("agent-1", current_task_id="task-99")
        assert "task-99" in str(exc)
        assert exc.current_task_id == "task-99"

    def test_message_contains_agent_id(self):
        assert "agent-1" in str(AgentBusyError("agent-1"))

    def test_raises_cleanly(self):
        with pytest.raises(AgentBusyError):
            raise AgentBusyError("agent-1")


class TestTaskExecutionError:
    """Tests for TaskExecutionError."""

    def test_task_id_attribute(self):
        assert TaskExecutionError("task-1", "timeout").task_id == "task-1"

    def test_reason_attribute(self):
        assert TaskExecutionError("task-1", "timeout").reason == "timeout"

    def test_agent_id_defaults_to_none(self):
        assert TaskExecutionError("task-1", "fail").agent_id is None

    def test_agent_id_can_be_provided(self):
        exc = TaskExecutionError("task-1", "fail", agent_id="agent-5")
        assert exc.agent_id == "agent-5"

    def test_message_contains_task_and_reason(self):
        exc = TaskExecutionError("task-1", "disk full")
        assert "task-1" in str(exc) and "disk full" in str(exc)

    def test_raises_cleanly(self):
        with pytest.raises(TaskExecutionError):
            raise TaskExecutionError("task-1", "out of memory")


class TestTaskNotFoundError:
    """Tests for TaskNotFoundError."""

    def test_task_id_attribute(self):
        assert TaskNotFoundError("task-99").task_id == "task-99"

    def test_message_includes_task_id(self):
        assert "task-99" in str(TaskNotFoundError("task-99"))

    def test_raises_cleanly(self):
        with pytest.raises(TaskNotFoundError):
            raise TaskNotFoundError("task-99")


class TestTaskDependencyError:
    """Tests for TaskDependencyError."""

    def test_task_id_attribute(self):
        assert TaskDependencyError("task-A", ["task-B"]).task_id == "task-A"

    def test_missing_dependencies_attribute(self):
        exc = TaskDependencyError("task-A", ["task-B", "task-C"])
        assert exc.missing_dependencies == ["task-B", "task-C"]

    def test_message_contains_task_id(self):
        assert "task-A" in str(TaskDependencyError("task-A", ["task-B"]))

    def test_raises_cleanly(self):
        with pytest.raises(TaskDependencyError):
            raise TaskDependencyError("task-A", ["task-B", "task-C"])


class TestConsensusError:
    """Tests for ConsensusError — takes (message, details=None) signature."""

    def test_message_attribute(self):
        assert ConsensusError("agents disagreed").message == "agents disagreed"

    def test_details_defaults_to_empty_dict(self):
        assert ConsensusError("fail").details == {}

    def test_details_none_normalised_to_empty_dict(self):
        assert ConsensusError("fail", details=None).details == {}

    def test_details_dict_stored_correctly(self):
        exc = ConsensusError("fail", details={"round": 3, "agents": 5})
        assert exc.details["round"] == 3
        assert exc.details["agents"] == 5

    def test_str_contains_message(self):
        assert "all agents failed" in str(ConsensusError("all agents failed"))

    def test_raises_cleanly(self):
        with pytest.raises(ConsensusError):
            raise ConsensusError("no consensus reached")


class TestChannelError:
    """Tests for ChannelError."""

    def test_channel_id_attribute(self):
        assert ChannelError("ch-1", "timeout").channel_id == "ch-1"

    def test_reason_attribute(self):
        assert ChannelError("ch-1", "timeout").reason == "timeout"

    def test_message_contains_channel_and_reason(self):
        exc = ChannelError("ch-1", "connection refused")
        assert "ch-1" in str(exc) and "connection refused" in str(exc)

    def test_raises_cleanly(self):
        with pytest.raises(ChannelError):
            raise ChannelError("ch-1", "connection refused")


class TestMessageDeliveryError:
    """Tests for MessageDeliveryError."""

    def test_message_id_attribute(self):
        exc = MessageDeliveryError("msg-1", "sender-A", "receiver-B", "dropped")
        assert exc.message_id == "msg-1"

    def test_routing_attributes_set(self):
        exc = MessageDeliveryError("msg-1", "sender-A", "receiver-B", "queue full")
        assert exc.sender_id == "sender-A"
        assert exc.receiver_id == "receiver-B"
        assert exc.reason == "queue full"

    def test_message_string_contains_all_ids(self):
        exc = MessageDeliveryError("msg-1", "sender-A", "receiver-B", "dropped")
        s = str(exc)
        assert "msg-1" in s and "sender-A" in s and "receiver-B" in s

    def test_raises_cleanly(self):
        with pytest.raises(MessageDeliveryError):
            raise MessageDeliveryError("msg-1", "sender-A", "receiver-B", "queue full")


class TestCoordinationError:
    """Tests for CoordinationError."""

    def test_operation_attribute(self):
        assert (
            CoordinationError("leader-election", "timeout").operation
            == "leader-election"
        )

    def test_reason_attribute(self):
        assert CoordinationError("leader-election", "timeout").reason == "timeout"

    def test_message_contains_both_fields(self):
        exc = CoordinationError("leader-election", "no candidates")
        s = str(exc)
        assert "leader-election" in s and "no candidates" in s

    def test_raises_cleanly(self):
        with pytest.raises(CoordinationError):
            raise CoordinationError("leader-election", "no candidates")


class TestLeaderElectionError:
    """Tests for LeaderElectionError."""

    def test_reason_attribute(self):
        assert (
            LeaderElectionError("no agents available").reason == "no agents available"
        )

    def test_candidates_defaults_to_empty_list(self):
        assert LeaderElectionError("fail").candidates == []

    def test_candidates_stored_when_provided(self):
        exc = LeaderElectionError("split vote", candidates=["a1", "a2"])
        assert exc.candidates == ["a1", "a2"]

    def test_message_contains_reason(self):
        assert "no agents available" in str(LeaderElectionError("no agents available"))

    def test_raises_cleanly(self):
        with pytest.raises(LeaderElectionError):
            raise LeaderElectionError("no agents available")


class TestCapabilityMismatchError:
    """Tests for CapabilityMismatchError."""

    def test_required_capabilities_attribute(self):
        exc = CapabilityMismatchError(["compute", "store"])
        assert exc.required_capabilities == ["compute", "store"]

    def test_available_capabilities_defaults_to_empty(self):
        assert CapabilityMismatchError(["compute"]).available_capabilities == []

    def test_available_capabilities_stored_when_provided(self):
        exc = CapabilityMismatchError(["compute"], available_capabilities=["store"])
        assert exc.available_capabilities == ["store"]

    def test_message_contains_required_capability_name(self):
        assert "compute" in str(CapabilityMismatchError(["compute", "store"]))

    def test_raises_cleanly(self):
        with pytest.raises(CapabilityMismatchError):
            raise CapabilityMismatchError(["compute", "store"])


class TestExceptionHierarchy:
    """Verifies the full hierarchy — all subclasses catchable as CollaborationError."""

    def test_all_subclasses_are_collaboration_errors(self):
        instances = [
            AgentNotFoundError("a"),
            AgentBusyError("a"),
            TaskExecutionError("t", "r"),
            TaskNotFoundError("t"),
            TaskDependencyError("t", []),
            ConsensusError("m"),
            ChannelError("c", "r"),
            MessageDeliveryError("m", "s", "r", "reason"),
            CoordinationError("op", "r"),
            LeaderElectionError("r"),
            CapabilityMismatchError(["c"]),
        ]
        for exc in instances:
            assert isinstance(exc, CollaborationError), (
                f"{type(exc).__name__} must be a CollaborationError"
            )

    def test_consensus_error_catchable_as_collaboration_error(self):
        with pytest.raises(CollaborationError):
            raise ConsensusError("caught as base")

    def test_channel_error_catchable_as_collaboration_error(self):
        with pytest.raises(CollaborationError):
            raise ChannelError("ch", "reason")

    def test_all_errors_are_base_exceptions(self):
        for exc in [
            CollaborationError("x"),
            ConsensusError("x"),
            ChannelError("c", "r"),
        ]:
            assert isinstance(exc, Exception)
