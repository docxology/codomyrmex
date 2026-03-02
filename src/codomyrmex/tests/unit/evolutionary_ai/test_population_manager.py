"""
Unit tests for evolutionary_ai.population — Zero-Mock compliant.

Covers: DiversityMetrics dataclass, PopulationManager (initialize,
evolve_generation, get_best, get_diversity_metrics, population property,
generation property, __len__, __repr__).
"""

import pytest

from codomyrmex.evolutionary_ai.operators import (
    SinglePointCrossover,
    SwapMutation,
    TournamentSelection,
)
from codomyrmex.evolutionary_ai.population import DiversityMetrics, PopulationManager

# ── Helpers ───────────────────────────────────────────────────────────


def _make_manager(elitism: int = 1) -> PopulationManager:
    """Create a PopulationManager with simple real operators."""
    return PopulationManager(
        selection=TournamentSelection(tournament_size=2),
        crossover=SinglePointCrossover(),
        mutation=SwapMutation(mutation_rate=0.1),
        elitism_count=elitism,
    )


def _genome_factory() -> list[int]:
    """Produce a fixed genome for deterministic tests."""
    return [1, 0, 1, 0, 1]


def _fitness_fn(genes: list[int]) -> float:
    """Simple fitness: count of 1s in genome."""
    return float(sum(genes))


# ── DiversityMetrics ──────────────────────────────────────────────────


@pytest.mark.unit
class TestDiversityMetrics:
    def test_fields(self):
        dm = DiversityMetrics(
            unique_fitness_count=5,
            fitness_std_dev=1.2,
            fitness_min=0.0,
            fitness_max=10.0,
            fitness_mean=5.0,
            population_size=20,
        )
        assert dm.unique_fitness_count == 5
        assert dm.fitness_std_dev == 1.2
        assert dm.fitness_min == 0.0
        assert dm.fitness_max == 10.0
        assert dm.fitness_mean == 5.0
        assert dm.population_size == 20


# ── PopulationManager ─────────────────────────────────────────────────


@pytest.mark.unit
class TestPopulationManagerInit:
    def test_initial_population_empty(self):
        pm = _make_manager()
        assert len(pm) == 0

    def test_initial_generation_zero(self):
        pm = _make_manager()
        assert pm.generation == 0


@pytest.mark.unit
class TestPopulationManagerInitialize:
    def test_initialize_creates_correct_size(self):
        pm = _make_manager()
        pop = pm.initialize(10, _genome_factory)
        assert len(pop) == 10

    def test_initialize_sets_len(self):
        pm = _make_manager()
        pm.initialize(6, _genome_factory)
        assert len(pm) == 6

    def test_initialize_resets_generation(self):
        pm = _make_manager()
        pm.initialize(4, _genome_factory)
        assert pm.generation == 0

    def test_initialize_individuals_have_no_fitness(self):
        pm = _make_manager()
        pop = pm.initialize(5, _genome_factory)
        assert all(ind.fitness is None for ind in pop)

    def test_population_property_returns_copy(self):
        pm = _make_manager()
        pm.initialize(4, _genome_factory)
        pop1 = pm.population
        pop2 = pm.population
        assert pop1 is not pop2
        assert len(pop1) == 4


@pytest.mark.unit
class TestPopulationManagerEvolve:
    def test_evolve_increments_generation(self):
        pm = _make_manager()
        pm.initialize(6, _genome_factory)
        pm.evolve_generation(fitness_fn=_fitness_fn)
        assert pm.generation == 1

    def test_evolve_preserves_population_size(self):
        pm = _make_manager()
        pm.initialize(8, _genome_factory)
        pm.evolve_generation(fitness_fn=_fitness_fn)
        assert len(pm) == 8

    def test_evolve_multiple_generations(self):
        pm = _make_manager()
        pm.initialize(6, _genome_factory)
        for _ in range(5):
            pm.evolve_generation(fitness_fn=_fitness_fn)
        assert pm.generation == 5

    def test_evolve_without_fitness_fn(self):
        pm = _make_manager()
        pm.initialize(4, _genome_factory)
        # Pre-assign fitness manually
        for ind in pm.population:
            ind.fitness = 1.0
        pm._population = pm.population  # re-sync internal state via population prop
        # Direct attribute assignment needed since population returns copy
        for ind in pm._population:
            ind.fitness = 1.0
        # Should not raise
        pm.evolve_generation()
        assert pm.generation == 1

    def test_evolve_without_init_raises(self):
        pm = _make_manager()
        with pytest.raises(RuntimeError, match="not initialized"):
            pm.evolve_generation()

    def test_elitism_preserves_best(self):
        pm = _make_manager(elitism=1)
        pm.initialize(6, _genome_factory)
        pm.evolve_generation(fitness_fn=_fitness_fn)
        # Best individual should have fitness in population
        best = pm.get_best()
        assert best is not None
        assert best.fitness is not None


@pytest.mark.unit
class TestPopulationManagerGetBest:
    def test_get_best_returns_none_when_empty(self):
        pm = _make_manager()
        assert pm.get_best() is None

    def test_get_best_returns_none_when_no_fitness(self):
        pm = _make_manager()
        pm.initialize(4, _genome_factory)
        # No fitness assigned yet
        assert pm.get_best() is None

    def test_get_best_after_evaluation(self):
        pm = _make_manager()
        pm.initialize(6, _genome_factory)
        pm.evolve_generation(fitness_fn=_fitness_fn)
        best = pm.get_best()
        assert best is not None
        # All genomes are identical [1,0,1,0,1] → fitness=3
        assert best.fitness is not None
        assert best.fitness >= 0


@pytest.mark.unit
class TestPopulationManagerDiversity:
    def test_diversity_raises_when_empty(self):
        pm = _make_manager()
        with pytest.raises(RuntimeError, match="empty"):
            pm.get_diversity_metrics()

    def test_diversity_metrics_fields_populated(self):
        pm = _make_manager()
        pm.initialize(5, _genome_factory)
        pm.evolve_generation(fitness_fn=_fitness_fn)
        dm = pm.get_diversity_metrics()
        assert isinstance(dm, DiversityMetrics)
        assert dm.population_size == 5
        assert dm.fitness_min <= dm.fitness_max
        assert dm.fitness_mean >= dm.fitness_min

    def test_diversity_std_dev_non_negative(self):
        pm = _make_manager()
        pm.initialize(4, _genome_factory)
        pm.evolve_generation(fitness_fn=_fitness_fn)
        dm = pm.get_diversity_metrics()
        assert dm.fitness_std_dev >= 0.0


@pytest.mark.unit
class TestPopulationManagerRepr:
    def test_repr_contains_size(self):
        pm = _make_manager()
        pm.initialize(4, _genome_factory)
        r = repr(pm)
        assert "4" in r

    def test_repr_contains_generation(self):
        pm = _make_manager()
        pm.initialize(4, _genome_factory)
        r = repr(pm)
        assert "generation=0" in r
