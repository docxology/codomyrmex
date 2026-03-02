"""
Unit tests for evolutionary_ai.fitness — Zero-Mock compliant.

Covers: FitnessResult, ScalarFitness (maximize/minimize), MultiObjectiveFitness
(evaluate/dominates), ConstrainedFitness (feasible/penalised).
"""

import pytest

from codomyrmex.evolutionary_ai.fitness import (
    ConstrainedFitness,
    FitnessResult,
    MultiObjectiveFitness,
    ScalarFitness,
)

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
        result = ff.evaluate([1.0, 2.0, 3.0])
        assert result.value == pytest.approx(6.0)

    def test_minimize_negates_value(self):
        ff = ScalarFitness(fn=lambda g: sum(g), maximize=False)
        result = ff.evaluate([1.0, 2.0, 3.0])
        assert result.value == pytest.approx(-6.0)

    def test_default_maximize_is_true(self):
        ff = ScalarFitness(fn=lambda g: 10.0)
        result = ff.evaluate([])
        assert result.value == 10.0

    def test_metadata_has_raw(self):
        ff = ScalarFitness(fn=lambda g: 5.0)
        result = ff.evaluate([])
        assert result.metadata["raw"] == 5.0

    def test_metadata_has_maximize_flag(self):
        ff = ScalarFitness(fn=lambda g: 5.0, maximize=False)
        result = ff.evaluate([])
        assert result.metadata["maximize"] is False

    def test_feasible_is_true(self):
        ff = ScalarFitness(fn=lambda g: 1.0)
        result = ff.evaluate([])
        assert result.feasible is True

    def test_returns_fitness_result(self):
        ff = ScalarFitness(fn=lambda g: 1.0)
        result = ff.evaluate([])
        assert isinstance(result, FitnessResult)

    def test_integer_genome(self):
        ff = ScalarFitness(fn=lambda g: float(g))
        result = ff.evaluate(42)
        assert result.value == 42.0


# ── MultiObjectiveFitness ─────────────────────────────────────────────


@pytest.mark.unit
class TestMultiObjectiveFitness:
    def test_evaluate_two_objectives(self):
        ff = MultiObjectiveFitness(
            objectives=[lambda g: g[0], lambda g: g[1]]
        )
        result = ff.evaluate([3.0, 5.0])
        assert result.value == [3.0, 5.0]

    def test_maximize_false_negates(self):
        ff = MultiObjectiveFitness(
            objectives=[lambda g: g[0]],
            maximize=[False],
        )
        result = ff.evaluate([4.0])
        assert result.value == [-4.0]

    def test_mixed_maximize(self):
        ff = MultiObjectiveFitness(
            objectives=[lambda g: g[0], lambda g: g[1]],
            maximize=[True, False],
        )
        result = ff.evaluate([3.0, 5.0])
        assert result.value[0] == pytest.approx(3.0)
        assert result.value[1] == pytest.approx(-5.0)

    def test_metadata_has_num_objectives(self):
        ff = MultiObjectiveFitness(objectives=[lambda g: 1.0, lambda g: 2.0])
        result = ff.evaluate([])
        assert result.metadata["num_objectives"] == 2

    def test_mismatched_maximize_raises(self):
        with pytest.raises(ValueError):
            MultiObjectiveFitness(
                objectives=[lambda g: 1.0],
                maximize=[True, False],  # 2 flags for 1 objective
            )

    def test_default_maximize_all_true(self):
        ff = MultiObjectiveFitness(objectives=[lambda g: 5.0, lambda g: 3.0])
        result = ff.evaluate([])
        assert result.value == [5.0, 3.0]


@pytest.mark.unit
class TestMultiObjectiveDominates:
    def test_a_dominates_b_clearly(self):
        # a=[5,5] > b=[3,3] in both objectives
        assert MultiObjectiveFitness.dominates([5.0, 5.0], [3.0, 3.0]) is True

    def test_b_dominates_a(self):
        assert MultiObjectiveFitness.dominates([3.0, 3.0], [5.0, 5.0]) is False

    def test_equal_vectors_no_dominance(self):
        assert MultiObjectiveFitness.dominates([5.0, 5.0], [5.0, 5.0]) is False

    def test_a_better_in_one_worse_in_other(self):
        # a=[5,3] vs b=[3,5]: a better in obj1, worse in obj2 — no dominance
        assert MultiObjectiveFitness.dominates([5.0, 3.0], [3.0, 5.0]) is False

    def test_a_dominates_with_equality_in_some(self):
        # a=[5,5] vs b=[5,3]: a==b in obj1, a>b in obj2 → a dominates
        assert MultiObjectiveFitness.dominates([5.0, 5.0], [5.0, 3.0]) is True


# ── ConstrainedFitness ────────────────────────────────────────────────


@pytest.mark.unit
class TestConstrainedFitness:
    def test_feasible_when_no_constraints(self):
        base = ScalarFitness(fn=lambda g: 10.0)
        ff = ConstrainedFitness(base=base, constraints=[])
        result = ff.evaluate([])
        assert result.feasible is True

    def test_value_unchanged_when_feasible(self):
        base = ScalarFitness(fn=lambda g: 10.0)
        ff = ConstrainedFitness(base=base, constraints=[])
        result = ff.evaluate([])
        assert result.value == pytest.approx(10.0)

    def test_infeasible_when_constraint_violated(self):
        base = ScalarFitness(fn=lambda g: 100.0)
        # Constraint: genome must be > 5; if genome <=5, violation = 5-genome
        ff = ConstrainedFitness(
            base=base,
            constraints=[lambda g: max(0, 5 - g)],
            penalty_weight=10.0,
        )
        result = ff.evaluate(3)  # violation = 5-3 = 2
        assert result.feasible is False

    def test_penalty_reduces_fitness(self):
        base = ScalarFitness(fn=lambda g: 100.0)
        ff = ConstrainedFitness(
            base=base,
            constraints=[lambda g: 2.0],  # constant violation = 2
            penalty_weight=10.0,
        )
        result = ff.evaluate([])
        # penalised = 100 - 10 * 2 = 80
        assert result.value == pytest.approx(80.0)

    def test_metadata_has_violations(self):
        base = ScalarFitness(fn=lambda g: 50.0)
        ff = ConstrainedFitness(
            base=base,
            constraints=[lambda g: 1.0, lambda g: 0.0],
        )
        result = ff.evaluate([])
        assert "violations" in result.metadata
        assert len(result.metadata["violations"]) == 2

    def test_metadata_has_base_fitness(self):
        base = ScalarFitness(fn=lambda g: 42.0)
        ff = ConstrainedFitness(base=base, constraints=[])
        result = ff.evaluate([])
        assert result.metadata["base_fitness"] == pytest.approx(42.0)

    def test_no_penalty_when_constraint_satisfied(self):
        base = ScalarFitness(fn=lambda g: 50.0)
        ff = ConstrainedFitness(
            base=base,
            constraints=[lambda g: -1.0],  # negative = satisfied
            penalty_weight=1000.0,
        )
        result = ff.evaluate([])
        assert result.value == pytest.approx(50.0)
        assert result.feasible is True

    def test_custom_penalty_weight(self):
        base = ScalarFitness(fn=lambda g: 100.0)
        ff = ConstrainedFitness(
            base=base,
            constraints=[lambda g: 1.0],
            penalty_weight=50.0,
        )
        result = ff.evaluate([])
        assert result.value == pytest.approx(100.0 - 50.0 * 1.0)
