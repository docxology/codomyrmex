"""Task coordination submodule.

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
    "BullyElection",
    "ConsensusBuilder",
    "DependencyGraph",
    "ElectionResult",
    # Leader election
    "ElectionState",
    "LeaderElection",
    "Proposal",
    "RandomElection",
    "RingElection",
    "RotatingLeadership",
    # Task management
    "SchedulingStrategy",
    "TaskManager",
    "TaskQueue",
    "Vote",
    # Consensus
    "VoteType",
    "VotingMechanism",
    "VotingResult",
]
