"""Consensus strategies for swarm decision-making.

Three strategies: majority vote, weighted vote, and veto consensus.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class Decision(Enum):
    """Outcome of a consensus round."""
    APPROVED = "approved"
    REJECTED = "rejected"
    DEADLOCK = "deadlock"
    VETOED = "vetoed"


@dataclass
class Vote:
    """A single agent's vote.

    Attributes:
        agent_id: Voting agent.
        approve: True = approve, False = reject.
        weight: Vote weight (for weighted voting).
        reason: Optional rationale.
    """

    agent_id: str
    approve: bool
    weight: float = 1.0
    reason: str = ""


@dataclass
class ConsensusResult:
    """Result of a consensus round.

    Attributes:
        decision: The final decision.
        votes: All cast votes.
        approval_score: Fraction of approval (0-1).
        strategy: Strategy used.
    """

    decision: Decision
    votes: list[Vote] = field(default_factory=list)
    approval_score: float = 0.0
    strategy: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "decision": self.decision.value,
            "approval_score": round(self.approval_score, 3),
            "strategy": self.strategy,
            "votes_for": sum(1 for v in self.votes if v.approve),
            "votes_against": sum(1 for v in self.votes if not v.approve),
            "total_votes": len(self.votes),
        }


class ConsensusEngine:
    """Resolve votes using configurable strategies.

    Strategies:
        - ``majority``: Simple majority wins.
        - ``weighted``: Sum of weights determines outcome.
        - ``veto``: Any rejection = vetoed.

    Usage::

        engine = ConsensusEngine()
        votes = [Vote("alice", True), Vote("bob", False), Vote("carol", True)]
        result = engine.resolve(votes, strategy="majority")
        assert result.decision == Decision.APPROVED
    """

    def resolve(
        self,
        votes: list[Vote],
        strategy: str = "majority",
        threshold: float = 0.5,
    ) -> ConsensusResult:
        """Resolve a set of votes into a decision.

        Args:
            votes: List of votes.
            strategy: Voting strategy (``majority``, ``weighted``, ``veto``).
            threshold: Approval threshold (default 0.5 = simple majority).

        Returns:
            ``ConsensusResult`` with the decision.
        """
        if not votes:
            return ConsensusResult(
                decision=Decision.DEADLOCK,
                votes=[],
                strategy=strategy,
            )

        if strategy == "weighted":
            return self._weighted(votes, threshold)
        elif strategy == "veto":
            return self._veto(votes)
        else:
            return self._majority(votes, threshold)

    def _majority(self, votes: list[Vote], threshold: float) -> ConsensusResult:
        """Simple majority vote."""
        approvals = sum(1 for v in votes if v.approve)
        total = len(votes)
        score = approvals / total

        if score > threshold:
            decision = Decision.APPROVED
        elif score < (1.0 - threshold):
            decision = Decision.REJECTED
        else:
            decision = Decision.DEADLOCK

        result = ConsensusResult(
            decision=decision,
            votes=votes,
            approval_score=score,
            strategy="majority",
        )

        logger.info(
            "Majority vote",
            extra={"score": round(score, 2), "decision": decision.value},
        )

        return result

    def _weighted(self, votes: list[Vote], threshold: float) -> ConsensusResult:
        """Weight-based voting."""
        total_weight = sum(v.weight for v in votes)
        approval_weight = sum(v.weight for v in votes if v.approve)
        score = approval_weight / total_weight if total_weight > 0 else 0.0

        if score > threshold:
            decision = Decision.APPROVED
        elif score < (1.0 - threshold):
            decision = Decision.REJECTED
        else:
            decision = Decision.DEADLOCK

        return ConsensusResult(
            decision=decision,
            votes=votes,
            approval_score=score,
            strategy="weighted",
        )

    def _veto(self, votes: list[Vote]) -> ConsensusResult:
        """Any rejection = vetoed."""
        all_approve = all(v.approve for v in votes)
        score = sum(1 for v in votes if v.approve) / len(votes)

        return ConsensusResult(
            decision=Decision.APPROVED if all_approve else Decision.VETOED,
            votes=votes,
            approval_score=score,
            strategy="veto",
        )


__all__ = [
    "ConsensusEngine",
    "ConsensusResult",
    "Decision",
    "Vote",
]
