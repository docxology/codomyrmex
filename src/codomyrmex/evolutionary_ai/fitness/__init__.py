"""
Fitness evaluation for evolutionary algorithms.

Provides an abstract FitnessFunction base class and concrete implementations
for scalar, multi-objective (Pareto), and constrained fitness evaluation.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, TypeVar

T = TypeVar("T")


@dataclass
class FitnessResult:
    """Container for a fitness evaluation outcome.

    Attributes:
        value: Primary fitness value (scalar or vector depending on function).
        feasible: Whether the genome satisfies all constraints.
        metadata: Arbitrary extra information from the evaluation.
    """
    value: float | list[float]
    feasible: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


class FitnessFunction(ABC):
    """Abstract base class for fitness functions.

    Subclasses must implement ``evaluate`` which receives a genome (of any
    type) and returns a :class:`FitnessResult`.
    """

    @abstractmethod
    def evaluate(self, genome: Any) -> FitnessResult:
        """Evaluate the fitness of a genome.

        Args:
            genome: The genome representation to evaluate.

        Returns:
            A FitnessResult containing the fitness value and metadata.
        """


class ScalarFitness(FitnessFunction):
    """Single-objective fitness function.

    Wraps a user-supplied callable that maps a genome to a single float.

    Args:
        fn: A callable ``(genome) -> float``.
        maximize: If True (default) higher values are better; if False
                  the returned value is negated so the framework can always
                  maximize internally.
    """

    def __init__(
        self,
        fn: Any,  # Callable[[Any], float]
        maximize: bool = True,
    ) -> None:
        self._fn = fn
        self._maximize = maximize

    def evaluate(self, genome: Any) -> FitnessResult:
        """Evaluate."""
        raw = float(self._fn(genome))
        value = raw if self._maximize else -raw
        return FitnessResult(
            value=value,
            metadata={"raw": raw, "maximize": self._maximize},
        )


class MultiObjectiveFitness(FitnessFunction):
    """Pareto-based multi-objective fitness function.

    Evaluates a genome against multiple objectives and supports Pareto
    dominance comparison.

    Args:
        objectives: A list of callables, each ``(genome) -> float``.
        maximize: Per-objective direction flags.  Defaults to all-True.
    """

    def __init__(
        self,
        objectives: list[Any],  # list[Callable[[Any], float]]
        maximize: list[bool] | None = None,
    ) -> None:
        self._objectives = objectives
        self._maximize = maximize or [True] * len(objectives)
        if len(self._maximize) != len(self._objectives):
            raise ValueError("maximize length must match number of objectives")

    def evaluate(self, genome: Any) -> FitnessResult:
        """Evaluate."""
        values: list[float] = []
        for fn, is_max in zip(self._objectives, self._maximize, strict=False):
            raw = float(fn(genome))
            values.append(raw if is_max else -raw)
        return FitnessResult(
            value=values,
            metadata={"num_objectives": len(self._objectives)},
        )

    @staticmethod
    def dominates(a: list[float], b: list[float]) -> bool:
        """Return True if fitness vector *a* Pareto-dominates *b*.

        *a* dominates *b* iff a is >= b in every objective and strictly
        greater in at least one objective (assuming maximisation).

        Args:
            a: Fitness vector of individual A.
            b: Fitness vector of individual B.

        Returns:
            True if a dominates b.
        """
        dominated_in_at_least_one = False
        for ai, bi in zip(a, b, strict=False):
            if ai < bi:
                return False
            if ai > bi:
                dominated_in_at_least_one = True
        return dominated_in_at_least_one


class ConstrainedFitness(FitnessFunction):
    """Fitness function with constraint penalties.

    Evaluates a base fitness and then applies penalty terms for each
    violated constraint.

    Args:
        base: The underlying FitnessFunction producing the raw fitness.
        constraints: A list of callables ``(genome) -> float`` where a
                     return value <= 0 means the constraint is satisfied
                     and a positive value is the magnitude of violation.
        penalty_weight: Multiplier applied to total constraint violation
                        when computing the penalised fitness.
    """

    def __init__(
        self,
        base: FitnessFunction,
        constraints: list[Any],  # list[Callable[[Any], float]]
        penalty_weight: float = 1000.0,
    ) -> None:
        self._base = base
        self._constraints = constraints
        self._penalty_weight = penalty_weight

    def evaluate(self, genome: Any) -> FitnessResult:
        """Evaluate."""
        base_result = self._base.evaluate(genome)
        base_value = (
            base_result.value
            if isinstance(base_result.value, (int, float))
            else sum(base_result.value)
        )

        violations: list[float] = []
        total_violation = 0.0
        for constraint_fn in self._constraints:
            v = float(constraint_fn(genome))
            violations.append(v)
            if v > 0:
                total_violation += v

        feasible = total_violation == 0.0
        penalised = base_value - self._penalty_weight * total_violation

        return FitnessResult(
            value=penalised,
            feasible=feasible,
            metadata={
                "base_fitness": base_value,
                "violations": violations,
                "total_violation": total_violation,
                "penalty_weight": self._penalty_weight,
            },
        )


__all__ = [
    "ConstrainedFitness",
    "FitnessFunction",
    "FitnessResult",
    "MultiObjectiveFitness",
    "ScalarFitness",
]
