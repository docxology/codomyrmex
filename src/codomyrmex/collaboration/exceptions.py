"""
Custom exceptions for the collaboration module.

Provides specific exception types for different failure scenarios
in multi-agent collaboration workflows.
"""


class CollaborationError(Exception):
    """Base exception for all collaboration module errors."""

    def __init__(self, message: str, details: dict = None):
        """Execute   Init   operations natively."""
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AgentNotFoundError(CollaborationError):
    """Raised when an agent cannot be found in the registry."""

    def __init__(self, agent_id: str, message: str = None):
        """Execute   Init   operations natively."""
        message = message or f"Agent not found: {agent_id}"
        super().__init__(message, {"agent_id": agent_id})
        self.agent_id = agent_id


class AgentBusyError(CollaborationError):
    """Raised when an agent is busy and cannot accept new tasks."""

    def __init__(self, agent_id: str, current_task_id: str = None):
        """Execute   Init   operations natively."""
        message = f"Agent {agent_id} is busy"
        if current_task_id:
            message += f" with task {current_task_id}"
        super().__init__(message, {"agent_id": agent_id, "current_task_id": current_task_id})
        self.agent_id = agent_id
        self.current_task_id = current_task_id


class TaskExecutionError(CollaborationError):
    """Raised when a task fails to execute."""

    def __init__(self, task_id: str, reason: str, agent_id: str = None):
        """Execute   Init   operations natively."""
        message = f"Task {task_id} execution failed: {reason}"
        super().__init__(message, {"task_id": task_id, "reason": reason, "agent_id": agent_id})
        self.task_id = task_id
        self.reason = reason
        self.agent_id = agent_id


class TaskNotFoundError(CollaborationError):
    """Raised when a task cannot be found."""

    def __init__(self, task_id: str):
        """Execute   Init   operations natively."""
        message = f"Task not found: {task_id}"
        super().__init__(message, {"task_id": task_id})
        self.task_id = task_id


class TaskDependencyError(CollaborationError):
    """Raised when task dependencies cannot be satisfied."""

    def __init__(self, task_id: str, missing_dependencies: list):
        """Execute   Init   operations natively."""
        message = f"Task {task_id} has unmet dependencies: {missing_dependencies}"
        super().__init__(message, {"task_id": task_id, "missing_dependencies": missing_dependencies})
        self.task_id = task_id
        self.missing_dependencies = missing_dependencies


class ConsensusError(CollaborationError):
    """Raised when consensus cannot be reached among agents."""

    def __init__(self, proposal: str, votes_for: int, votes_against: int, quorum: float):
        """Execute   Init   operations natively."""
        message = f"Consensus failed for '{proposal}': {votes_for} for, {votes_against} against (quorum: {quorum})"
        super().__init__(message, {
            "proposal": proposal,
            "votes_for": votes_for,
            "votes_against": votes_against,
            "quorum": quorum,
        })
        self.proposal = proposal
        self.votes_for = votes_for
        self.votes_against = votes_against
        self.quorum = quorum


class ChannelError(CollaborationError):
    """Raised when there's an error with a communication channel."""

    def __init__(self, channel_id: str, reason: str):
        """Execute   Init   operations natively."""
        message = f"Channel error on {channel_id}: {reason}"
        super().__init__(message, {"channel_id": channel_id, "reason": reason})
        self.channel_id = channel_id
        self.reason = reason


class MessageDeliveryError(CollaborationError):
    """Raised when a message cannot be delivered."""

    def __init__(self, message_id: str, sender_id: str, receiver_id: str, reason: str):
        """Execute   Init   operations natively."""
        message = f"Failed to deliver message {message_id} from {sender_id} to {receiver_id}: {reason}"
        super().__init__(message, {
            "message_id": message_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "reason": reason,
        })
        self.message_id = message_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.reason = reason


class CoordinationError(CollaborationError):
    """Raised when there's a coordination failure."""

    def __init__(self, operation: str, reason: str):
        """Execute   Init   operations natively."""
        message = f"Coordination failed during {operation}: {reason}"
        super().__init__(message, {"operation": operation, "reason": reason})
        self.operation = operation
        self.reason = reason


class LeaderElectionError(CollaborationError):
    """Raised when leader election fails."""

    def __init__(self, reason: str, candidates: list = None):
        """Execute   Init   operations natively."""
        message = f"Leader election failed: {reason}"
        super().__init__(message, {"reason": reason, "candidates": candidates or []})
        self.reason = reason
        self.candidates = candidates or []


class CapabilityMismatchError(CollaborationError):
    """Raised when no agent has the required capabilities."""

    def __init__(self, required_capabilities: list, available_capabilities: list = None):
        """Execute   Init   operations natively."""
        message = f"No agent has required capabilities: {required_capabilities}"
        super().__init__(message, {
            "required_capabilities": required_capabilities,
            "available_capabilities": available_capabilities or [],
        })
        self.required_capabilities = required_capabilities
        self.available_capabilities = available_capabilities or []


__all__ = [
    "CollaborationError",
    "AgentNotFoundError",
    "AgentBusyError",
    "TaskExecutionError",
    "TaskNotFoundError",
    "TaskDependencyError",
    "ConsensusError",
    "ChannelError",
    "MessageDeliveryError",
    "CoordinationError",
    "LeaderElectionError",
    "CapabilityMismatchError",
]
