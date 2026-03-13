"""Leader election protocols for multi-agent coordination.

Provides algorithms for selecting a coordinator or leader
among a group of agents.
"""

import random
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from codomyrmex.collaboration.agents.base import CollaborativeAgent
from codomyrmex.collaboration.protocols import AgentState
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class ElectionState(Enum):
    """State of an election process."""

    IDLE = "idle"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ElectionResult:
    """Result of a leader election."""

    leader_id: str | None
    success: bool
    round_count: int
    participants: list[str]
    timestamp: datetime = field(default_factory=datetime.now)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "leader_id": self.leader_id,
            "success": self.success,
            "round_count": self.round_count,
            "participants": self.participants,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
        }


class LeaderElection(ABC):
    """Base leader election protocol.

    Provides common functionality for leader election algorithms.
    """

    def __init__(self):
        self._state = ElectionState.IDLE
        self._current_leader: str | None = None
        self._participants: set[str] = set()
        self._election_history: list[ElectionResult] = []

    @property
    def state(self) -> ElectionState:
        """State."""
        return self._state

    @property
    def current_leader(self) -> str | None:
        return self._current_leader

    def get_history(self) -> list[ElectionResult]:
        """Get election history."""
        return self._election_history.copy()

    @abstractmethod
    async def elect(self, agents: list[CollaborativeAgent]) -> ElectionResult:
        """Run an election among the given agents.

        This is the base implementation - subclasses should override.
        """
        raise NotImplementedError(
            "Subclasses must implement elect()"
        )  # ABC: intentional

    def _filter_healthy(
        self, agents: list[CollaborativeAgent]
    ) -> list[CollaborativeAgent]:
        """Return only agents not in ERROR state."""
        return [a for a in agents if a.state != AgentState.ERROR]

    def _record_result(self, result: ElectionResult) -> None:
        """Record an election result."""
        self._election_history.append(result)
        if result.success:
            self._current_leader = result.leader_id
        self._state = (
            ElectionState.COMPLETED if result.success else ElectionState.FAILED
        )

    def _prepare_election(
        self, agents: list[CollaborativeAgent]
    ) -> tuple[list[CollaborativeAgent], ElectionResult | None]:
        """Validate agents and set up election state.

        Returns (healthy_agents, failure_result). If failure_result is not None
        the caller should record it and return immediately.
        """
        if not agents:
            return [], ElectionResult(
                leader_id=None,
                success=False,
                round_count=0,
                participants=[],
                error="No agents to elect from",
            )
        self._state = ElectionState.IN_PROGRESS
        self._participants = {a.agent_id for a in agents}
        healthy = self._filter_healthy(agents)
        if not healthy:
            return [], ElectionResult(
                leader_id=None,
                success=False,
                round_count=1,
                participants=list(self._participants),
                error="No healthy agents available",
            )
        return healthy, None


class BullyElection(LeaderElection):
    """Bully algorithm for leader election.

    The agent with the highest priority (determined by a scoring function)
    becomes the leader. Higher-priority agents can "bully" lower-priority
    ones out of contention.

    Attributes:
        priority_fn: Function to determine agent priority (higher = more priority).
        timeout: Timeout for waiting for responses.

    """

    def __init__(
        self,
        priority_fn: Callable[[CollaborativeAgent], float] | None = None,
        timeout: float = 5.0,
    ):
        super().__init__()
        self._priority_fn = priority_fn or self._default_priority
        self._timeout = timeout

    @staticmethod
    def _default_priority(agent: CollaborativeAgent) -> float:
        """Default priority based on agent ID hash."""
        return hash(agent.agent_id)

    async def elect(self, agents: list[CollaborativeAgent]) -> ElectionResult:
        """Run the bully election algorithm."""
        healthy_agents, failure = self._prepare_election(agents)
        if failure is not None:
            self._record_result(failure)
            return failure

        leader = sorted(healthy_agents, key=self._priority_fn, reverse=True)[0]
        result = ElectionResult(
            leader_id=leader.agent_id,
            success=True,
            round_count=1,
            participants=list(self._participants),
        )
        self._record_result(result)
        logger.info(
            "Bully election complete: Leader is %s (%s)", leader.name, leader.agent_id
        )
        return result


class RingElection(LeaderElection):
    """Ring-based leader election.

    Agents are arranged in a logical ring and pass election messages
    around until the highest-priority agent is determined.
    """

    def __init__(
        self,
        priority_fn: Callable[[CollaborativeAgent], float] | None = None,
    ):
        super().__init__()
        self._priority_fn = priority_fn or (lambda a: hash(a.agent_id))

    async def elect(self, agents: list[CollaborativeAgent]) -> ElectionResult:
        """Run the ring election algorithm (simulated ring traversal)."""
        healthy_agents, failure = self._prepare_election(agents)
        if failure is not None:
            self._record_result(failure)
            return failure

        candidates = [(self._priority_fn(a), a) for a in healthy_agents]
        candidates.sort(key=lambda x: x[0], reverse=True)
        leader = candidates[0][1]
        result = ElectionResult(
            leader_id=leader.agent_id,
            success=True,
            round_count=len(healthy_agents),
            participants=list(self._participants),
        )
        self._record_result(result)
        logger.info(
            "Ring election complete: Leader is %s (%s)", leader.name, leader.agent_id
        )
        return result


class RandomElection(LeaderElection):
    """Random leader election.

    Randomly selects a leader from the available agents.
    Useful for load balancing or when all agents are equal.
    """

    async def elect(self, agents: list[CollaborativeAgent]) -> ElectionResult:
        """Randomly select a leader."""
        healthy_agents, failure = self._prepare_election(agents)
        if failure is not None:
            self._record_result(failure)
            return failure

        leader = random.choice(healthy_agents)
        result = ElectionResult(
            leader_id=leader.agent_id,
            success=True,
            round_count=1,
            participants=list(self._participants),
        )
        self._record_result(result)
        logger.info(
            "Random election complete: Leader is %s (%s)", leader.name, leader.agent_id
        )
        return result


class RotatingLeadership:
    """Rotating leadership pattern.

    Cycles through agents as leader, ensuring fair distribution
    of leadership responsibilities.
    """

    def __init__(self, agents: list[CollaborativeAgent] | None = None):
        self._agents: list[CollaborativeAgent] = agents or []
        self._current_index = 0
        self._term_count = 0

    def add_agent(self, agent: CollaborativeAgent) -> None:
        """Add an agent to the rotation."""
        if agent not in self._agents:
            self._agents.append(agent)

    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the rotation."""
        for i, agent in enumerate(self._agents):
            if agent.agent_id == agent_id:
                self._agents.pop(i)
                # Adjust index if needed
                if i <= self._current_index and self._current_index > 0:
                    self._current_index -= 1
                return True
        return False

    def get_current_leader(self) -> CollaborativeAgent | None:
        """Get the current leader."""
        if not self._agents:
            return None
        return self._agents[self._current_index % len(self._agents)]

    def rotate(self) -> CollaborativeAgent | None:
        """Rotate to the next leader."""
        if not self._agents:
            return None

        self._current_index = (self._current_index + 1) % len(self._agents)
        self._term_count += 1

        leader = self._agents[self._current_index]
        logger.info("Leadership rotated to %s (term %s)", leader.name, self._term_count)
        return leader

    def get_term_count(self) -> int:
        """Get the current term count."""
        return self._term_count


__all__ = [
    "BullyElection",
    "ElectionResult",
    "ElectionState",
    "LeaderElection",
    "RandomElection",
    "RingElection",
    "RotatingLeadership",
]
