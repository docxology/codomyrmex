"""
Unit tests for evolutionary_ai.fitness — Zero-Mock compliant.
"""

import pytest

from codomyrmex.evolutionary_ai.fitness.fitness import (
    ConstrainedFitness,
    FitnessResult,
    MultiObjectiveFitness,
    ScalarFitness,
)
from codomyrmex.evolutionary_ai.genome.genome import Individual

# ── FitnessResult ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestFitnessResult:
    def test_default_feasible(self):
        r = FitnessResult(value=1.0)
        assert r.feasible is True

    def test_default_metadata_empty(self):
        r = FitnessResult(value=0.5)
        assert r.metadata == {}

    def test_custom_fields(self):
        r = FitnessResult(value=3.14, feasible=False, metadata={"reason": "violated"})
        assert r.value == 3.14
        assert r.feasible is False
        assert r.metadata["reason"] == "violated"

    def test_list_value(self):
        r = FitnessResult(value=[1.0, 2.0, 3.0])
        assert r.value == [1.0, 2.0, 3.0]


# ── ScalarFitness ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestScalarFitness:
    def test_maximize_returns_raw_value(self):
        ff = ScalarFitness(fn=lambda g: sum(g), maximize=True)
        ind = Individual(genes=[1.0, 2.0, 3.0])
        result = ff.evaluate(ind)
        assert result.value == pytest.approx(6.0)

    def test_minimize_negates_value(self):
        ff = ScalarFitness(fn=lambda g: sum(g), maximize=False)
        ind = Individual(genes=[1.0, 2.0, 3.0])
        result = ff.evaluate(ind)
        assert result.value == pytest.approx(-6.0)

    def test_metadata_has_raw(self):
        ff = ScalarFitness(fn=lambda g: 5.0)
        ind = Individual(genes=[])
        result = ff.evaluate(ind)
        assert result.metadata["raw"] == 5.0

    def test_feasible_is_true(self):
        ff = ScalarFitness(fn=lambda g: 1.0)
        ind = Individual(genes=[])
        result = ff.evaluate(ind)
        assert result.feasible is True


# ── MultiObjectiveFitness ─────────────────────────────────────────────


@pytest.mark.unit
class TestMultiObjectiveFitness:
    def test_evaluate_two_objectives(self):
        ff = MultiObjectiveFitness(
            objectives=[lambda g: g[0], lambda g: g[1]]
        )
        ind = Individual(genes=[3.0, 5.0])
        result = ff.evaluate(ind)
        assert result.value == [3.0, 5.0]

    def test_mixed_maximize(self):
        ff = MultiObjectiveFitness(
            objectives=[lambda g: g[0], lambda g: g[1]],
            maximize=[True, False],
        )
        ind = Individual(genes=[3.0, 5.0])
        result = ff.evaluate(ind)
        assert result.value[0] == pytest.approx(3.0)
        assert result.value[1] == pytest.approx(-5.0)

    def test_mismatched_maximize_raises(self):
        with pytest.raises(ValueError):
            MultiObjectiveFitness(
                objectives=[lambda g: 1.0],
                maximize=[True, False],
            )

@pytest.mark.unit
class TestMultiObjectiveDominates:
    def test_a_dominates_b(self):
        assert MultiObjectiveFitness.dominates([5.0, 5.0], [3.0, 3.0]) is True
        assert MultiObjectiveFitness.dominates([5.0, 3.0], [3.0, 3.0]) is True
        assert MultiObjectiveFitness.dominates([3.0, 3.0], [5.0, 5.0]) is False
        assert MultiObjectiveFitness.dominates([5.0, 3.0], [3.0, 5.0]) is False


# ── ConstrainedFitness ────────────────────────────────────────────────


@pytest.mark.unit
class TestConstrainedFitness:
    def test_feasible_when_no_constraints(self):
        base = ScalarFitness(fn=lambda g: 10.0)
        ff = ConstrainedFitness(base=base, constraints=[])
        ind = Individual(genes=[])
        result = ff.evaluate(ind)
        assert result.feasible is True
        assert result.value == pytest.approx(10.0)

    def test_penalty_reduces_fitness(self):
        base = ScalarFitness(fn=lambda g: 100.0)
        ff = ConstrainedFitness(
            base=base,
            constraints=[lambda g: 2.0],  # constant violation = 2
            penalty_weight=10.0,
        )
        ind = Individual(genes=[])
        result = ff.evaluate(ind)
        # penalised = 100 - 10 * 2 = 80
        assert result.value == pytest.approx(80.0)
        assert result.feasible is False
