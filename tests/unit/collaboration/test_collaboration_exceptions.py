"""Tests for collaboration.exceptions module."""

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


class TestCollaborationError:
    def test_basic(self):
        e = CollaborationError("base error")
        assert str(e) == "base error"
        assert e.details == {}

    def test_with_details(self):
        e = CollaborationError("error", details={"key": "val"})
        assert e.details["key"] == "val"


class TestAgentErrors:
    def test_agent_not_found(self):
        e = AgentNotFoundError("agent_1")
        assert e.agent_id == "agent_1"
        assert "agent_1" in str(e)

    def test_agent_not_found_custom_message(self):
        e = AgentNotFoundError("agent_1", message="custom msg")
        assert str(e) == "custom msg"

    def test_agent_busy_no_task(self):
        e = AgentBusyError("agent_2")
        assert e.agent_id == "agent_2"
        assert e.current_task_id is None

    def test_agent_busy_with_task(self):
        e = AgentBusyError("agent_2", current_task_id="task_99")
        assert e.current_task_id == "task_99"
        assert "task_99" in str(e)


class TestTaskErrors:
    def test_task_execution_error(self):
        e = TaskExecutionError("t1", "network failure", agent_id="a1")
        assert e.task_id == "t1"
        assert e.reason == "network failure"
        assert e.agent_id == "a1"
        assert "t1" in str(e)

    def test_task_not_found(self):
        e = TaskNotFoundError("task_xyz")
        assert e.task_id == "task_xyz"
        assert "task_xyz" in str(e)

    def test_task_dependency_error(self):
        e = TaskDependencyError("task_a", ["task_b", "task_c"])
        assert e.task_id == "task_a"
        assert "task_b" in e.missing_dependencies
        assert "task_c" in e.missing_dependencies


class TestCommunicationErrors:
    def test_consensus_error(self):
        e = ConsensusError("no consensus", details={"votes": 2})
        assert e.details["votes"] == 2

    def test_channel_error(self):
        e = ChannelError("ch_1", "connection refused")
        assert e.channel_id == "ch_1"
        assert e.reason == "connection refused"
        assert "ch_1" in str(e)

    def test_message_delivery_error(self):
        e = MessageDeliveryError("msg_1", "sender", "receiver", "timeout")
        assert e.message_id == "msg_1"
        assert e.sender_id == "sender"
        assert e.receiver_id == "receiver"
        assert e.reason == "timeout"


class TestCoordinationErrors:
    def test_coordination_error(self):
        e = CoordinationError("leader_election", "no quorum")
        assert e.operation == "leader_election"
        assert e.reason == "no quorum"

    def test_leader_election_error(self):
        e = LeaderElectionError("split brain", candidates=["a1", "a2"])
        assert e.reason == "split brain"
        assert "a1" in e.candidates

    def test_leader_election_no_candidates(self):
        e = LeaderElectionError("no candidates")
        assert e.candidates == []

    def test_capability_mismatch(self):
        e = CapabilityMismatchError(["gpu", "tpu"], ["cpu"])
        assert "gpu" in e.required_capabilities
        assert "cpu" in e.available_capabilities

    def test_capability_mismatch_no_available(self):
        e = CapabilityMismatchError(["gpu"])
        assert e.available_capabilities == []


class TestExceptionHierarchy:
    def test_all_inherit_collaboration_error(self):
        classes = [
            AgentNotFoundError,
            AgentBusyError,
            TaskExecutionError,
            TaskNotFoundError,
            TaskDependencyError,
            ConsensusError,
            ChannelError,
            MessageDeliveryError,
            CoordinationError,
            LeaderElectionError,
            CapabilityMismatchError,
        ]
        for cls in classes:
            assert issubclass(cls, CollaborationError), (
                f"{cls.__name__} must inherit CollaborationError"
            )

    def test_all_inherit_exception(self):
        assert issubclass(CollaborationError, Exception)
