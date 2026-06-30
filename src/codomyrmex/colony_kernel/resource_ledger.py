"""Resource ledger — tracks colony action budgets and enforces spending caps.

All Colony Kernel modules import models from models.py. This module depends
only on models.py and stdlib; no cross-subsystem imports.

No external dependencies beyond stdlib.
"""

from __future__ import annotations

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

    # Internal state — not part of the public interface.
    _accumulated: ResourceCost = field(
        default_factory=ResourceCost, init=False, repr=False
    )
    _history: list[tuple[str, ResourceCost, float]] = field(
        default_factory=list, init=False, repr=False
    )
    _period_start: float = field(default_factory=time.time, init=False, repr=False)

    # ---------------------------------------------------------------------------
    # Period reset
    # ---------------------------------------------------------------------------

    def _maybe_reset(self) -> None:
        """Reset accumulated cost if the budget period has elapsed."""
        if self.budget.period_seconds <= 0:
            return
        if time.time() - self._period_start >= self.budget.period_seconds:
            self._accumulated = ResourceCost()
            self._period_start = time.time()

    def reset_period(self) -> None:
        """Manually reset the period accumulator."""
        self._accumulated = ResourceCost()
        self._period_start = time.time()

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
        self._maybe_reset()
        self._accumulated = self._accumulated + cost
        self._history.append((agent_id, cost, time.time()))

    def consume(self, cost: ResourceCost) -> None:
        """Record actual consumption after an action executes.

        This is the canonical method called by ColonyKernel.record_outcome.
        Does not require an agent_id — use record_cost for per-agent tracking.
        """
        self._maybe_reset()
        self._accumulated = self._accumulated + cost

    def reset(self, period: str = "hourly") -> None:
        """Reset the accumulated usage counter.

        History is preserved across resets; only the running total is cleared.

        Args:
            period: Human-readable label describing the reset period (e.g.
                ``"hourly"``, ``"daily"``).  Not used computationally — stored
                for observability.  Defaults to ``"hourly"``.
        """
        self._accumulated = ResourceCost()
        self._period_start = time.time()

    # ---------------------------------------------------------------------------
    # Queries
    # ---------------------------------------------------------------------------

    def check_budget(self, estimate: ResourceCost) -> tuple[bool, str]:
        """Return (approved, reason).

        Approved when accumulating *estimate* on top of current usage would
        not breach any budget dimension. The accumulator is NOT modified here;
        call ``consume`` after the action executes.
        """
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

    def current_usage(self) -> ResourceCost:
        """Return the accumulated cost since the last :meth:`reset`.

        Returns a copy; mutating the returned object does not affect the ledger.
        """
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
        return list(self._history)

    def agent_spend(self, agent_id: str) -> ResourceCost:
        """Return the total spend accumulated by a single agent across all history.

        Args:
            agent_id: The agent whose total spend to compute.

        Returns:
            Summed ``ResourceCost`` for that agent; zero-cost if unknown.
        """
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


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    "ResourceBudget",
    "ResourceLedger",
]
