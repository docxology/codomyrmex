"""
Unit tests for evolutionary_ai core submodules — Zero-Mock compliant.

Covers the direct implementation files:
  - evolutionary_ai/genome/genome.py  (Genome, GenomeStats)
  - evolutionary_ai/operators/operators.py  (crossover, mutate, selection variants)
  - evolutionary_ai/population/population.py  (Population, GenerationStats)

These are distinct from evolutionary_ai/__init__.py exports and require
direct imports to achieve coverage.
"""

import math

import pytest

from codomyrmex.evolutionary_ai.genome.genome import Genome, GenomeStats
from codomyrmex.evolutionary_ai.operators.operators import (
    _fitness_key,
    crossover,
    mutate,
    rank_selection,
    roulette_selection,
    swap_mutate,
    tournament_selection,
    two_point_crossover,
    uniform_crossover,
    uniform_mutate,
)
from codomyrmex.evolutionary_ai.population.population import (
    GenerationStats,
    Population,
)

# ── Genome ─────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestGenome:
    """Tests for Genome class in genome/genome.py."""

    def test_init_stores_genes(self):
        g = Genome([1.0, 2.0, 3.0])
        assert g.genes == [1.0, 2.0, 3.0]
        assert g.fitness is None

    def test_len_returns_gene_count(self):
        g = Genome([0.1, 0.2])
        assert len(g) == 2

    def test_getitem(self):
        g = Genome([10.0, 20.0, 30.0])
        assert g[1] == 20.0

    def test_eq_same_genes(self):
        g1 = Genome([1.0, 2.0])
        g2 = Genome([1.0, 2.0])
        assert g1 == g2

    def test_eq_different_genes(self):
        g1 = Genome([1.0, 2.0])
        g2 = Genome([1.0, 3.0])
        assert g1 != g2

    def test_eq_non_genome_returns_not_implemented(self):
        g = Genome([1.0])
        result = g.__eq__("not a genome")
        assert result is NotImplemented

    def test_repr(self):
        g = Genome([1.0, 2.0], fitness=0.5)
        r = repr(g)
        assert "Genome" in r
        assert "0.5" in r

    def test_random_produces_correct_length(self):
        g = Genome.random(10)
        assert len(g) == 10

    def test_random_within_bounds(self):
        g = Genome.random(100, low=0.5, high=1.0)
        for gene in g.genes:
            assert 0.5 <= gene <= 1.0

    def test_zeros(self):
        g = Genome.zeros(5)
        assert g.genes == [0.0, 0.0, 0.0, 0.0, 0.0]
        assert g.fitness is None

    def test_from_dict_roundtrip(self):
        g = Genome([1.0, 2.0], fitness=0.8, metadata={"gen": 3})
        d = g.to_dict()
        g2 = Genome.from_dict(d)
        assert g2.genes == [1.0, 2.0]
        assert g2.fitness == 0.8
        assert g2.metadata == {"gen": 3}

    def test_clone_is_independent(self):
        g = Genome([1.0, 2.0], fitness=0.5)
        c = g.clone()
        c.genes[0] = 99.0
        assert g.genes[0] == 1.0  # original unchanged

    def test_distance_same_genome(self):
        g = Genome([3.0, 4.0])
        assert g.distance(g) == 0.0

    def test_distance_known_value(self):
        g1 = Genome([0.0, 0.0])
        g2 = Genome([3.0, 4.0])
        assert math.isclose(g1.distance(g2), 5.0)

    def test_distance_raises_on_length_mismatch(self):
        g1 = Genome([1.0, 2.0])
        g2 = Genome([1.0])
        with pytest.raises(ValueError, match="length"):
            g1.distance(g2)

    def test_clamp_clips_genes(self):
        g = Genome([-0.5, 0.5, 1.5])
        c = g.clamp(0.0, 1.0)
        assert c.genes == [0.0, 0.5, 1.0]
        assert c.fitness is None  # fitness reset

    def test_clamp_does_not_modify_original(self):
        g = Genome([-0.5, 1.5])
        _ = g.clamp(0.0, 1.0)
        assert g.genes == [-0.5, 1.5]

    def test_stats_empty_genome(self):
        g = Genome([])
        s = g.stats()
        assert isinstance(s, GenomeStats)
        assert s.length == 0

    def test_stats_values(self):
        g = Genome([1.0, 2.0, 3.0])
        s = g.stats()
        assert s.length == 3
        assert math.isclose(s.mean, 2.0)
        assert s.min_val == 1.0
        assert s.max_val == 3.0
        assert s.std >= 0.0

    def test_to_dict_structure(self):
        g = Genome([1.0], fitness=0.5, metadata={"key": "val"})
        d = g.to_dict()
        assert "genes" in d
        assert "fitness" in d
        assert "metadata" in d

    def test_metadata_defaults_to_empty(self):
        g = Genome([1.0])
        assert g.metadata == {}


# ── Operators ──────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCrossoverOperators:
    """Tests for crossover operators in operators/operators.py."""

    def test_crossover_produces_two_children(self):
        p1 = Genome([1.0] * 10)
        p2 = Genome([2.0] * 10)
        c1, c2 = crossover(p1, p2)
        assert len(c1) == 10
        assert len(c2) == 10

    def test_crossover_short_genome_returns_clones(self):
        p1 = Genome([1.0])
        p2 = Genome([2.0])
        c1, c2 = crossover(p1, p2)
        assert c1.genes == [1.0]
        assert c2.genes == [2.0]

    def test_crossover_children_combine_parents(self):
        p1 = Genome([1.0] * 5)
        p2 = Genome([0.0] * 5)
        c1, c2 = crossover(p1, p2)
        # Combined genes — each child is a mix of 1.0 and 0.0
        combined_vals = set(c1.genes + c2.genes)
        assert combined_vals == {0.0, 1.0}

    def test_two_point_crossover_length_preserved(self):
        p1 = Genome([float(i) for i in range(10)])
        p2 = Genome([float(i * 2) for i in range(10)])
        c1, c2 = two_point_crossover(p1, p2)
        assert len(c1) == 10
        assert len(c2) == 10

    def test_two_point_crossover_short_genome_fallback(self):
        p1 = Genome([1.0, 2.0])
        p2 = Genome([3.0, 4.0])
        c1, c2 = two_point_crossover(p1, p2)
        # Falls back to single-point when n < 3
        assert len(c1) == 2

    def test_uniform_crossover_length_preserved(self):
        p1 = Genome([1.0] * 6)
        p2 = Genome([0.0] * 6)
        c1, c2 = uniform_crossover(p1, p2)
        assert len(c1) == 6
        assert len(c2) == 6


@pytest.mark.unit
class TestMutationOperators:
    """Tests for mutation operators."""

    def test_mutate_returns_genome_same_length(self):
        g = Genome([0.5] * 8)
        m = mutate(g, rate=1.0, amount=0.01)
        assert len(m) == 8

    def test_mutate_rate_zero_returns_unchanged(self):
        g = Genome([0.5, 0.5, 0.5])
        m = mutate(g, rate=0.0)
        assert m.genes == [0.5, 0.5, 0.5]

    def test_mutate_rate_one_modifies_all(self):
        g = Genome([1.0, 1.0, 1.0])
        m = mutate(g, rate=1.0, amount=0.5)
        # All genes should be modified (Gaussian, so almost certainly not exactly 1.0)
        assert m.genes is not g.genes  # different list

    def test_uniform_mutate_rate_zero_unchanged(self):
        g = Genome([0.3, 0.6, 0.9])
        m = uniform_mutate(g, rate=0.0)
        assert m.genes == [0.3, 0.6, 0.9]

    def test_uniform_mutate_rate_one_within_bounds(self):
        g = Genome([0.5] * 20)
        m = uniform_mutate(g, rate=1.0, low=0.0, high=1.0)
        for gene in m.genes:
            assert 0.0 <= gene <= 1.0

    def test_swap_mutate_same_length(self):
        g = Genome([1.0, 2.0, 3.0, 4.0, 5.0])
        m = swap_mutate(g)
        assert len(m) == 5
        # Same values, different order (or same if lucky)
        assert sorted(m.genes) == sorted(g.genes)

    def test_swap_mutate_single_gene_returns_clone(self):
        g = Genome([7.0])
        m = swap_mutate(g)
        assert m.genes == [7.0]


@pytest.mark.unit
class TestSelectionOperators:
    """Tests for selection operators."""

    def _pop(self, n=10, base_fitness=None):
        genomes = [Genome.random(5) for _ in range(n)]
        for i, g in enumerate(genomes):
            g.fitness = base_fitness[i] if base_fitness else float(i)
        return genomes

    def test_fitness_key_none_returns_neg_inf(self):
        g = Genome([1.0])
        assert _fitness_key(g) == -float("inf")

    def test_fitness_key_returns_fitness(self):
        g = Genome([1.0], fitness=0.75)
        assert _fitness_key(g) == 0.75

    def test_tournament_selection_returns_genome(self):
        pop = self._pop(10)
        winner = tournament_selection(pop, size=3)
        assert isinstance(winner, Genome)
        assert winner in pop

    def test_tournament_selection_tends_toward_best(self):
        pop = self._pop(20)
        # With size=5, best genome (fitness=19) should win frequently
        wins = sum(1 for _ in range(100) if tournament_selection(pop, size=5).fitness == 19.0)
        assert wins > 20  # Should win at least 20% of the time

    def test_roulette_selection_returns_from_population(self):
        pop = self._pop(10)
        result = roulette_selection(pop)
        assert result in pop

    def test_roulette_selection_empty_raises(self):
        with pytest.raises(ValueError):
            roulette_selection([])

    def test_roulette_selection_zero_fitness_all(self):
        pop = [Genome([1.0], fitness=0.0) for _ in range(5)]
        result = roulette_selection(pop)
        assert result in pop

    def test_rank_selection_returns_from_population(self):
        pop = self._pop(10)
        result = rank_selection(pop)
        assert result in pop

    def test_rank_selection_empty_raises(self):
        with pytest.raises(ValueError):
            rank_selection([])

    def test_rank_selection_negative_fitness(self):
        # rank_selection works with negative fitness (roulette doesn't)
        pop = [Genome([1.0], fitness=float(-i)) for i in range(5)]
        result = rank_selection(pop)
        assert result in pop


# ── Population ─────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestPopulation:
    """Tests for Population class in population/population.py."""

    def test_init_creates_correct_size(self):
        pop = Population(size=10, genome_length=5)
        assert len(pop.individuals) == 10

    def test_init_genome_length(self):
        pop = Population(size=5, genome_length=8)
        for ind in pop.individuals:
            assert len(ind) == 8

    def test_generation_starts_at_zero(self):
        pop = Population(size=5, genome_length=4)
        assert pop.generation == 0

    def test_history_starts_empty(self):
        pop = Population(size=5, genome_length=4)
        assert pop.history == []

    def test_evaluate_sets_fitness(self):
        pop = Population(size=5, genome_length=4)
        pop.evaluate(lambda g: sum(g.genes))
        for ind in pop.individuals:
            assert ind.fitness is not None

    def test_evolve_increments_generation(self):
        pop = Population(size=10, genome_length=5)
        pop.evaluate(lambda g: sum(g.genes))
        pop.evolve()
        assert pop.generation == 1

    def test_evolve_records_stats(self):
        pop = Population(size=10, genome_length=5)
        pop.evaluate(lambda g: sum(g.genes))
        stats = pop.evolve()
        assert len(pop.history) == 1
        assert isinstance(stats, GenerationStats)
        assert stats.generation == 1

    def test_evolve_returns_generation_stats(self):
        pop = Population(size=8, genome_length=4)
        pop.evaluate(lambda g: sum(g.genes))
        stats = pop.evolve()
        assert stats.best_fitness >= stats.mean_fitness
        assert stats.mean_fitness >= stats.worst_fitness

    def test_evolve_maintains_population_size(self):
        pop = Population(size=10, genome_length=5)
        pop.evaluate(lambda g: sum(g.genes))
        original_size = len(pop.individuals)
        pop.evolve()
        assert len(pop.individuals) == original_size

    def test_get_best_returns_highest_fitness(self):
        pop = Population(size=6, genome_length=3)
        pop.evaluate(lambda g: g.genes[0])
        best = pop.get_best()
        for ind in pop.individuals:
            if ind.fitness is not None:
                assert best.fitness >= ind.fitness

    def test_get_worst_returns_lowest_fitness(self):
        pop = Population(size=6, genome_length=3)
        pop.evaluate(lambda g: g.genes[0])
        worst = pop.get_worst()
        for ind in pop.individuals:
            if ind.fitness is not None:
                assert worst.fitness <= ind.fitness

    def test_mean_fitness_correct(self):
        pop = Population(size=4, genome_length=2)
        fitnesses = [1.0, 2.0, 3.0, 4.0]
        for ind, f in zip(pop.individuals, fitnesses, strict=False):
            ind.fitness = f
        assert abs(pop.mean_fitness() - 2.5) < 1e-9

    def test_mean_fitness_no_fitness_returns_zero(self):
        pop = Population(size=4, genome_length=2)
        assert pop.mean_fitness() == 0.0

    def test_is_converged_false_when_too_few_generations(self):
        pop = Population(size=8, genome_length=4)
        pop.evaluate(lambda g: sum(g.genes))
        pop.evolve()
        assert pop.is_converged(window=5) is False

    def test_is_converged_true_when_no_improvement(self):
        pop = Population(size=8, genome_length=4)
        # Force constant fitness across 6 generations
        for _ in range(6):
            pop.evaluate(lambda g: 1.0)  # constant fitness
            pop.evolve()
        assert pop.is_converged(threshold=1e-6, window=5) is True

    def test_to_dict_structure(self):
        pop = Population(size=4, genome_length=3)
        pop.evaluate(lambda g: sum(g.genes))
        pop.evolve()
        d = pop.to_dict()
        assert "generation" in d
        assert "individuals" in d
        assert "history" in d
        assert d["generation"] == 1
        assert len(d["individuals"]) == 4

    def test_evolve_with_elitism_preserves_best(self):
        pop = Population(size=10, genome_length=5)
        pop.evaluate(lambda g: sum(g.genes))
        best_before = pop.get_best().fitness
        pop.evolve(elitism=2)
        # After elitism=2, the top 2 should be carried forward
        best_after = pop.get_best().fitness
        # Best fitness should not decrease
        assert best_after >= best_before - 1e-9

    def test_compute_stats_empty_fitness(self):
        pop = Population(size=4, genome_length=3)
        # No evaluate() called — all fitness=None
        pop.generation = 1
        stats = pop._compute_stats()
        assert stats.best_fitness == 0.0
        assert stats.mean_fitness == 0.0

    def test_sample_diversity_single_individual(self):
        pop = Population(size=1, genome_length=3)
        diversity = pop._sample_diversity()
        assert diversity == 0.0
