"""
Consensus mechanisms for multi-agent agreement.

Provides voting mechanisms and consensus building for
collaborative decision making.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from collections.abc import Callable

from ..agents.base import CollaborativeAgent

logger = logging.getLogger(__name__)


class VoteType(Enum):
    """Types of votes."""
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"


@dataclass
class Vote:
    """A vote cast by an agent."""
    voter_id: str
    vote: VoteType
    timestamp: datetime = field(default_factory=datetime.now)
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "voter_id": self.voter_id,
            "vote": self.vote.value,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
        }


@dataclass
class Proposal:
    """A proposal to be voted on."""
    proposal_id: str
    title: str
    description: str
    proposer_id: str
    created_at: datetime = field(default_factory=datetime.now)
    deadline: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "description": self.description,
            "proposer_id": self.proposer_id,
            "created_at": self.created_at.isoformat(),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "metadata": self.metadata,
        }


@dataclass
class VotingResult:
    """Result of a voting round."""
    proposal_id: str
    passed: bool
    votes_for: int
    votes_against: int
    abstentions: int
    total_voters: int
    quorum_met: bool
    votes: list[Vote] = field(default_factory=list)

    @property
    def participation_rate(self) -> float:
        """Calculate voter participation rate."""
        if self.total_voters == 0:
            return 0.0
        return (self.votes_for + self.votes_against + self.abstentions) / self.total_voters

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "passed": self.passed,
            "votes_for": self.votes_for,
            "votes_against": self.votes_against,
            "abstentions": self.abstentions,
            "total_voters": self.total_voters,
            "quorum_met": self.quorum_met,
            "participation_rate": self.participation_rate,
            "votes": [v.to_dict() for v in self.votes],
        }


class VotingMechanism:
    """
    Manages voting processes for multi-agent consensus.

    Supports various voting strategies including simple majority,
    supermajority, and unanimity.

    Attributes:
        quorum: Minimum participation rate (0.0 to 1.0).
        threshold: Vote ratio needed to pass (0.0 to 1.0).
    """

    def __init__(
        self,
        quorum: float = 0.5,
        threshold: float = 0.5,
    ):
        if not 0 <= quorum <= 1:
            raise ValueError("Quorum must be between 0 and 1")
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")

        self._quorum = quorum
        self._threshold = threshold
        self._active_proposals: dict[str, Proposal] = {}
        self._votes: dict[str, dict[str, Vote]] = {}  # proposal_id -> voter_id -> Vote
        self._results: dict[str, VotingResult] = {}

    def create_proposal(
        self,
        title: str,
        description: str,
        proposer_id: str,
        deadline: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Proposal:
        """Create a new proposal for voting."""
        proposal = Proposal(
            proposal_id=str(uuid.uuid4()),
            title=title,
            description=description,
            proposer_id=proposer_id,
            deadline=deadline,
            metadata=metadata or {},
        )
        self._active_proposals[proposal.proposal_id] = proposal
        self._votes[proposal.proposal_id] = {}
        logger.info(f"Proposal created: {title} ({proposal.proposal_id})")
        return proposal

    def cast_vote(
        self,
        proposal_id: str,
        voter_id: str,
        vote: VoteType,
        reason: str | None = None,
    ) -> Vote:
        """
        Cast a vote on a proposal.

        Raises:
            ValueError: If proposal not found or voting closed.
        """
        if proposal_id not in self._active_proposals:
            raise ValueError(f"Proposal not found: {proposal_id}")

        proposal = self._active_proposals[proposal_id]
        if proposal.deadline and datetime.now() > proposal.deadline:
            raise ValueError("Voting deadline has passed")

        vote_obj = Vote(
            voter_id=voter_id,
            vote=vote,
            reason=reason,
        )
        self._votes[proposal_id][voter_id] = vote_obj
        logger.info(f"Vote cast: {voter_id} voted {vote.value} on {proposal_id}")
        return vote_obj

    def get_votes(self, proposal_id: str) -> list[Vote]:
        """Get all votes for a proposal."""
        return list(self._votes.get(proposal_id, {}).values())

    def tally_votes(
        self,
        proposal_id: str,
        total_voters: int,
    ) -> VotingResult:
        """
        Tally votes and determine the result.

        Args:
            proposal_id: ID of the proposal.
            total_voters: Total number of eligible voters.

        Returns:
            The voting result.
        """
        if proposal_id not in self._active_proposals:
            raise ValueError(f"Proposal not found: {proposal_id}")

        votes = self.get_votes(proposal_id)

        votes_for = sum(1 for v in votes if v.vote == VoteType.YES)
        votes_against = sum(1 for v in votes if v.vote == VoteType.NO)
        abstentions = sum(1 for v in votes if v.vote == VoteType.ABSTAIN)

        # Check quorum
        participation = len(votes) / total_voters if total_voters > 0 else 0
        quorum_met = participation >= self._quorum

        # Check if passed
        decisive_votes = votes_for + votes_against
        if decisive_votes > 0:
            approval_rate = votes_for / decisive_votes
        else:
            approval_rate = 0

        passed = quorum_met and approval_rate >= self._threshold

        result = VotingResult(
            proposal_id=proposal_id,
            passed=passed,
            votes_for=votes_for,
            votes_against=votes_against,
            abstentions=abstentions,
            total_voters=total_voters,
            quorum_met=quorum_met,
            votes=votes,
        )

        self._results[proposal_id] = result
        del self._active_proposals[proposal_id]
        del self._votes[proposal_id]

        logger.info(f"Voting complete: {proposal_id} - {'PASSED' if passed else 'REJECTED'}")
        return result

    def get_result(self, proposal_id: str) -> VotingResult | None:
        """Get the result of a completed vote."""
        return self._results.get(proposal_id)


class ConsensusBuilder:
    """
    Facilitates reaching consensus among agents.

    Provides methods for value convergence, conflict resolution,
    and agreement tracking.
    """

    def __init__(self, convergence_threshold: float = 0.8):
        self._convergence_threshold = convergence_threshold
        self._proposals: dict[str, dict[str, Any]] = {}  # key -> agent_id -> value
        self._consensus_values: dict[str, Any] = {}

    def propose_value(
        self,
        key: str,
        agent_id: str,
        value: Any,
    ) -> None:
        """Propose a value for a key."""
        if key not in self._proposals:
            self._proposals[key] = {}
        self._proposals[key][agent_id] = value

    def check_consensus(
        self,
        key: str,
        total_agents: int,
    ) -> Any | None:
        """
        Check if consensus has been reached for a key.

        Returns the consensus value if reached, None otherwise.
        """
        if key not in self._proposals:
            return None

        proposals = self._proposals[key]
        if not proposals:
            return None

        # Count occurrences of each value
        value_counts: dict[str, int] = {}
        for value in proposals.values():
            # Use string representation for hashing
            key_str = str(value)
            value_counts[key_str] = value_counts.get(key_str, 0) + 1

        # Find most common value
        if not value_counts:
            return None

        max_count = max(value_counts.values())
        agreement_rate = max_count / total_agents

        if agreement_rate >= self._convergence_threshold:
            # Find the actual value (not the string key)
            for value in proposals.values():
                if str(value) == max(value_counts.keys(), key=lambda k: value_counts[k]):
                    self._consensus_values[key] = value
                    return value

        return None

    def get_consensus(self, key: str) -> Any | None:
        """Get the consensus value for a key if one was reached."""
        return self._consensus_values.get(key)

    def get_proposals(self, key: str) -> dict[str, Any]:
        """Get all proposals for a key."""
        return self._proposals.get(key, {})

    def clear(self, key: str | None = None) -> None:
        """Clear proposals, optionally for a specific key."""
        if key:
            self._proposals.pop(key, None)
            self._consensus_values.pop(key, None)
        else:
            self._proposals.clear()
            self._consensus_values.clear()

    async def reach_consensus(
        self,
        key: str,
        agents: list[CollaborativeAgent],
        value_fn: Callable[[CollaborativeAgent], Any],
        max_rounds: int = 5,
    ) -> Any | None:
        """
        Attempt to reach consensus through iterative rounds.

        Args:
            key: Key for the consensus value.
            agents: Agents participating in consensus.
            value_fn: Function to get each agent's proposed value.
            max_rounds: Maximum rounds before giving up.

        Returns:
            The consensus value if reached, None otherwise.
        """
        for round_num in range(max_rounds):
            # Collect proposals
            for agent in agents:
                try:
                    value = value_fn(agent)
                    self.propose_value(key, agent.agent_id, value)
                except Exception as e:
                    logger.warning(f"Agent {agent.agent_id} failed to propose: {e}")

            # Check consensus
            consensus = self.check_consensus(key, len(agents))
            if consensus is not None:
                logger.info(f"Consensus reached for {key} in round {round_num + 1}")
                return consensus

            await asyncio.sleep(0.1)  # Brief delay between rounds

        logger.warning(f"Consensus not reached for {key} after {max_rounds} rounds")
        return None


__all__ = [
    "VoteType",
    "Vote",
    "Proposal",
    "VotingResult",
    "VotingMechanism",
    "ConsensusBuilder",
]
