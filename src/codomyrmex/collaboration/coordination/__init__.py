"""
Task coordination submodule.

Task distribution, consensus protocols, and leader election
for multi-agent collaboration.
"""

from .consensus import (
    ConsensusBuilder,
    Proposal,
    Vote,
    VoteType,
    VotingMechanism,
    VotingResult,
)
from .leader_election import (
    BullyElection,
    ElectionResult,
    ElectionState,
    LeaderElection,
    RandomElection,
    RingElection,
    RotatingLeadership,
)
from .task_manager import (
    DependencyGraph,
    SchedulingStrategy,
    TaskManager,
    TaskQueue,
)

__all__ = [
    # Task management
    "SchedulingStrategy",
    "TaskQueue",
    "DependencyGraph",
    "TaskManager",
    # Consensus
    "VoteType",
    "Vote",
    "Proposal",
    "VotingResult",
    "VotingMechanism",
    "ConsensusBuilder",
    # Leader election
    "ElectionState",
    "ElectionResult",
    "LeaderElection",
    "BullyElection",
    "RingElection",
    "RandomElection",
    "RotatingLeadership",
]
