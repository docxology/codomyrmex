"""Task coordination submodule.

Task distribution, consensus protocols, and leader election
for multi-agent collaboration.
"""

from .attestation import AttestationAuthority, TaskAttestation
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
from .raft import LogEntry, RaftCluster, RaftNode, RaftState
from .task_manager import (
    DependencyGraph,
    SchedulingStrategy,
    TaskManager,
    TaskQueue,
)

__all__ = [
    # Attestation
    "AttestationAuthority",
    "BullyElection",
    "ConsensusBuilder",
    "DependencyGraph",
    "ElectionResult",
    # Leader election
    "ElectionState",
    "LeaderElection",
    # Raft consensus (v1.3.1)
    "LogEntry",
    "Proposal",
    # Raft consensus (v1.3.1)
    "RaftCluster",
    "RaftNode",
    "RaftState",
    "RandomElection",
    "RingElection",
    "RotatingLeadership",
    # Task management
    "SchedulingStrategy",
    # Attestation
    "TaskAttestation",
    "TaskManager",
    "TaskQueue",
    "Vote",
    # Consensus
    "VoteType",
    "VotingMechanism",
    "VotingResult",
]
