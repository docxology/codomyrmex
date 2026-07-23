"""Independent reference semantics for the deterministic Colony Kernel.

This module intentionally does not import :mod:`actuation_gate` or
:mod:`kernel`.  It is a small executable specification used for differential
tests and bounded replay.  Matching the implementation on tested inputs is
evidence of agreement, not a proof of safety or semantic completeness.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ReferenceDecision(StrEnum):
    EXECUTE = "execute"
    HOLD = "hold"
    REFUSE = "refuse"


@dataclass(frozen=True)
class ReferencePolicy:
    """Explicit policy parameters for reference evaluation.

    These are initial/example values matching the current implementation.  A
    caller can supply a measured configuration rather than treating them as
    universal constants.
    """

    execute_threshold: float = 0.75
    hold_threshold: float = 0.50
    trust_hard_floor: float = 0.30
    medium_pressure: float = 3.0
    high_pressure: float = 6.0
    missing_field_penalty: float = 0.35
    failure_penalty: float = 0.25
    weights: dict[str, float] = field(
        default_factory=lambda: {
            "budget": 0.30,
            "risk": 0.30,
            "trust": 0.25,
            "completeness": 0.15,
        }
    )

    def validate(self) -> None:
        if not self.execute_threshold >= self.hold_threshold:
            raise ValueError("execute_threshold must be >= hold_threshold")
        if not 0.0 <= self.trust_hard_floor <= 1.0:
            raise ValueError("trust_hard_floor must be in [0, 1]")
        if self.medium_pressure > self.high_pressure:
            raise ValueError("medium_pressure must be <= high_pressure")
        if abs(sum(self.weights.values()) - 1.0) > 1e-9:
            raise ValueError("reference gate weights must sum to one")


@dataclass(frozen=True)
class ReferenceInput:
    """Normalized inputs to the independent gate semantics."""

    budget_approved: bool
    role: str
    trust_score: float
    risk_pressure: float
    failure_pressure: float
    missing_fields: int
    critical_finding: bool = False
    recent_failures: int = 0

    @property
    def effective_pressure(self) -> float:
        return max(self.risk_pressure, self.failure_pressure)


@dataclass(frozen=True)
class ReferenceResult:
    decision: ReferenceDecision
    score: float
    budget_approved: bool
    trust_component: float
    risk_component: float
    completeness_component: float
    hard_override: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "score": self.score,
            "budget_approved": self.budget_approved,
            "trust_component": self.trust_component,
            "risk_component": self.risk_component,
            "completeness_component": self.completeness_component,
            "hard_override": self.hard_override,
        }


class ReferenceGate:
    """Pure reference evaluator for the current ternary gate policy."""

    def __init__(self, policy: ReferencePolicy | None = None) -> None:
        self.policy = policy or ReferencePolicy()
        self.policy.validate()

    def evaluate(self, inputs: ReferenceInput) -> ReferenceResult:
        policy = self.policy
        if inputs.missing_fields < 0:
            raise ValueError("missing_fields must be non-negative")
        if not 0.0 <= inputs.trust_score <= 1.0:
            raise ValueError("trust_score must be in [0, 1]")

        if not inputs.budget_approved:
            return ReferenceResult(
                ReferenceDecision.HOLD,
                0.0,
                False,
                0.0,
                0.0,
                0.0,
                "budget",
            )
        if inputs.role == "sandbox":
            return ReferenceResult(
                ReferenceDecision.REFUSE,
                0.0,
                True,
                0.0,
                0.0,
                0.0,
                "sandbox",
            )
        if inputs.trust_score < policy.trust_hard_floor:
            return ReferenceResult(
                ReferenceDecision.REFUSE,
                0.0,
                True,
                0.0,
                0.0,
                0.0,
                "trust_floor",
            )
        if inputs.critical_finding:
            return ReferenceResult(
                ReferenceDecision.REFUSE,
                0.0,
                True,
                0.0,
                0.0,
                0.0,
                "critical_finding",
            )

        pressure = inputs.effective_pressure
        risk_component = (
            0.0
            if pressure >= policy.high_pressure
            else 0.5
            if pressure >= policy.medium_pressure
            else 1.0
        )
        trust_component = 1.0 if inputs.trust_score >= 0.6 else 0.5
        if inputs.recent_failures >= 3:
            trust_component = max(0.0, trust_component - policy.failure_penalty)
        completeness_component = max(
            0.0, 1.0 - inputs.missing_fields * policy.missing_field_penalty
        )
        score = (
            policy.weights["budget"]
            + policy.weights["risk"] * risk_component
            + policy.weights["trust"] * trust_component
            + policy.weights["completeness"] * completeness_component
        )
        score = max(0.0, min(1.0, score))
        decision = (
            ReferenceDecision.EXECUTE
            if score >= policy.execute_threshold
            else ReferenceDecision.HOLD
            if score >= policy.hold_threshold
            else ReferenceDecision.REFUSE
        )
        return ReferenceResult(
            decision,
            score,
            True,
            trust_component,
            risk_component,
            completeness_component,
        )


@dataclass
class ReferenceState:
    """Small serializable state used for transition and replay tests."""

    pressures: dict[str, dict[str, float]] = field(default_factory=dict)
    trust: dict[str, float] = field(default_factory=dict)
    tick: int = 0

    def deposit(self, target: str, signal_type: str, strength: float) -> None:
        if strength < 0:
            raise ValueError("strength must be non-negative")
        target_signals = self.pressures.setdefault(target, {})
        target_signals[signal_type] = target_signals.get(signal_type, 0.0) + strength

    def evaporate(self, rates: dict[str, float]) -> None:
        for target in list(self.pressures):
            for signal_type in list(self.pressures[target]):
                self.pressures[target][signal_type] = max(
                    0.0,
                    self.pressures[target][signal_type] - rates.get(signal_type, 0.0),
                )
                if self.pressures[target][signal_type] == 0.0:
                    del self.pressures[target][signal_type]
            if not self.pressures[target]:
                del self.pressures[target]
        self.tick += 1

    def digest(self) -> str:
        payload = {"pressures": self.pressures, "trust": self.trust, "tick": self.tick}
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


__all__ = [
    "ReferenceDecision",
    "ReferenceGate",
    "ReferenceInput",
    "ReferencePolicy",
    "ReferenceResult",
    "ReferenceState",
]
