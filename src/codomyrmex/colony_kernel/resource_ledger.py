"""Resource ledger — tracks colony action budgets and enforces spending caps.

This module imports only models.py and stdlib.

No external dependencies beyond stdlib.
"""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.colony_kernel.models import ResourceCost

# ---------------------------------------------------------------------------
# Budget definition
# ---------------------------------------------------------------------------


@dataclass
class ResourceBudget:
    """Colony-wide spending caps applied by ResourceLedger.

    All fields correspond to dimensions of ResourceCost.
    ``max_risk_level``, ``max_merge_risk``, and ``max_security_exposure`` are
    cumulative caps (0.0–1.0); because ResourceCost clamps those fields the
    ledger compares the running sum against the cap.

    Set a cap to ``float("inf")`` to disable enforcement for that dimension.
    ``period_seconds`` controls when the ledger auto-resets (0 = never reset).

    Alias fields accepted at construction time:
      ``max_llm_calls_per_hour``  → stored as ``max_llm_calls``
      ``total_doc_debt_allowed``  → stored as ``max_doc_debt``
    """

    max_llm_calls: int = 500
    max_runtime_seconds: float = 3600.0
    max_risk_level: float = 0.8
    max_human_attention_minutes: float = 120.0
    max_merge_risk: float = 0.7
    max_doc_debt: float = 1000.0
    max_security_exposure: float = 0.5
    period_seconds: float = 86400.0  # 24 hours
    # Alias keyword arguments — resolved in __post_init__; not stored as fields.
    max_llm_calls_per_hour: int | None = field(default=None, repr=False)
    total_doc_debt_allowed: float | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.max_llm_calls_per_hour is not None:
            self.max_llm_calls = self.max_llm_calls_per_hour
        if self.total_doc_debt_allowed is not None:
            self.max_doc_debt = self.total_doc_debt_allowed


# ---------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------


@dataclass
class ResourceLedger:
    """Colony action budget tracker.

    Maintains a running cumulative ``ResourceCost`` since the last reset and
    a full chronological history of (agent_id, cost, timestamp) triples.

    Thread-safety: this class is not thread-safe. External locking is the
    caller's responsibility in concurrent environments.

    Args:
        budget: The spending cap applied by :meth:`can_afford`.
    """

    budget: ResourceBudget = field(default_factory=ResourceBudget)
    db_path: str | None = None

    # Internal state — not part of the public interface.
    _accumulated: ResourceCost = field(
        default_factory=ResourceCost, init=False, repr=False
    )
    _history: list[tuple[str, ResourceCost, float]] = field(
        default_factory=list, init=False, repr=False
    )
    _period_start: float = field(default_factory=time.time, init=False, repr=False)
    _conn: sqlite3.Connection | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Open the optional durable backend and restore its current period."""
        if self.db_path is None:
            return
        self._conn = sqlite3.connect(
            self.db_path, check_same_thread=False, timeout=10.0
        )
        self._conn.execute("PRAGMA busy_timeout=10000")
        try:
            self._conn.execute("PRAGMA journal_mode=WAL")
        except sqlite3.OperationalError as exc:
            if "locked" not in str(exc).lower():
                raise
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS resource_usage (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                llm_calls INTEGER NOT NULL,
                runtime_seconds REAL NOT NULL,
                risk_level REAL NOT NULL,
                human_attention_minutes REAL NOT NULL,
                merge_risk REAL NOT NULL,
                doc_debt REAL NOT NULL,
                security_exposure REAL NOT NULL,
                period_start REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS resource_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                llm_calls INTEGER NOT NULL,
                runtime_seconds REAL NOT NULL,
                risk_level REAL NOT NULL,
                human_attention_minutes REAL NOT NULL,
                merge_risk REAL NOT NULL,
                doc_debt REAL NOT NULL,
                security_exposure REAL NOT NULL,
                recorded_at REAL NOT NULL
            );
            """
        )
        self._conn.execute(
            "INSERT OR IGNORE INTO resource_usage VALUES (1, 0, 0, 0, 0, 0, 0, 0, ?)",
            (self._period_start,),
        )
        self._conn.commit()
        self._load_persistent_state()

    def _load_persistent_state(self) -> None:
        if self._conn is None:
            return
        row = self._conn.execute(
            "SELECT llm_calls, runtime_seconds, risk_level, human_attention_minutes, "
            "merge_risk, doc_debt, security_exposure, period_start FROM resource_usage "
            "WHERE singleton = 1"
        ).fetchone()
        if row is not None:
            self._accumulated = ResourceCost(*row[:7])
            self._period_start = float(row[7])
        rows = self._conn.execute(
            "SELECT agent_id, llm_calls, runtime_seconds, risk_level, "
            "human_attention_minutes, merge_risk, doc_debt, security_exposure, "
            "recorded_at FROM resource_history ORDER BY id"
        ).fetchall()
        self._history = [
            (str(row[0]), ResourceCost(*row[1:8]), float(row[8])) for row in rows
        ]

    def _persist_state(self) -> None:
        if self._conn is None:
            return
        acc = self._accumulated
        self._conn.execute(
            "UPDATE resource_usage SET llm_calls=?, runtime_seconds=?, risk_level=?, "
            "human_attention_minutes=?, merge_risk=?, doc_debt=?, "
            "security_exposure=?, period_start=? WHERE singleton=1",
            (
                acc.llm_calls,
                acc.runtime_seconds,
                acc.risk_level,
                acc.human_attention_minutes,
                acc.merge_risk,
                acc.doc_debt,
                acc.security_exposure,
                self._period_start,
            ),
        )

    # ---------------------------------------------------------------------------
    # Period reset
    # ---------------------------------------------------------------------------

    def _maybe_reset(self) -> None:
        """Reset accumulated cost if the budget period has elapsed."""
        if self.budget.period_seconds <= 0:
            return
        if time.time() - self._period_start >= self.budget.period_seconds:
            self._load_persistent_state()
            self._accumulated = ResourceCost()
            self._period_start = time.time()
            if self._conn is not None:
                with self._conn:
                    self._persist_state()

    def reset_period(self) -> None:
        """Manually reset the period accumulator."""
        self._load_persistent_state()
        self._accumulated = ResourceCost()
        self._period_start = time.time()
        if self._conn is not None:
            with self._conn:
                self._persist_state()

    # ---------------------------------------------------------------------------
    # Mutation
    # ---------------------------------------------------------------------------

    def record_cost(self, cost: ResourceCost, agent_id: str) -> None:
        """Record an actual cost incurred by ``agent_id``.

        Updates the running accumulated total and appends to history.
        Does NOT enforce budget — call :meth:`can_afford` before executing
        to enforce caps.

        Args:
            cost: The cost to record.
            agent_id: Identifier of the agent that incurred the cost.
        """
        if not agent_id:
            raise ValueError("agent_id must be non-empty")
        self._load_persistent_state()
        self._maybe_reset()
        self._accumulated = self._accumulated + cost
        recorded_at = time.time()
        self._history.append((agent_id, cost, recorded_at))
        if self._conn is not None:
            with self._conn:
                self._persist_state()
                self._conn.execute(
                    "INSERT INTO resource_history "
                    "(agent_id, llm_calls, runtime_seconds, risk_level, "
                    "human_attention_minutes, merge_risk, doc_debt, security_exposure, recorded_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (agent_id, cost.llm_calls, cost.runtime_seconds, cost.risk_level,
                     cost.human_attention_minutes, cost.merge_risk, cost.doc_debt,
                     cost.security_exposure, recorded_at),
                )

    def consume(self, cost: ResourceCost) -> None:
        """Record actual consumption after an action executes.

        This is the canonical method called by ColonyKernel.record_outcome.
        Does not require an agent_id — use record_cost for per-agent tracking.
        """
        self._load_persistent_state()
        self._maybe_reset()
        self._accumulated = self._accumulated + cost
        if self._conn is not None:
            with self._conn:
                self._persist_state()

    def reset(self, period: str = "hourly") -> None:
        """Reset the accumulated usage counter.

        History is preserved across resets; only the running total is cleared.

        Args:
            period: Human-readable label describing the reset period (e.g.
                ``"hourly"``, ``"daily"``).  Not used computationally — stored
                for observability.  Defaults to ``"hourly"``.
        """
        self.reset_period()

    # ---------------------------------------------------------------------------
    # Queries
    # ---------------------------------------------------------------------------

    def check_budget(self, estimate: ResourceCost) -> tuple[bool, str]:
        """Return (approved, reason).

        Approved when accumulating *estimate* on top of current usage would
        not breach any budget dimension. The accumulator is NOT modified here;
        call ``consume`` after the action executes.
        """
        self._load_persistent_state()
        self._maybe_reset()
        ok, reason = self.can_afford(estimate)
        if ok:
            return (True, "within budget")
        return (False, reason or "budget exceeded")

    def can_afford(self, cost: ResourceCost) -> tuple[bool, str | None]:
        """Check whether adding ``cost`` to the current accumulated total
        would remain within every budget cap.

        Returns a ``(True, None)`` pair if affordable, or
        ``(False, reason_string)`` naming the first violated dimension.

        Args:
            cost: The prospective cost to check.
        """
        self._load_persistent_state()
        self._maybe_reset()
        projected: ResourceCost = self._accumulated + cost

        if projected.llm_calls > self.budget.max_llm_calls:
            return (
                False,
                f"llm_calls budget exceeded: {projected.llm_calls} > "
                f"{self.budget.max_llm_calls}",
            )

        if projected.runtime_seconds > self.budget.max_runtime_seconds:
            return (
                False,
                f"runtime_seconds budget exceeded: {projected.runtime_seconds:.2f}s > "
                f"{self.budget.max_runtime_seconds:.2f}s",
            )

        if projected.risk_level > self.budget.max_risk_level:
            return (
                False,
                f"risk_level budget exceeded: {projected.risk_level:.3f} > "
                f"{self.budget.max_risk_level:.3f}",
            )

        if projected.human_attention_minutes > self.budget.max_human_attention_minutes:
            return (
                False,
                f"human_attention_minutes budget exceeded: "
                f"{projected.human_attention_minutes:.2f} > "
                f"{self.budget.max_human_attention_minutes:.2f}",
            )

        if projected.merge_risk > self.budget.max_merge_risk:
            return (
                False,
                f"merge_risk budget exceeded: {projected.merge_risk:.3f} > "
                f"{self.budget.max_merge_risk:.3f}",
            )

        if projected.doc_debt > self.budget.max_doc_debt:
            return (
                False,
                f"doc_debt budget exceeded: {projected.doc_debt:.2f} > "
                f"{self.budget.max_doc_debt:.2f}",
            )

        if projected.security_exposure > self.budget.max_security_exposure:
            return (
                False,
                f"security_exposure budget exceeded: {projected.security_exposure:.3f} > "
                f"{self.budget.max_security_exposure:.3f}",
            )

        return (True, None)

    def check_and_consume(
        self,
        cost: ResourceCost,
        agent_id: str = "",
    ) -> tuple[bool, str]:
        """Atomically check budget and consume if affordable.

        This is the safe combined alternative to calling ``check_budget``
        followed by ``consume`` separately, which has a TOCTOU gap in
        concurrent environments.

        If affordable, the cost is consumed immediately and the method returns
        ``(True, "consumed")``.  If not affordable, nothing is consumed and
        the method returns ``(False, reason_string)``.

        Note: This class is not thread-safe — if concurrent access is required,
        wrap the ledger with a ``threading.Lock`` (see :class:`ThreadSafeResourceLedger`)
        or use external locking around this call.

        Args:
            cost: The cost to check and potentially consume.
            agent_id: Optional agent identifier for per-agent history tracking.
                When non-empty, records the cost via ``record_cost`` rather than
                the anonymous ``consume`` path so the agent's history is updated.

        Returns:
            ``(True, "consumed")`` if within budget (cost is consumed),
            ``(False, reason)`` if budget would be exceeded (not consumed).
        """
        if self._conn is not None:
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                self._load_persistent_state()
                self._maybe_reset()
                ok, reason = self.can_afford(cost)
                if not ok:
                    self._conn.rollback()
                    return (False, reason or "budget exceeded")
                self._accumulated = self._accumulated + cost
                if agent_id:
                    recorded_at = time.time()
                    self._history.append((agent_id, cost, recorded_at))
                    self._conn.execute(
                        "INSERT INTO resource_history "
                        "(agent_id, llm_calls, runtime_seconds, risk_level, "
                        "human_attention_minutes, merge_risk, doc_debt, security_exposure, recorded_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (agent_id, cost.llm_calls, cost.runtime_seconds, cost.risk_level,
                         cost.human_attention_minutes, cost.merge_risk, cost.doc_debt,
                         cost.security_exposure, recorded_at),
                    )
                self._persist_state()
                self._conn.commit()
                return (True, "consumed")
            except Exception:
                self._conn.rollback()
                raise

        self._maybe_reset()
        ok, reason = self.can_afford(cost)
        if not ok:
            return (False, reason or "budget exceeded")

        if agent_id:
            self.record_cost(cost, agent_id)
        else:
            self.consume(cost)
        return (True, "consumed")

    def current_usage(self) -> ResourceCost:
        """Return the accumulated cost since the last :meth:`reset`.

        Returns a copy; mutating the returned object does not affect the ledger.
        """
        self._load_persistent_state()
        self._maybe_reset()
        return ResourceCost(
            llm_calls=self._accumulated.llm_calls,
            runtime_seconds=self._accumulated.runtime_seconds,
            risk_level=self._accumulated.risk_level,
            human_attention_minutes=self._accumulated.human_attention_minutes,
            merge_risk=self._accumulated.merge_risk,
            doc_debt=self._accumulated.doc_debt,
            security_exposure=self._accumulated.security_exposure,
        )

    def usage_summary(self) -> dict[str, Any]:
        """Return current period consumption vs budget as a plain dict."""
        self._load_persistent_state()
        self._maybe_reset()
        acc = self._accumulated
        b = self.budget
        return {
            "llm_calls": {"used": acc.llm_calls, "max": b.max_llm_calls},
            "runtime_seconds": {
                "used": round(acc.runtime_seconds, 3),
                "max": b.max_runtime_seconds,
            },
            "risk_level": {
                "used": round(acc.risk_level, 3),
                "max": b.max_risk_level,
            },
            "human_attention_minutes": {
                "used": round(acc.human_attention_minutes, 3),
                "max": b.max_human_attention_minutes,
            },
            "merge_risk": {"used": round(acc.merge_risk, 3), "max": b.max_merge_risk},
            "doc_debt": {"used": round(acc.doc_debt, 3), "max": b.max_doc_debt},
            "security_exposure": {
                "used": round(acc.security_exposure, 3),
                "max": b.max_security_exposure,
            },
            "period_start": self._period_start,
        }

    def history(self) -> list[tuple[str, ResourceCost, float]]:
        """Return the full chronological cost history.

        Each entry is ``(agent_id, cost, unix_timestamp)``.  History spans
        across resets — it is never cleared.

        Returns:
            A shallow copy of the internal history list.
        """
        self._load_persistent_state()
        return list(self._history)

    def agent_spend(self, agent_id: str) -> ResourceCost:
        """Return the total spend accumulated by a single agent across all history.

        Args:
            agent_id: The agent whose total spend to compute.

        Returns:
            Summed ``ResourceCost`` for that agent; zero-cost if unknown.
        """
        self._load_persistent_state()
        total = ResourceCost()
        for aid, cost, _ in self._history:
            if aid == agent_id:
                total = total + cost
        return total

    def most_expensive_agents(self, k: int = 5) -> list[tuple[str, ResourceCost]]:
        """Return the top-``k`` spenders ranked by LLM calls (primary), then
        by human attention minutes (secondary).

        Args:
            k: Number of agents to return.

        Returns:
            A list of ``(agent_id, total_cost)`` pairs, most expensive first.
        """
        self._load_persistent_state()
        per_agent: dict[str, ResourceCost] = {}
        for aid, cost, _ in self._history:
            if aid in per_agent:
                per_agent[aid] = per_agent[aid] + cost
            else:
                per_agent[aid] = cost

        ranked = sorted(
            per_agent.items(),
            key=lambda item: (
                -item[1].llm_calls,
                -item[1].human_attention_minutes,
            ),
        )
        return ranked[:k]

    def close(self) -> None:
        """Close the durable backend, if configured."""

        if self._conn is not None:
            self._conn.close()


# ---------------------------------------------------------------------------
# Thread-safe wrapper
# ---------------------------------------------------------------------------


class ThreadSafeResourceLedger:
    """Thread-safe wrapper around ResourceLedger using a ``threading.Lock``.

    All public methods are delegated to the underlying ``ResourceLedger`` with
    the lock held.  Use this wrapper when multiple threads share a ledger
    (e.g. a multi-threaded web server calling ``check_and_consume`` concurrently).

    Example::

        from threading import Lock
        ledger = ThreadSafeResourceLedger(ResourceLedger(budget=budget))
        ok, reason = ledger.check_and_consume(cost, agent_id="worker-1")

    Note: The lock is **not** re-entrant.  Do not call one public method from
    within another public method of the same instance or a deadlock will occur.
    """

    def __init__(self, ledger: ResourceLedger) -> None:
        import threading
        self._ledger = ledger
        self._lock = threading.Lock()

    # Delegate all public methods with lock held.

    def check_budget(self, estimate: ResourceCost) -> tuple[bool, str]:
        with self._lock:
            return self._ledger.check_budget(estimate)

    def can_afford(self, cost: ResourceCost) -> tuple[bool, str | None]:
        with self._lock:
            return self._ledger.can_afford(cost)

    def check_and_consume(
        self, cost: ResourceCost, agent_id: str = ""
    ) -> tuple[bool, str]:
        with self._lock:
            return self._ledger.check_and_consume(cost, agent_id)

    def consume(self, cost: ResourceCost) -> None:
        with self._lock:
            self._ledger.consume(cost)

    def record_cost(self, cost: ResourceCost, agent_id: str) -> None:
        with self._lock:
            self._ledger.record_cost(cost, agent_id)

    def reset(self, period: str = "hourly") -> None:
        with self._lock:
            self._ledger.reset(period)

    def reset_period(self) -> None:
        with self._lock:
            self._ledger.reset_period()

    def current_usage(self) -> ResourceCost:
        with self._lock:
            return self._ledger.current_usage()

    def usage_summary(self) -> dict[str, Any]:
        with self._lock:
            return self._ledger.usage_summary()

    def history(self) -> list[tuple[str, ResourceCost, float]]:
        with self._lock:
            return self._ledger.history()

    def agent_spend(self, agent_id: str) -> ResourceCost:
        with self._lock:
            return self._ledger.agent_spend(agent_id)

    def most_expensive_agents(self, k: int = 5) -> list[tuple[str, ResourceCost]]:
        with self._lock:
            return self._ledger.most_expensive_agents(k)

    @property
    def budget(self) -> ResourceBudget:
        return self._ledger.budget


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    "ResourceBudget",
    "ResourceLedger",
    "ThreadSafeResourceLedger",
]
