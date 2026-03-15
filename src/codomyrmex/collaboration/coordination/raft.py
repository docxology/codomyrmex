"""In-memory Raft consensus protocol.

Implements the core Raft algorithm for multi-agent distributed agreement:
leader election, log replication, and commitment tracking.

Builds on :mod:`codomyrmex.collaboration.coordination.consensus`
and :mod:`codomyrmex.collaboration.swarm.consensus`.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Raft enums & data
# ---------------------------------------------------------------------------


class RaftState(Enum):
    """State of a Raft node."""

    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


@dataclass
class LogEntry:
    """A single entry in the Raft replicated log.

    Attributes:
        term: Election term when entry was created.
        index: Position in the log (1-indexed).
        command: Application-level command payload.
        committed: Whether this entry has been committed.
    """

    term: int
    index: int
    command: Any
    committed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "term": self.term,
            "index": self.index,
            "command": self.command,
            "committed": self.committed,
        }


@dataclass
class VoteResponse:
    """Response to a RequestVote RPC."""

    term: int
    vote_granted: bool


@dataclass
class AppendResponse:
    """Response to an AppendEntries RPC."""

    term: int
    success: bool
    match_index: int = 0


# ---------------------------------------------------------------------------
# Raft Node
# ---------------------------------------------------------------------------


class RaftNode:
    """A single Raft consensus node.

    Manages election state, log entries, and leader/follower transitions.

    Args:
        node_id: Unique identifier for this node.
        election_timeout_range: (min, max) ticks before election starts.
        heartbeat_interval: Ticks between leader heartbeats.
    """

    def __init__(
        self,
        node_id: str,
        election_timeout_range: tuple[int, int] = (5, 10),
        heartbeat_interval: int = 2,
    ) -> None:
        self.node_id = node_id
        self.state = RaftState.FOLLOWER
        self.current_term = 0
        self.voted_for: str | None = None
        self.log: list[LogEntry] = []
        self.commit_index = 0
        self.last_applied = 0

        # Volatile leader state
        self._next_index: dict[str, int] = {}
        self._match_index: dict[str, int] = {}

        # Timing
        self._election_timeout_range = election_timeout_range
        self._heartbeat_interval = heartbeat_interval
        self._ticks_since_heartbeat = 0
        self._election_timeout = random.randint(*election_timeout_range)

        # Election tracking
        self._votes_received: set[str] = set()

    @property
    def last_log_term(self) -> int:
        """Return the term of the last log entry, or 0 if log is empty."""
        return self.log[-1].term if self.log else 0

    @property
    def last_log_index(self) -> int:
        """Return the index of the last log entry, or 0 if log is empty."""
        return self.log[-1].index if self.log else 0

    # -- RequestVote RPC -----------------------------------------------------

    def _is_candidate_log_up_to_date(
        self, candidate_last_log_term: int, candidate_last_log_index: int
    ) -> bool:
        """Check if candidate's log is at least as up-to-date as this node's.

        Per Raft §5.4.1: a log is more up-to-date if:
        1. Its last entry has a higher term, or
        2. The terms are equal and the log is at least as long.
        """
        my_last_log_term = self.last_log_term
        my_last_log_index = self.last_log_index

        if candidate_last_log_term != my_last_log_term:
            return candidate_last_log_term > my_last_log_term
        return candidate_last_log_index >= my_last_log_index

    def request_vote(
        self,
        term: int,
        candidate_id: str,
        last_log_term: int = 0,
        last_log_index: int = 0,
    ) -> VoteResponse:
        """Handle a RequestVote RPC.

        Implements Raft §5.4.1 log comparison: a voter grants a vote only if
        the candidate's log is at least as up-to-date as its own.

        Args:
            term: Candidate's current term.
            candidate_id: Who is requesting the vote.
            last_log_term: Term of the candidate's last log entry.
            last_log_index: Index of the candidate's last log entry.

        Returns:
            VoteResponse indicating whether vote was granted.
        """
        if term < self.current_term:
            return VoteResponse(term=self.current_term, vote_granted=False)

        if term > self.current_term:
            self._step_down(term)

        can_vote = self.voted_for is None or self.voted_for == candidate_id

        # Raft §5.4.1: candidate's log must be at least as up-to-date as voter's.
        # A log is more up-to-date if its last entry has a higher term,
        # or if the terms are equal, the longer log wins.
        candidate_log_ok = self._is_candidate_log_up_to_date(
            last_log_term, last_log_index
        )

        if can_vote and candidate_log_ok:
            self.voted_for = candidate_id
            self._ticks_since_heartbeat = 0
            logger.debug(
                "%s: granted vote to %s (term %d)", self.node_id, candidate_id, term
            )
            return VoteResponse(term=self.current_term, vote_granted=True)

        return VoteResponse(term=self.current_term, vote_granted=False)

    # -- AppendEntries RPC ---------------------------------------------------

    def append_entries(
        self,
        term: int,
        leader_id: str,
        entries: list[LogEntry],
        prev_log_index: int,
        prev_log_term: int,
        leader_commit: int,
    ) -> AppendResponse:
        """Handle an AppendEntries RPC (heartbeat or log replication).

        Args:
            term: Leader's current term.
            leader_id: Who is sending.
            entries: New log entries to append.
            prev_log_index: Index of log entry before new ones.
            prev_log_term: Term of entry at prev_log_index.
            leader_commit: Leader's commit index.

        Returns:
            AppendResponse indicating success or failure.
        """
        if term < self.current_term:
            return AppendResponse(term=self.current_term, success=False)

        if term > self.current_term or self.state != RaftState.FOLLOWER:
            self._step_down(term)

        self._ticks_since_heartbeat = 0

        # Log consistency check
        if prev_log_index > 0:
            if prev_log_index > len(self.log):
                return AppendResponse(term=self.current_term, success=False)
            if self.log[prev_log_index - 1].term != prev_log_term:
                # Truncate conflicting entries
                self.log = self.log[: prev_log_index - 1]
                return AppendResponse(term=self.current_term, success=False)

        # Append new entries
        for entry in entries:
            if entry.index <= len(self.log):
                # Overwrite conflicting
                self.log[entry.index - 1] = entry
            else:
                self.log.append(entry)

        # Update commit index
        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, len(self.log))
            self._apply_committed()

        return AppendResponse(
            term=self.current_term,
            success=True,
            match_index=len(self.log),
        )

    # -- Propose (leader-only) -----------------------------------------------

    def propose(self, command: Any) -> LogEntry:
        """Propose a new command (leader-only).

        Args:
            command: Application-level command to replicate.

        Returns:
            The created LogEntry.

        Raises:
            RuntimeError: If this node is not the leader.
        """
        if self.state != RaftState.LEADER:
            raise RuntimeError(
                f"Node {self.node_id} is not the leader (state={self.state.value})"
            )

        entry = LogEntry(
            term=self.current_term,
            index=len(self.log) + 1,
            command=command,
        )
        self.log.append(entry)
        logger.info(
            "%s: proposed entry %d (term %d)", self.node_id, entry.index, entry.term
        )
        return entry

    # -- Tick ----------------------------------------------------------------

    def tick(self, cluster_size: int = 3) -> str | None:
        """Advance the timer by one tick.

        Args:
            cluster_size: Total nodes in the cluster (for majority calc).

        Returns:
            Event string if a state transition occurred, else None.
        """
        self._ticks_since_heartbeat += 1

        if self.state == RaftState.LEADER:
            if self._ticks_since_heartbeat >= self._heartbeat_interval:
                self._ticks_since_heartbeat = 0
                return "heartbeat"
            return None

        if self._ticks_since_heartbeat >= self._election_timeout:
            return self._start_election(cluster_size)

        return None

    # -- Election logic ------------------------------------------------------

    def _start_election(self, cluster_size: int) -> str:
        """Transition to candidate and start an election."""
        self.current_term += 1
        self.state = RaftState.CANDIDATE
        self.voted_for = self.node_id
        self._votes_received = {self.node_id}
        self._ticks_since_heartbeat = 0
        self._election_timeout = random.randint(*self._election_timeout_range)

        logger.info("%s: starting election (term %d)", self.node_id, self.current_term)

        # Single-node cluster: self-vote is already a majority
        majority = cluster_size // 2 + 1
        if len(self._votes_received) >= majority:
            self.state = RaftState.LEADER
            logger.info(
                "%s: became leader (term %d, single-node)",
                self.node_id,
                self.current_term,
            )
            return "became_leader"

        return "election_started"

    def receive_vote(
        self, response: VoteResponse, cluster_size: int, voter_id: str
    ) -> str | None:
        """Process a received vote response.

        Returns 'became_leader' if majority reached.
        """
        if response.term > self.current_term:
            self._step_down(response.term)
            return "stepped_down"

        if self.state != RaftState.CANDIDATE:
            return None

        if response.vote_granted:
            self._votes_received.add(voter_id)
            majority = cluster_size // 2 + 1
            if len(self._votes_received) >= majority:
                self.state = RaftState.LEADER
                self._ticks_since_heartbeat = 0
                logger.info(
                    "%s: became leader (term %d)", self.node_id, self.current_term
                )
                return "became_leader"

        return None

    # -- Internal helpers ----------------------------------------------------

    def _step_down(self, new_term: int) -> None:
        """Revert to follower for a higher term."""
        self.current_term = new_term
        self.state = RaftState.FOLLOWER
        self.voted_for = None
        self._votes_received.clear()
        self._ticks_since_heartbeat = 0
        self._election_timeout = random.randint(*self._election_timeout_range)

    def _apply_committed(self) -> None:
        """Mark entries up to commit_index as committed."""
        for i in range(self.last_applied, min(self.commit_index, len(self.log))):
            self.log[i].committed = True
        self.last_applied = max(self.last_applied, self.commit_index)

    def get_committed_entries(self) -> list[LogEntry]:
        """Return all committed log entries."""
        return [e for e in self.log if e.committed]

    def to_dict(self) -> dict[str, Any]:
        """Serialize node state."""
        return {
            "node_id": self.node_id,
            "state": self.state.value,
            "current_term": self.current_term,
            "commit_index": self.commit_index,
            "log_length": len(self.log),
            "voted_for": self.voted_for,
        }


# ---------------------------------------------------------------------------
# Raft Cluster
# ---------------------------------------------------------------------------


class RaftCluster:
    """Manage a cluster of Raft nodes, routing messages between them.

    Usage::

        cluster = RaftCluster(node_ids=["n1", "n2", "n3"])
        cluster.elect_leader()
        entry = cluster.propose("set x=1")
        assert entry.committed

    """

    def __init__(
        self,
        node_ids: list[str],
        election_timeout_range: tuple[int, int] = (5, 10),
        heartbeat_interval: int = 2,
    ) -> None:
        if not node_ids:
            raise ValueError("Cluster must have at least one node")

        self.nodes: dict[str, RaftNode] = {
            nid: RaftNode(
                node_id=nid,
                election_timeout_range=election_timeout_range,
                heartbeat_interval=heartbeat_interval,
            )
            for nid in node_ids
        }
        self._cluster_size = len(node_ids)

    @property
    def leader(self) -> RaftNode | None:
        """Return the current leader, or None."""
        for node in self.nodes.values():
            if node.state == RaftState.LEADER:
                return node
        return None

    def elect_leader(self, max_rounds: int = 50) -> RaftNode:
        """Simulate election until a leader emerges.

        Args:
            max_rounds: Maximum ticks to attempt.

        Returns:
            The elected leader node.

        Raises:
            RuntimeError: If no leader emerges within max_rounds.
        """
        for _ in range(max_rounds):
            for node in self.nodes.values():
                event = node.tick(self._cluster_size)
                if event == "election_started":
                    self._run_election(node)

            if self.leader is not None:
                return self.leader

        raise RuntimeError(f"No leader elected after {max_rounds} rounds")

    def propose(self, command: Any) -> LogEntry:
        """Propose a command through the leader and replicate.

        Args:
            command: Application payload.

        Returns:
            The committed LogEntry.

        Raises:
            RuntimeError: If there is no leader.
        """
        leader = self.leader
        if leader is None:
            raise RuntimeError("No leader available")

        entry = leader.propose(command)
        self._replicate(leader, entry)
        return entry

    def get_committed_log(self) -> list[LogEntry]:
        """Return committed entries from the leader."""
        leader = self.leader
        if leader is None:
            return []
        return leader.get_committed_entries()

    # -- internal ------------------------------------------------------------

    def _run_election(self, candidate: RaftNode) -> None:
        """Send RequestVote RPCs from *candidate* to all other nodes."""
        for nid, node in self.nodes.items():
            if nid == candidate.node_id:
                continue
            response = node.request_vote(
                term=candidate.current_term,
                candidate_id=candidate.node_id,
                last_log_term=candidate.last_log_term,
                last_log_index=candidate.last_log_index,
            )
            result = candidate.receive_vote(response, self._cluster_size, nid)
            if result == "became_leader":
                # Step down other candidates
                for other_id, other_node in self.nodes.items():
                    if (
                        other_id != candidate.node_id
                        and other_node.state == RaftState.CANDIDATE
                    ):
                        other_node._step_down(candidate.current_term)
                return

    def _replicate(self, leader: RaftNode, entry: LogEntry) -> None:
        """Replicate *entry* from *leader* to followers and commit if majority."""
        match_count = 1  # leader counts

        for nid, node in self.nodes.items():
            if nid == leader.node_id:
                continue
            prev_log_index = entry.index - 1
            prev_log_term = (
                leader.log[prev_log_index - 1].term if prev_log_index > 0 else 0
            )

            response = node.append_entries(
                term=leader.current_term,
                leader_id=leader.node_id,
                entries=[entry],
                prev_log_index=prev_log_index,
                prev_log_term=prev_log_term,
                leader_commit=leader.commit_index,
            )
            if response.success:
                match_count += 1

        # Commit if majority
        majority = self._cluster_size // 2 + 1
        if match_count >= majority:
            leader.commit_index = entry.index
            entry.committed = True
            # Notify followers of new commit
            for nid, node in self.nodes.items():
                if nid != leader.node_id:
                    node.append_entries(
                        term=leader.current_term,
                        leader_id=leader.node_id,
                        entries=[],
                        prev_log_index=len(node.log),
                        prev_log_term=node.log[-1].term if node.log else 0,
                        leader_commit=leader.commit_index,
                    )

    def to_dict(self) -> dict[str, Any]:
        """Serialize cluster state."""
        return {
            "cluster_size": self._cluster_size,
            "leader": self.leader.node_id if self.leader else None,
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
        }


__all__ = [
    "AppendResponse",
    "LogEntry",
    "RaftCluster",
    "RaftNode",
    "RaftState",
    "VoteResponse",
]
