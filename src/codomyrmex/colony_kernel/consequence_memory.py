"""Consequence memory — SQLite-backed record of proposal outcomes and agent trust profiles.

ConsequenceMemory is the colony's long-term accountability store. Every
ActionProposal outcome is written here; the resulting trust scores and
per-agent profiles govern what agents are permitted to propose next.

Canonical standalone implementation with both kernel API (get_profile,
save_profile, record returns record, recent_consequences, role_distribution)
and standalone query API (history, trust_score, pattern_success_rate, etc.).

Supports db_path=None (pure in-memory list, no SQLite) and db_path=":memory:"
or a file path (SQLite-backed).
"""

from __future__ import annotations

import json
import sqlite3
import time
from collections import defaultdict
from dataclasses import asdict
from typing import Any, Self

from codomyrmex.colony_kernel.models import (
    _TRUST_DELTA_FAIL,
    _TRUST_DELTA_HUMAN_WEIGHT,
    _TRUST_DELTA_PASS,
    _TRUST_DELTA_REPAIR,
    ActionProposal,
    AgentRole,
    AgentTrustProfile,
    ConsequenceRecord,
    ResourceCost,
    compute_trust_delta,
)

# ---------------------------------------------------------------------------
# Internal helpers / constants
# ---------------------------------------------------------------------------

_TRUST_BASE: float = 0.5

# Trust delta constants — imported from models.py (single source of truth).
_DELTA_TESTS_PASSED: float = _TRUST_DELTA_PASS
_DELTA_FEEDBACK_ACCEPTED: float = _TRUST_DELTA_HUMAN_WEIGHT
_DELTA_REPAIR_NEEDED: float = _TRUST_DELTA_REPAIR
_DELTA_FEEDBACK_REJECTED: float = _TRUST_DELTA_FAIL

_FEEDBACK_ACCEPTED_THRESHOLD: float = 0.5
_FEEDBACK_REJECTED_THRESHOLD: float = -0.5

_TRUST_WINDOW: int = 50  # last N records used in trust computation
_CONSEQUENCE_HISTORY_MAX = 200  # rows kept per agent in SQLite history table


def _delta_for_record(record: ConsequenceRecord) -> float:
    """Compute the incremental trust delta for a single consequence record.

    Formula (additive, not multiplicative):
      +_DELTA_TESTS_PASSED      if tests_passed is True
      +_DELTA_REPAIR_NEEDED     if repair_needed is True
      +_DELTA_FEEDBACK_ACCEPTED if human_feedback >= 0.5
      +_DELTA_FEEDBACK_REJECTED if human_feedback <= -0.5
      0.0                       for feedback in (-0.5, 0.5)

    Note: tests_passed=False with no repair and no feedback contributes 0.0
    (no explicit fail penalty in this formula — repair_needed captures that).
    """
    delta: float = 0.0
    if record.tests_passed:
        delta += _DELTA_TESTS_PASSED
    if record.repair_needed:
        delta += _DELTA_REPAIR_NEEDED
    if record.human_feedback >= 0.5:
        delta += _DELTA_FEEDBACK_ACCEPTED
    elif record.human_feedback <= -0.5:
        delta += _DELTA_FEEDBACK_REJECTED
    return delta


# ---------------------------------------------------------------------------
# Serialisation helpers — ActionProposal / ResourceCost <-> JSON
# ---------------------------------------------------------------------------


def _proposal_to_json(proposal: ActionProposal) -> str:
    d = asdict(proposal)
    return json.dumps(d)


def _proposal_from_json(raw: str) -> ActionProposal:
    d: dict[str, Any] = json.loads(raw)
    budget_raw: dict[str, Any] = d.pop("budget_estimate", {})
    budget = ResourceCost(**budget_raw)
    return ActionProposal(budget_estimate=budget, **d)


def _record_to_row(record: ConsequenceRecord) -> tuple[Any, ...]:
    return (
        record.consequence_id,
        record.proposal.agent_id,
        record.proposal.action_type,
        _proposal_to_json(record.proposal),
        record.action_taken,
        record.actual_outcome,
        int(record.tests_passed),
        record.human_feedback,
        int(record.repair_needed),
        record.trust_delta,
        record.recorded_at,
    )


def _row_to_record(row: tuple[Any, ...]) -> ConsequenceRecord:
    (
        consequence_id,
        _agent_id,
        _action_type,
        proposal_json,
        action_taken,
        actual_outcome,
        tests_passed,
        human_feedback,
        repair_needed,
        trust_delta,
        recorded_at,
    ) = row
    proposal = _proposal_from_json(proposal_json)
    return ConsequenceRecord(
        consequence_id=consequence_id,
        proposal=proposal,
        action_taken=action_taken,
        actual_outcome=actual_outcome,
        tests_passed=bool(tests_passed),
        human_feedback=float(human_feedback),
        repair_needed=bool(repair_needed),
        trust_delta=float(trust_delta),
        recorded_at=float(recorded_at),
    )


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS consequences (
    consequence_id  TEXT PRIMARY KEY,
    agent_id        TEXT NOT NULL,
    action_type     TEXT NOT NULL,
    proposal_json   TEXT NOT NULL,
    action_taken    TEXT NOT NULL,
    actual_outcome  TEXT NOT NULL,
    tests_passed    INTEGER NOT NULL,
    human_feedback  REAL NOT NULL,
    repair_needed   INTEGER NOT NULL,
    trust_delta     REAL NOT NULL,
    recorded_at     REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_profiles (
    agent_id           TEXT PRIMARY KEY,
    role               TEXT NOT NULL,
    trust_score        REAL NOT NULL,
    total_proposals    INTEGER NOT NULL,
    accepted_proposals INTEGER NOT NULL,
    last_updated       REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS consequence_history (
    agent_id       TEXT NOT NULL,
    consequence_id TEXT NOT NULL,
    seq            INTEGER NOT NULL,
    PRIMARY KEY (agent_id, consequence_id)
);
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class ConsequenceMemory:
    """Persistent consequence log backed by SQLite (or in-memory list).

    Provides both:
    - Kernel API: get_profile(), save_profile(), record() returns record,
      recent_consequences(), role_distribution()
    - Standalone query API: history(), trust_score(), pattern_success_rate(),
      successful_patterns(), best_performing_agents(), worst_performing_agents()

    Storage modes:
    - db_path=None: pure in-memory list (no SQLite; for unit tests)
    - db_path=":memory:" or file path: SQLite-backed (WAL mode)
    """

    def __init__(self, db_path: str | None = None) -> None:
        """Open (or create) the consequence store.

        Args:
            db_path: Pass None for pure in-memory list mode, ":memory:" for
                SQLite in-memory, or a file path for persistent SQLite.
        """
        self._db_path = db_path
        self._in_memory: list[ConsequenceRecord] | None = None

        if db_path is None:
            # Pure in-memory fallback — no SQLite.
            self._in_memory = []
        else:
            self._conn = sqlite3.connect(db_path, check_same_thread=False)
            self._conn.row_factory = None
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.executescript(_CREATE_SCHEMA)
            self._conn.commit()

    # ------------------------------------------------------------------
    # Internal helpers (SQLite profile management)
    # ------------------------------------------------------------------

    def _load_profile(self, agent_id: str) -> AgentTrustProfile:
        if self._in_memory is not None:
            # Compute trust from in-memory records
            records = [r for r in self._in_memory if r.proposal.agent_id == agent_id]
            score = _TRUST_BASE
            for rec in records[-_TRUST_WINDOW:]:
                score += _delta_for_record(rec)
            trust = max(0.0, min(1.0, score))
            total = len(records)
            accepted = sum(
                1 for r in records if r.tests_passed and not r.repair_needed
            )
            return AgentTrustProfile(
                agent_id=agent_id,
                trust_score=trust,
                total_proposals=total,
                accepted_proposals=accepted,
                consequence_history=[r.consequence_id for r in records[-200:]],
            )

        row = self._conn.execute(
            "SELECT role, trust_score, total_proposals, accepted_proposals, last_updated "
            "FROM agent_profiles WHERE agent_id = ?",
            (agent_id,),
        ).fetchone()
        if row is None:
            return AgentTrustProfile(agent_id=agent_id)
        role, trust, total, accepted, last_updated = row
        history_rows = self._conn.execute(
            "SELECT consequence_id FROM consequence_history "
            "WHERE agent_id = ? ORDER BY seq ASC",
            (agent_id,),
        ).fetchall()
        history = [r[0] for r in history_rows]
        return AgentTrustProfile(
            agent_id=agent_id,
            role=AgentRole(role),
            trust_score=trust,
            total_proposals=total,
            accepted_proposals=accepted,
            consequence_history=history,
            last_updated=last_updated,
        )

    def _save_profile_internal(self, profile: AgentTrustProfile) -> None:
        if self._in_memory is not None:
            return  # in-memory mode doesn't persist profiles
        self._conn.execute(
            """
            INSERT INTO agent_profiles
                (agent_id, role, trust_score, total_proposals, accepted_proposals, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(agent_id) DO UPDATE SET
                role               = excluded.role,
                trust_score        = excluded.trust_score,
                total_proposals    = excluded.total_proposals,
                accepted_proposals = excluded.accepted_proposals,
                last_updated       = excluded.last_updated
            """,
            (
                profile.agent_id,
                profile.role.value,
                profile.trust_score,
                profile.total_proposals,
                profile.accepted_proposals,
                profile.last_updated,
            ),
        )

    def _append_history(self, agent_id: str, consequence_id: str) -> None:
        if self._in_memory is not None:
            return
        row = self._conn.execute(
            "SELECT MAX(seq) FROM consequence_history WHERE agent_id = ?",
            (agent_id,),
        ).fetchone()
        next_seq = (row[0] or 0) + 1
        self._conn.execute(
            "INSERT OR IGNORE INTO consequence_history (agent_id, consequence_id, seq) "
            "VALUES (?, ?, ?)",
            (agent_id, consequence_id, next_seq),
        )
        self._conn.execute(
            """
            DELETE FROM consequence_history
            WHERE agent_id = ? AND seq <= (
                SELECT MAX(seq) - ? FROM consequence_history WHERE agent_id = ?
            )
            """,
            (agent_id, _CONSEQUENCE_HISTORY_MAX, agent_id),
        )

    # ------------------------------------------------------------------
    # Kernel API
    # ------------------------------------------------------------------

    def save_profile(self, profile: AgentTrustProfile) -> None:
        """Persist an updated AgentTrustProfile (e.g. after role promotion)."""
        if self._in_memory is not None:
            return  # in-memory mode: no-op (profiles computed from records)
        with self._conn:
            self._save_profile_internal(profile)

    def get_profile(self, agent_id: str) -> AgentTrustProfile:
        """Return the current trust profile; creates a SANDBOX default if absent."""
        return self._load_profile(agent_id)

    def record(self, rec: ConsequenceRecord) -> ConsequenceRecord:
        """Persist *rec*, compute trust_delta if zero, update profile.

        Uses ``compute_trust_delta`` (the canonical model formula) for the
        persistent trust update, which applies a negative delta for
        tests_passed=False even without repair_needed.  The exported
        ``_delta_for_record`` function uses the standalone formula
        (neutral feedback = 0 delta; no implicit fail penalty).

        Returns the (possibly mutated) record with trust_delta populated.
        """
        if rec.trust_delta == 0.0:
            object.__setattr__(rec, "trust_delta", compute_trust_delta(rec))

        if self._in_memory is not None:
            self._in_memory.append(rec)
            return rec

        agent_id = rec.proposal.agent_id
        profile = self._load_profile(agent_id)
        profile.total_proposals += 1
        if rec.tests_passed and not rec.repair_needed:
            profile.accepted_proposals += 1
        profile.apply_delta(rec.trust_delta)

        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO consequences
                    (consequence_id, agent_id, action_type, proposal_json,
                     action_taken, actual_outcome, tests_passed, human_feedback,
                     repair_needed, trust_delta, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                _record_to_row(rec),
            )
            self._save_profile_internal(profile)
            self._append_history(agent_id, rec.consequence_id)

        return rec

    def recent_consequences(self, limit: int = 10) -> list[dict[str, Any]]:
        """Return the *limit* most recent consequence rows as plain dicts."""
        if self._in_memory is not None:
            sorted_records = sorted(
                self._in_memory, key=lambda r: r.recorded_at, reverse=True
            )[:limit]
            return [
                {
                    "consequence_id": r.consequence_id,
                    "agent_id": r.proposal.agent_id,
                    "action_type": r.proposal.action_type,
                    "target": r.proposal.target,
                    "tests_passed": r.tests_passed,
                    "trust_delta": r.trust_delta,
                    "recorded_at": r.recorded_at,
                }
                for r in sorted_records
            ]

        rows = self._conn.execute(
            "SELECT consequence_id, agent_id, action_type, "
            "actual_outcome AS target, tests_passed, "
            "trust_delta, recorded_at FROM consequences "
            "ORDER BY recorded_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        # Note: SQLite schema stores target in proposal_json; use agent_id as fallback
        # Requery with proper fields
        rows2 = self._conn.execute(
            "SELECT consequence_id, agent_id, action_type, "
            "proposal_json, tests_passed, trust_delta, recorded_at "
            "FROM consequences ORDER BY recorded_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        result = []
        for r in rows2:
            proposal_data = json.loads(r[3])
            result.append({
                "consequence_id": r[0],
                "agent_id": r[1],
                "action_type": r[2],
                "target": proposal_data.get("target", ""),
                "tests_passed": bool(r[4]),
                "trust_delta": r[5],
                "recorded_at": r[6],
            })
        return result

    def recent_failures(self, agent_id: str, window: int = 10) -> int:
        """Return the count of failure records in the most recent *window* records for *agent_id*.

        A record is a failure when ``tests_passed`` is ``False`` or
        ``repair_needed`` is ``True``.  Only the most recent *window* records
        are examined so that old failures do not permanently penalise a
        reformed agent.

        Args:
            agent_id: The agent whose recent history is inspected.
            window: How many of the most-recent records to scan (default 10).

        Returns:
            Count of failure records in the examined window (0 when the agent
            has no history).
        """
        records = self._fetch_agent_records(agent_id, limit=window)
        return sum(
            1 for r in records if not r.tests_passed or r.repair_needed
        )

    def role_distribution(self) -> dict[str, int]:
        """Return a count of agents per role."""
        if self._in_memory is not None:
            return {}  # no role tracking in pure in-memory mode
        rows = self._conn.execute(
            "SELECT role, COUNT(*) FROM agent_profiles GROUP BY role"
        ).fetchall()
        return {r[0]: r[1] for r in rows}

    # ------------------------------------------------------------------
    # Standalone query API
    # ------------------------------------------------------------------

    def trust_score(self, agent_id: str) -> float:
        """Compute the trust score for an agent from their last 50 records."""
        records = self._fetch_agent_records(agent_id, limit=_TRUST_WINDOW)
        score = _TRUST_BASE
        for rec in records:
            score += _delta_for_record(rec)
        return max(0.0, min(1.0, score))

    def history(self, agent_id: str, limit: int = 20) -> list[ConsequenceRecord]:
        """Return the most recent consequence records for an agent."""
        return self._fetch_agent_records(agent_id, limit=limit)

    def successful_patterns(self, agent_id: str) -> list[str]:
        """Return action types that succeeded most often for an agent."""
        records = self._fetch_all_agent_records(agent_id)
        counts: dict[str, int] = defaultdict(int)
        for rec in records:
            if rec.tests_passed and not rec.repair_needed:
                counts[rec.proposal.action_type] += 1
        if not counts:
            return []
        return sorted(counts.keys(), key=lambda k: (-counts[k], k))

    def worst_performing_agents(self, k: int = 5) -> list[tuple[str, float]]:
        """Return the k agents with the lowest trust scores."""
        agent_ids = self._all_agent_ids()
        scored = [(aid, self.trust_score(aid)) for aid in agent_ids]
        scored.sort(key=lambda t: (t[1], t[0]))
        return scored[:k]

    def best_performing_agents(self, k: int = 5) -> list[tuple[str, float]]:
        """Return the k agents with the highest trust scores."""
        agent_ids = self._all_agent_ids()
        scored = [(aid, self.trust_score(aid)) for aid in agent_ids]
        scored.sort(key=lambda t: (-t[1], t[0]))
        return scored[:k]

    def pattern_success_rate(self, action_type: str) -> float:
        """Return the fraction of records for an action type that were successful."""
        records = self._fetch_action_type_records(action_type)
        if not records:
            return 0.0
        successes = sum(1 for r in records if r.tests_passed and not r.repair_needed)
        return successes / len(records)

    # ------------------------------------------------------------------
    # Private — storage layer abstraction
    # ------------------------------------------------------------------

    def _fetch_agent_records(self, agent_id: str, limit: int) -> list[ConsequenceRecord]:
        if self._in_memory is not None:
            filtered = [r for r in self._in_memory if r.proposal.agent_id == agent_id]
            filtered.sort(key=lambda r: r.recorded_at, reverse=True)
            return filtered[:limit]
        cursor = self._conn.execute(
            """
            SELECT consequence_id, agent_id, action_type, proposal_json,
                   action_taken, actual_outcome, tests_passed, human_feedback,
                   repair_needed, trust_delta, recorded_at
            FROM consequences
            WHERE agent_id = ?
            ORDER BY recorded_at DESC
            LIMIT ?
            """,
            (agent_id, limit),
        )
        return [_row_to_record(row) for row in cursor.fetchall()]

    def _fetch_all_agent_records(self, agent_id: str) -> list[ConsequenceRecord]:
        if self._in_memory is not None:
            return [r for r in self._in_memory if r.proposal.agent_id == agent_id]
        cursor = self._conn.execute(
            """
            SELECT consequence_id, agent_id, action_type, proposal_json,
                   action_taken, actual_outcome, tests_passed, human_feedback,
                   repair_needed, trust_delta, recorded_at
            FROM consequences WHERE agent_id = ? ORDER BY recorded_at ASC
            """,
            (agent_id,),
        )
        return [_row_to_record(row) for row in cursor.fetchall()]

    def _fetch_action_type_records(self, action_type: str) -> list[ConsequenceRecord]:
        if self._in_memory is not None:
            return [r for r in self._in_memory if r.proposal.action_type == action_type]
        cursor = self._conn.execute(
            """
            SELECT consequence_id, agent_id, action_type, proposal_json,
                   action_taken, actual_outcome, tests_passed, human_feedback,
                   repair_needed, trust_delta, recorded_at
            FROM consequences WHERE action_type = ? ORDER BY recorded_at ASC
            """,
            (action_type,),
        )
        return [_row_to_record(row) for row in cursor.fetchall()]

    def _all_agent_ids(self) -> list[str]:
        if self._in_memory is not None:
            seen: dict[str, None] = {}
            for r in self._in_memory:
                seen[r.proposal.agent_id] = None
            return list(seen.keys())
        cursor = self._conn.execute(
            "SELECT DISTINCT agent_id FROM consequences ORDER BY agent_id"
        )
        return [row[0] for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying SQLite connection, if open."""
        if self._in_memory is None:
            self._conn.close()

    def __del__(self) -> None:
        try:
            if self._in_memory is None:
                self._conn.close()
        except Exception:
            pass

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


__all__ = [
    "_DELTA_FEEDBACK_ACCEPTED",
    "_DELTA_FEEDBACK_REJECTED",
    "_DELTA_REPAIR_NEEDED",
    "_DELTA_TESTS_PASSED",
    "_TRUST_BASE",
    "ConsequenceMemory",
    "_delta_for_record",
]
