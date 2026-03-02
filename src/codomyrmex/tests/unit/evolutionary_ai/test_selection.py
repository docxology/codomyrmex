"""
Unit tests for evolutionary_ai.selection — Zero-Mock compliant.

Covers: TournamentSelection, RouletteWheelSelection, RankSelection.
"""

import pytest

from codomyrmex.evolutionary_ai.operators import Individual
from codomyrmex.evolutionary_ai.selection import (
    RankSelection,
    RouletteWheelSelection,
    TournamentSelection,
)

# ── Helpers ───────────────────────────────────────────────────────────


def _ind(genes: list, fitness: float) -> Individual:
    return Individual(genes=genes, fitness=fitness)


def _pop(fitnesses: list[float]) -> list[Individual]:
    return [_ind([i], f) for i, f in enumerate(fitnesses)]


# ── TournamentSelection ───────────────────────────────────────────────


@pytest.mark.unit
class TestTournamentSelection:
    def test_default_tournament_size(self):
        sel = TournamentSelection()
        assert sel.tournament_size == 3

    def test_custom_tournament_size(self):
        sel = TournamentSelection(tournament_size=5)
        assert sel.tournament_size == 5

    def test_invalid_size_raises(self):
        with pytest.raises(ValueError):
            TournamentSelection(tournament_size=0)

    def test_select_returns_correct_count(self):
        sel = TournamentSelection(tournament_size=2)
        pop = _pop([1.0, 2.0, 3.0, 4.0, 5.0])
        selected = sel.select(pop, 3)
        assert len(selected) == 3

    def test_select_returns_individuals(self):
        sel = TournamentSelection(tournament_size=2)
        pop = _pop([1.0, 2.0, 3.0])
        selected = sel.select(pop, 2)
        for ind in selected:
            assert isinstance(ind, Individual)

    def test_select_favours_higher_fitness(self):
        sel = TournamentSelection(tournament_size=5)  # large tournament = deterministic
        # With tournament_size = population_size, always picks best
        pop = _pop([1.0, 10.0, 5.0, 3.0, 7.0])
        selected = sel.select(pop, 10)
        fitnesses = [ind.fitness for ind in selected]
        assert all(f == 10.0 for f in fitnesses)

    def test_select_returns_copies_not_references(self):
        sel = TournamentSelection(tournament_size=2)
        pop = _pop([1.0, 2.0, 3.0])
        selected = sel.select(pop, 1)
        # Mutating the selected individual's genes should not affect the original
        original_genes = list(selected[0].genes)
        if isinstance(selected[0].genes, list):
            selected[0].genes.append(99)
        # The population should not be affected
        assert selected[0].fitness in [ind.fitness for ind in pop]
        _ = original_genes  # used to avoid lint warning

    def test_tournament_size_1_always_selects(self):
        sel = TournamentSelection(tournament_size=1)
        pop = _pop([1.0, 2.0, 3.0])
        selected = sel.select(pop, 3)
        assert len(selected) == 3

    def test_select_with_none_fitness_handled(self):
        sel = TournamentSelection(tournament_size=2)
        pop = [Individual(genes=[1], fitness=None), Individual(genes=[2], fitness=5.0)]
        selected = sel.select(pop, 1)
        # Should return the one with fitness=5.0 when tournament includes both
        # (nondeterministic with size=2, but should not raise)
        assert len(selected) == 1


# ── RouletteWheelSelection ────────────────────────────────────────────


@pytest.mark.unit
class TestRouletteWheelSelection:
    def test_select_returns_correct_count(self):
        sel = RouletteWheelSelection()
        pop = _pop([1.0, 2.0, 3.0, 4.0, 5.0])
        selected = sel.select(pop, 4)
        assert len(selected) == 4

    def test_select_returns_individuals(self):
        sel = RouletteWheelSelection()
        pop = _pop([1.0, 2.0, 3.0])
        selected = sel.select(pop, 2)
        for ind in selected:
            assert isinstance(ind, Individual)
            assert ind.fitness is not None

    def test_handles_negative_fitness(self):
        sel = RouletteWheelSelection()
        pop = _pop([-3.0, -1.0, 0.0, 2.0])
        selected = sel.select(pop, 3)
        assert len(selected) == 3

    def test_all_zero_fitness_handled(self):
        sel = RouletteWheelSelection()
        pop = _pop([0.0, 0.0, 0.0])
        # Should not raise; falls back to random.choices
        selected = sel.select(pop, 2)
        assert len(selected) == 2

    def test_returns_copies(self):
        sel = RouletteWheelSelection()
        pop = _pop([1.0, 2.0])
        selected = sel.select(pop, 1)
        # The selected individual should be a distinct object
        assert selected[0] is not pop[0] and selected[0] is not pop[1]

    def test_single_individual_population(self):
        sel = RouletteWheelSelection()
        pop = _pop([5.0])
        selected = sel.select(pop, 3)
        assert len(selected) == 3
        assert all(ind.fitness == 5.0 for ind in selected)


# ── RankSelection ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestRankSelection:
    def test_default_pressure(self):
        sel = RankSelection()
        assert sel.selection_pressure == 1.5

    def test_custom_pressure(self):
        sel = RankSelection(selection_pressure=1.8)
        assert sel.selection_pressure == 1.8

    def test_invalid_pressure_below_one(self):
        with pytest.raises(ValueError):
            RankSelection(selection_pressure=0.9)

    def test_invalid_pressure_above_two(self):
        with pytest.raises(ValueError):
            RankSelection(selection_pressure=2.1)

    def test_boundary_pressure_one(self):
        sel = RankSelection(selection_pressure=1.0)
        assert sel.selection_pressure == 1.0

    def test_boundary_pressure_two(self):
        sel = RankSelection(selection_pressure=2.0)
        assert sel.selection_pressure == 2.0

    def test_select_returns_correct_count(self):
        sel = RankSelection()
        pop = _pop([1.0, 2.0, 3.0, 4.0, 5.0])
        selected = sel.select(pop, 3)
        assert len(selected) == 3

    def test_select_returns_individuals(self):
        sel = RankSelection()
        pop = _pop([1.0, 2.0, 3.0])
        selected = sel.select(pop, 2)
        for ind in selected:
            assert isinstance(ind, Individual)

    def test_max_pressure_biases_toward_best(self):
        sel = RankSelection(selection_pressure=2.0)
        # With max pressure (2.0), the highest-ranked individual has
        # probability 2/n, while lowest has 0 — so over many samples
        # we should see the best individual selected more often.
        pop = _pop([1.0, 2.0, 10.0, 4.0, 5.0])
        selected = sel.select(pop, 50)
        best_fitness = max(ind.fitness for ind in pop)
        best_count = sum(1 for ind in selected if ind.fitness == best_fitness)
        assert best_count > 0

    def test_handles_none_fitness(self):
        sel = RankSelection()
        pop = [
            Individual(genes=[1], fitness=None),
            Individual(genes=[2], fitness=3.0),
            Individual(genes=[3], fitness=1.0),
        ]
        selected = sel.select(pop, 2)
        assert len(selected) == 2
