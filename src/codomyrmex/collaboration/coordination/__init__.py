"""
Task coordination submodule.

Task distribution, consensus protocols, and leader election
for multi-agent collaboration.
"""

from .task_manager import (
    SchedulingStrategy,
    TaskQueue,
    DependencyGraph,
    TaskManager,
)
from .consensus import (
    VoteType,
    Vote,
    Proposal,
    VotingResult,
    VotingMechanism,
    ConsensusBuilder,
)
from .leader_election import (
    ElectionState,
    ElectionResult,
    LeaderElection,
    BullyElection,
    RingElection,
    RandomElection,
    RotatingLeadership,
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
