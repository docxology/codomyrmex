"""Solver-neutral and optional Z3 encodings for Colony Kernel obligations."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class FormalStatus(StrEnum):
    PROVED = "proved"
    REFUTED = "refuted"
    UNKNOWN = "unknown"
    TIMEOUT = "timeout"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class KernelFormalSnapshot:
    """Finite values needed to state the current kernel obligations."""

    weights: dict[str, float]
    trust_score: float
    pheromone_strength: float
    pheromone_max_strength: float
    score_low_pressure: float
    score_high_pressure: float
    risk_component_low: float
    risk_component_high: float
    score_unrelated_before: float
    score_unrelated_after: float
    has_execute_verdict: bool
    has_authorization: bool
    has_execution_receipt: bool
    has_outcome_link: bool
    role_thresholds: tuple[float, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class FormalResult:
    invariant: str
    status: FormalStatus
    reason: str = ""
    counterexample: dict[str, Any] | None = None
    elapsed_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "invariant": self.invariant,
            "status": self.status.value,
            "reason": self.reason,
            "counterexample": self.counterexample,
            "elapsed_ms": self.elapsed_ms,
        }


def runtime_obligations(snapshot: KernelFormalSnapshot) -> dict[str, bool]:
    """Evaluate the same obligations without requiring a solver."""

    return {
        "weights_sum_to_one": abs(sum(snapshot.weights.values()) - 1.0) <= 1e-9,
        "trust_in_range": 0.0 <= snapshot.trust_score <= 1.0,
        "pheromone_in_range": 0.0
        <= snapshot.pheromone_strength
        <= snapshot.pheromone_max_strength,
        "role_thresholds_monotonic": all(
            left < right
            for left, right in zip(
                snapshot.role_thresholds, snapshot.role_thresholds[1:], strict=False
            )
        ),
        "pressure_monotonicity": (
            snapshot.risk_component_high < snapshot.risk_component_low
            or snapshot.score_high_pressure <= snapshot.score_low_pressure + 1e-9
        ),
        "unrelated_target_locality": abs(
            snapshot.score_unrelated_before - snapshot.score_unrelated_after
        )
        <= 1e-9,
        "authorized_outcome_linkage": (
            not snapshot.has_outcome_link
            or (
                snapshot.has_execute_verdict
                and snapshot.has_authorization
                and snapshot.has_execution_receipt
            )
        ),
    }


def z3_available() -> bool:
    """Return whether the optional Z3 dependency can be imported."""

    try:
        import z3
    except ImportError:
        return False
    return True


def prove_kernel_obligations(
    snapshot: KernelFormalSnapshot, *, timeout_ms: int = 1000
) -> list[FormalResult]:
    """Prove bounded obligations with Z3 when the optional extra is installed.

    The function deliberately returns structured ``unavailable`` results when
    Z3 is absent, making CI state visible without pretending runtime checks are
    solver proofs.
    """

    if timeout_ms <= 0:
        raise ValueError("timeout_ms must be positive")
    try:
        import z3
    except ImportError:
        return [
            FormalResult(
                invariant=name,
                status=FormalStatus.UNAVAILABLE,
                reason="z3-solver is not installed; runtime predicates remain available",
            )
            for name in runtime_obligations(snapshot)
        ]

    weights = {name: z3.RealVal(str(value)) for name, value in snapshot.weights.items()}
    score_low = z3.RealVal(str(snapshot.score_low_pressure))
    score_high = z3.RealVal(str(snapshot.score_high_pressure))
    risk_low = z3.RealVal(str(snapshot.risk_component_low))
    risk_high = z3.RealVal(str(snapshot.risk_component_high))
    checks: list[tuple[str, Any]] = [
        ("weights_sum_to_one", z3.Sum(list(weights.values())) == 1),
        (
            "trust_in_range",
            z3.And(
                z3.RealVal(str(snapshot.trust_score)) >= 0,
                z3.RealVal(str(snapshot.trust_score)) <= 1,
            ),
        ),
        (
            "pheromone_in_range",
            z3.And(
                z3.RealVal(str(snapshot.pheromone_strength)) >= 0,
                z3.RealVal(str(snapshot.pheromone_strength))
                <= z3.RealVal(str(snapshot.pheromone_max_strength)),
            ),
        ),
        (
            "role_thresholds_monotonic",
            z3.And(
                [
                    z3.RealVal(str(left)) < z3.RealVal(str(right))
                    for left, right in zip(
                        snapshot.role_thresholds,
                        snapshot.role_thresholds[1:],
                        strict=False,
                    )
                ]
                or [z3.BoolVal(True)]
            ),
        ),
        (
            "pressure_monotonicity",
            z3.Implies(risk_high >= risk_low, score_high <= score_low),
        ),
        (
            "unrelated_target_locality",
            z3.RealVal(str(snapshot.score_unrelated_before))
            == z3.RealVal(str(snapshot.score_unrelated_after)),
        ),
        (
            "authorized_outcome_linkage",
            z3.Implies(
                z3.BoolVal(snapshot.has_outcome_link),
                z3.And(
                    z3.BoolVal(snapshot.has_execute_verdict),
                    z3.BoolVal(snapshot.has_authorization),
                    z3.BoolVal(snapshot.has_execution_receipt),
                ),
            ),
        ),
    ]
    results: list[FormalResult] = []
    for name, obligation in checks:
        started = time.perf_counter()
        solver = z3.Solver()
        solver.set(timeout=timeout_ms)
        solver.add(z3.Not(obligation))
        outcome = solver.check()
        elapsed = (time.perf_counter() - started) * 1000
        if outcome == z3.unsat:
            results.append(FormalResult(name, FormalStatus.PROVED, elapsed_ms=elapsed))
        elif outcome == z3.sat:
            model = solver.model()
            results.append(
                FormalResult(
                    name,
                    FormalStatus.REFUTED,
                    reason="solver produced a counterexample",
                    counterexample={
                        str(decl): str(model[decl]) for decl in model.decls()
                    },
                    elapsed_ms=elapsed,
                )
            )
        elif "timeout" in solver.reason_unknown().lower():
            results.append(
                FormalResult(
                    name,
                    FormalStatus.TIMEOUT,
                    solver.reason_unknown(),
                    elapsed_ms=elapsed,
                )
            )
        else:
            results.append(
                FormalResult(
                    name,
                    FormalStatus.UNKNOWN,
                    solver.reason_unknown(),
                    elapsed_ms=elapsed,
                )
            )
    return results


__all__ = [
    "FormalResult",
    "FormalStatus",
    "KernelFormalSnapshot",
    "prove_kernel_obligations",
    "runtime_obligations",
    "z3_available",
]
