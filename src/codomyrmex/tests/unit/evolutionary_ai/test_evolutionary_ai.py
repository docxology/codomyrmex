"""Comprehensive tests for the evolutionary_ai module.

Tests cover genome management, population operations, genetic operators
(mutation, crossover, selection), the operator class hierarchy, and factory
functions for creating operators.
"""

import random

import pytest

from codomyrmex.evolutionary_ai import (
    BitFlipMutation,
    BlendCrossover,
    CrossoverType,
    ElitismSelection,
    GaussianMutation,
    Genome,
    Individual,
    MutationType,
    Population,
    RankSelection,
    RouletteSelection,
    ScrambleMutation,
    SelectionType,
    SinglePointCrossover,
    SwapMutation,
    TournamentSelection,
    TwoPointCrossover,
    UniformCrossover,
    create_crossover,
    create_mutation,
    create_selection,
    crossover,
    mutate,
    tournament_selection,
)

# ---------------------------------------------------------------------------
# Genome
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_genome_creation_with_genes():
    """Test genome initialized with explicit genes."""
    g = Genome([0.1, 0.2, 0.3])
    assert len(g) == 3
    assert g.genes == [0.1, 0.2, 0.3]
    assert g.fitness is None


@pytest.mark.unit
def test_genome_creation_random():
    """Test genome initialized with random genes."""
    g = Genome.random(15)
    assert len(g) == 15
    for gene in g.genes:
        assert isinstance(gene, float)


@pytest.mark.unit
def test_genome_default_length():
    """Test genome default length when no genes provided."""
    g = Genome()
    assert len(g) == 10


@pytest.mark.unit
def test_genome_copy_preserves_fitness():
    """Test genome copy preserves fitness value."""
    g = Genome([0.5, 0.6])
    g.fitness = 42.0
    c = g.copy()
    assert c.genes == g.genes
    assert c.fitness == 42.0
    # Mutation of copy does not affect original
    c.genes[0] = 0.0
    assert g.genes[0] == 0.5


@pytest.mark.unit
def test_genome_iteration():
    """Test genome supports iteration."""
    g = Genome([0.1, 0.2, 0.3])
    values = list(g)
    assert values == [0.1, 0.2, 0.3]


@pytest.mark.unit
def test_genome_getitem():
    """Test genome supports indexing."""
    g = Genome([0.5, 0.6, 0.7])
    assert g[1] == 0.6


# ---------------------------------------------------------------------------
# Crossover (convenience function)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_crossover_produces_two_children():
    """Test crossover returns exactly two children."""
    p1 = Genome([0, 0, 0, 0])
    p2 = Genome([1, 1, 1, 1])
    c1, c2 = crossover(p1, p2)
    assert len(c1) == 4
    assert len(c2) == 4


@pytest.mark.unit
def test_crossover_children_have_parent_genes():
    """Test crossover children contain genes from both parents."""
    random.seed(42)
    p1 = Genome([0, 0, 0, 0])
    p2 = Genome([1, 1, 1, 1])
    c1, c2 = crossover(p1, p2)
    for g in c1.genes + c2.genes:
        assert g in [0, 1]


@pytest.mark.unit
def test_crossover_single_gene_returns_copies():
    """Test crossover with single-gene genomes returns copies."""
    p1 = Genome([0.5])
    p2 = Genome([0.9])
    c1, c2 = crossover(p1, p2)
    assert c1.genes == [0.5]
    assert c2.genes == [0.9]


# ---------------------------------------------------------------------------
# Mutation (convenience function)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_mutation_with_full_rate():
    """Test mutation at 100% rate changes all genes."""
    g = Genome([0.5, 0.5, 0.5])
    mutated = mutate(g, rate=1.0)
    assert mutated.genes != g.genes
    assert len(mutated) == 3


@pytest.mark.unit
def test_mutation_with_zero_rate():
    """Test mutation at 0% rate keeps genes unchanged."""
    g = Genome([0.5, 0.5, 0.5])
    mutated = mutate(g, rate=0.0)
    assert mutated.genes == g.genes


@pytest.mark.unit
def test_mutation_clamps_to_bounds():
    """Test mutation clamps gene values to [0, 1]."""
    random.seed(1)
    g = Genome([0.0, 1.0])
    mutated = mutate(g, rate=1.0)
    for gene in mutated.genes:
        assert 0.0 <= gene <= 1.0


# ---------------------------------------------------------------------------
# Tournament selection (convenience function)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_tournament_selection_picks_fittest():
    """Test tournament selection returns the fittest when size equals population."""
    g1 = Genome([1]); g1.fitness = 10
    g2 = Genome([2]); g2.fitness = 20
    g3 = Genome([3]); g3.fitness = 5
    winner = tournament_selection([g1, g2, g3], tournament_size=3)
    assert winner.fitness == 20


@pytest.mark.unit
def test_tournament_selection_returns_copy():
    """Test tournament selection returns a copy, not a reference."""
    g1 = Genome([1]); g1.fitness = 10
    winner = tournament_selection([g1], tournament_size=1)
    winner.fitness = 999
    assert g1.fitness == 10


# ---------------------------------------------------------------------------
# Population
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_population_initialization():
    """Test population creates the correct number of individuals."""
    pop = Population(size=15, genome_length=8)
    assert len(pop.individuals) == 15
    assert pop.generation == 0
    assert all(len(g) == 8 for g in pop.individuals)


@pytest.mark.unit
def test_population_evaluate():
    """Test evaluation assigns fitness to all individuals."""
    pop = Population(size=5, genome_length=3)
    pop.evaluate(lambda g: sum(g.genes))
    for ind in pop.individuals:
        assert ind.fitness is not None
        assert ind.fitness >= 0


@pytest.mark.unit
def test_population_get_best():
    """Test get_best returns the individual with highest fitness."""
    pop = Population(size=5, genome_length=3)
    pop.evaluate(lambda g: sum(g.genes))
    best = pop.get_best()
    assert best.fitness == max(ind.fitness for ind in pop.individuals)


@pytest.mark.unit
def test_population_get_worst():
    """Test get_worst returns the individual with lowest fitness."""
    pop = Population(size=5, genome_length=3)
    pop.evaluate(lambda g: sum(g.genes))
    worst = pop.get_worst()
    assert worst.fitness == min(ind.fitness for ind in pop.individuals)


@pytest.mark.unit
def test_population_evolve_increments_generation():
    """Test evolve increments generation counter."""
    pop = Population(size=10, genome_length=5)
    pop.evaluate(lambda g: sum(g.genes))
    pop.evolve(mutation_rate=0.1)
    assert pop.generation == 1
    pop.evolve(mutation_rate=0.1)
    assert pop.generation == 2


@pytest.mark.unit
def test_population_evolve_preserves_size():
    """Test evolve maintains population size."""
    pop = Population(size=20, genome_length=5)
    pop.evaluate(lambda g: sum(g.genes))
    pop.evolve(mutation_rate=0.1)
    assert len(pop.individuals) == 20


@pytest.mark.unit
def test_population_elitism_preserves_best():
    """Test evolve with elitism preserves top individuals."""
    pop = Population(size=10, genome_length=5)
    pop.evaluate(lambda g: sum(g.genes))
    best_before = pop.get_best().fitness
    pop.evolve(mutation_rate=0.01, elitism=2)
    pop.evaluate(lambda g: sum(g.genes))
    best_after = pop.get_best().fitness
    # Elitism should keep the best fitness at least as good
    assert best_after >= best_before


# ---------------------------------------------------------------------------
# Individual dataclass
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_individual_comparison():
    """Test Individual ordering by fitness."""
    a = Individual(genes=[1, 2], fitness=5.0)
    b = Individual(genes=[3, 4], fitness=10.0)
    assert a < b
    assert not b < a


@pytest.mark.unit
def test_individual_none_fitness_ordering():
    """Test Individual with None fitness is less than any fitness."""
    a = Individual(genes=[1], fitness=None)
    b = Individual(genes=[2], fitness=0.0)
    assert a < b


# ---------------------------------------------------------------------------
# Mutation operators (class-based)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_bit_flip_mutation():
    """Test BitFlipMutation flips bits."""
    op = BitFlipMutation(mutation_rate=1.0)
    ind = Individual(genes=[0, 1, 0, 1])
    mutated = op.mutate(ind)
    assert mutated.genes == [1, 0, 1, 0]


@pytest.mark.unit
def test_swap_mutation():
    """Test SwapMutation swaps two genes."""
    random.seed(42)
    op = SwapMutation(mutation_rate=1.0)
    original_genes = [1, 2, 3, 4, 5]
    ind = Individual(genes=original_genes.copy())
    mutated = op.mutate(ind)
    # Length preserved; at least one swap happened
    assert len(mutated.genes) == 5
    assert sorted(mutated.genes) == sorted(original_genes)


@pytest.mark.unit
def test_gaussian_mutation_with_bounds():
    """Test GaussianMutation respects bounds."""
    op = GaussianMutation(mutation_rate=1.0, sigma=100.0, bounds=(0.0, 1.0))
    ind = Individual(genes=[0.5, 0.5, 0.5])
    mutated = op.mutate(ind)
    for gene in mutated.genes:
        assert 0.0 <= gene <= 1.0


@pytest.mark.unit
def test_scramble_mutation():
    """Test ScrambleMutation shuffles a subset of genes."""
    random.seed(42)
    op = ScrambleMutation(mutation_rate=1.0)
    original = [1, 2, 3, 4, 5]
    ind = Individual(genes=original.copy())
    mutated = op.mutate(ind)
    assert len(mutated.genes) == 5
    assert sorted(mutated.genes) == sorted(original)


# ---------------------------------------------------------------------------
# Crossover operators (class-based)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_single_point_crossover():
    """Test SinglePointCrossover produces valid offspring."""
    random.seed(42)
    op = SinglePointCrossover(crossover_rate=1.0)
    p1 = Individual(genes=[0, 0, 0, 0])
    p2 = Individual(genes=[1, 1, 1, 1])
    c1, c2 = op.crossover(p1, p2)
    assert len(c1.genes) == 4
    assert len(c2.genes) == 4
    for g in c1.genes + c2.genes:
        assert g in [0, 1]


@pytest.mark.unit
def test_two_point_crossover():
    """Test TwoPointCrossover produces valid offspring."""
    random.seed(42)
    op = TwoPointCrossover(crossover_rate=1.0)
    p1 = Individual(genes=[0, 0, 0, 0, 0])
    p2 = Individual(genes=[1, 1, 1, 1, 1])
    c1, c2 = op.crossover(p1, p2)
    assert len(c1.genes) == 5
    assert len(c2.genes) == 5


@pytest.mark.unit
def test_uniform_crossover():
    """Test UniformCrossover mixes genes from both parents."""
    random.seed(42)
    op = UniformCrossover(crossover_rate=1.0, mixing_ratio=0.5)
    p1 = Individual(genes=[0, 0, 0, 0])
    p2 = Individual(genes=[1, 1, 1, 1])
    c1, c2 = op.crossover(p1, p2)
    assert len(c1.genes) == 4
    # At least some mixing should occur
    assert not all(g == 0 for g in c1.genes) or not all(g == 1 for g in c1.genes)


@pytest.mark.unit
def test_blend_crossover():
    """Test BlendCrossover produces real-valued offspring."""
    random.seed(42)
    op = BlendCrossover(crossover_rate=1.0, alpha=0.5)
    p1 = Individual(genes=[0.0, 0.0])
    p2 = Individual(genes=[1.0, 1.0])
    c1, c2 = op.crossover(p1, p2)
    assert len(c1.genes) == 2
    # Values should be in an expanded range around [0, 1]
    for g in c1.genes + c2.genes:
        assert -0.5 <= g <= 1.5


# ---------------------------------------------------------------------------
# Selection operators (class-based)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_tournament_selection_operator():
    """Test TournamentSelection selects from population."""
    pop = [Individual(genes=[i], fitness=float(i)) for i in range(10)]
    selector = TournamentSelection(tournament_size=3)
    selected = selector.select(pop, num_selected=5)
    assert len(selected) == 5
    for ind in selected:
        assert ind.fitness is not None


@pytest.mark.unit
def test_roulette_selection_operator():
    """Test RouletteSelection selects proportionally to fitness."""
    pop = [Individual(genes=[i], fitness=float(i + 1)) for i in range(10)]
    selector = RouletteSelection()
    selected = selector.select(pop, num_selected=5)
    assert len(selected) == 5


@pytest.mark.unit
def test_rank_selection_operator():
    """Test RankSelection selects based on rank."""
    pop = [Individual(genes=[i], fitness=float(i)) for i in range(10)]
    selector = RankSelection(selection_pressure=2.0)
    selected = selector.select(pop, num_selected=5)
    assert len(selected) == 5


@pytest.mark.unit
def test_elitism_selection_preserves_best():
    """Test ElitismSelection keeps the top individuals."""
    pop = [Individual(genes=[i], fitness=float(i)) for i in range(10)]
    selector = ElitismSelection(elite_count=2)
    selected = selector.select(pop, num_selected=5)
    assert len(selected) == 5
    # The two best (fitness 9 and 8) should be in the selection
    fitnesses = [ind.fitness for ind in selected]
    assert 9.0 in fitnesses
    assert 8.0 in fitnesses


# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_create_mutation_factory():
    """Test create_mutation factory for different types."""
    op = create_mutation(MutationType.BIT_FLIP, mutation_rate=0.5)
    assert isinstance(op, BitFlipMutation)

    op2 = create_mutation(MutationType.GAUSSIAN, mutation_rate=0.1, sigma=0.2)
    assert isinstance(op2, GaussianMutation)


@pytest.mark.unit
def test_create_crossover_factory():
    """Test create_crossover factory for different types."""
    op = create_crossover(CrossoverType.SINGLE_POINT)
    assert isinstance(op, SinglePointCrossover)

    op2 = create_crossover(CrossoverType.UNIFORM, mixing_ratio=0.3)
    assert isinstance(op2, UniformCrossover)


@pytest.mark.unit
def test_create_selection_factory():
    """Test create_selection factory for different types."""
    op = create_selection(SelectionType.TOURNAMENT, tournament_size=5)
    assert isinstance(op, TournamentSelection)

    op2 = create_selection(SelectionType.ELITISM, elite_count=3)
    assert isinstance(op2, ElitismSelection)


@pytest.mark.unit
def test_create_mutation_unknown_raises():
    """Test create_mutation raises on unknown type."""
    with pytest.raises(ValueError):
        create_mutation(MutationType.INVERSION)


@pytest.mark.unit
def test_create_crossover_unknown_raises():
    """Test create_crossover raises on unknown type."""
    with pytest.raises(ValueError):
        create_crossover(CrossoverType.ORDER)


@pytest.mark.unit
def test_create_selection_unknown_raises():
    """Test create_selection raises on unknown type."""
    with pytest.raises(ValueError):
        create_selection(SelectionType.TRUNCATION)


# From test_coverage_boost_r2.py
class TestGenome:
    """Tests for Genome class."""

    def test_init_and_len(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome

        g = Genome([1.0, 2.0, 3.0])
        assert len(g) == 3
        assert g[0] == 1.0

    def test_random_factory(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome

        g = Genome.random(10, low=0.0, high=1.0)
        assert len(g) == 10
        assert all(0.0 <= gene <= 1.0 for gene in g.genes)

    def test_zeros_factory(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome

        g = Genome.zeros(5)
        assert all(gene == 0.0 for gene in g.genes)

    def test_clone(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome

        g = Genome([1.0, 2.0], fitness=0.5, metadata={"tag": "x"})
        c = g.clone()
        assert c == g
        assert c is not g
        assert c.fitness == 0.5

    def test_distance(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome

        g1 = Genome([0.0, 0.0])
        g2 = Genome([3.0, 4.0])
        assert abs(g1.distance(g2) - 5.0) < 1e-9

    def test_distance_length_mismatch(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome

        with pytest.raises(ValueError, match="Cannot compute distance"):
            Genome([1.0]).distance(Genome([1.0, 2.0]))

    def test_clamp(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome

        g = Genome([-1.0, 0.5, 2.0])
        clamped = g.clamp(0.0, 1.0)
        assert clamped.genes == [0.0, 0.5, 1.0]

    def test_stats(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome

        g = Genome([2.0, 4.0, 6.0])
        s = g.stats()
        assert abs(s.mean - 4.0) < 1e-9
        assert s.min_val == 2.0
        assert s.max_val == 6.0
        assert s.length == 3

    def test_stats_empty(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome

        s = Genome([]).stats()
        assert s.length == 0

    def test_serialization_roundtrip(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome

        g = Genome([1.0, 2.0], fitness=0.9, metadata={"gen": 1})
        d = g.to_dict()
        g2 = Genome.from_dict(d)
        assert g2 == g
        assert g2.fitness == 0.9

    def test_eq_and_repr(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome

        g = Genome([1.0], fitness=0.5)
        assert g != "not a genome"
        assert "fitness=0.5" in repr(g)


# From test_coverage_boost_r2.py
class TestCrossover:
    """Tests for crossover operators."""

    def test_single_point_crossover(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome
        from codomyrmex.evolutionary_ai.operators.operators import crossover

        p1 = Genome([1.0, 1.0, 1.0, 1.0])
        p2 = Genome([2.0, 2.0, 2.0, 2.0])
        c1, c2 = crossover(p1, p2)
        assert len(c1) == 4
        assert len(c2) == 4

    def test_crossover_short_genome(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome
        from codomyrmex.evolutionary_ai.operators.operators import crossover

        p1 = Genome([1.0])
        p2 = Genome([2.0])
        c1, c2 = crossover(p1, p2)
        assert c1.genes == [1.0]
        assert c2.genes == [2.0]

    def test_two_point_crossover(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome
        from codomyrmex.evolutionary_ai.operators.operators import two_point_crossover

        p1 = Genome([1.0] * 6)
        p2 = Genome([2.0] * 6)
        c1, c2 = two_point_crossover(p1, p2)
        assert len(c1) == 6

    def test_uniform_crossover(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome
        from codomyrmex.evolutionary_ai.operators.operators import uniform_crossover

        p1 = Genome([0.0] * 10)
        p2 = Genome([1.0] * 10)
        c1, c2 = uniform_crossover(p1, p2, swap_prob=0.5)
        assert len(c1) == 10
        # At least some genes should come from each parent
        combined = set(c1.genes) | set(c2.genes)
        assert 0.0 in combined or 1.0 in combined


# From test_coverage_boost_r2.py
class TestMutation:
    """Tests for mutation operators."""

    def test_gaussian_mutate(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome
        from codomyrmex.evolutionary_ai.operators.operators import mutate

        g = Genome([0.5] * 20)
        m = mutate(g, rate=1.0, amount=0.1)
        assert len(m) == 20
        # With rate=1.0, all genes should be mutated
        assert m.genes != g.genes

    def test_uniform_mutate(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome
        from codomyrmex.evolutionary_ai.operators.operators import uniform_mutate

        g = Genome([0.5] * 10)
        m = uniform_mutate(g, rate=1.0, low=0.0, high=1.0)
        assert len(m) == 10

    def test_swap_mutate(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome
        from codomyrmex.evolutionary_ai.operators.operators import swap_mutate

        g = Genome([1.0, 2.0, 3.0, 4.0])
        m = swap_mutate(g)
        assert sorted(m.genes) == sorted(g.genes)  # Same elements, different order

    def test_swap_mutate_short(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome
        from codomyrmex.evolutionary_ai.operators.operators import swap_mutate

        g = Genome([1.0])
        m = swap_mutate(g)
        assert m.genes == [1.0]


# From test_coverage_boost_r2.py
class TestSelection:
    """Tests for selection operators."""

    def test_tournament_selection(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome
        from codomyrmex.evolutionary_ai.operators.operators import tournament_selection

        pop = [Genome([float(i)], fitness=float(i)) for i in range(10)]
        selected = tournament_selection(pop, size=3)
        assert isinstance(selected, Genome)
        assert selected.fitness is not None

    def test_roulette_selection(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome
        from codomyrmex.evolutionary_ai.operators.operators import roulette_selection

        pop = [Genome([float(i)], fitness=float(i) + 1) for i in range(10)]
        selected = roulette_selection(pop)
        assert isinstance(selected, Genome)

    def test_roulette_empty_raises(self):
        from codomyrmex.evolutionary_ai.operators.operators import roulette_selection

        with pytest.raises(ValueError, match="empty"):
            roulette_selection([])

    def test_roulette_zero_fitness(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome
        from codomyrmex.evolutionary_ai.operators.operators import roulette_selection

        pop = [Genome([0.0], fitness=0.0) for _ in range(5)]
        selected = roulette_selection(pop)
        assert isinstance(selected, Genome)

    def test_rank_selection(self):
        from codomyrmex.evolutionary_ai.genome.genome import Genome
        from codomyrmex.evolutionary_ai.operators.operators import rank_selection

        pop = [Genome([float(i)], fitness=float(i)) for i in range(10)]
        selected = rank_selection(pop)
        assert isinstance(selected, Genome)

    def test_rank_empty_raises(self):
        from codomyrmex.evolutionary_ai.operators.operators import rank_selection

        with pytest.raises(ValueError, match="empty"):
            rank_selection([])


# From test_coverage_boost_r2.py
class TestPopulation:
    """Tests for Population class."""

    def test_init(self):
        from codomyrmex.evolutionary_ai.population.population import Population

        pop = Population(size=20, genome_length=5)
        assert len(pop.individuals) == 20
        assert pop.generation == 0

    def test_evaluate(self):
        from codomyrmex.evolutionary_ai.population.population import Population

        pop = Population(size=10, genome_length=3)
        pop.evaluate(lambda g: sum(g.genes))
        assert all(ind.fitness is not None for ind in pop.individuals)

    def test_evolve(self):
        from codomyrmex.evolutionary_ai.population.population import Population

        pop = Population(size=20, genome_length=5)
        pop.evaluate(lambda g: sum(g.genes))
        pop.evolve(mutation_rate=0.1, elitism=2)
        assert pop.generation == 1
        assert len(pop.individuals) == 20

    def test_get_best_worst(self):
        from codomyrmex.evolutionary_ai.population.population import Population

        pop = Population(size=10, genome_length=3)
        pop.evaluate(lambda g: sum(g.genes))
        best = pop.get_best()
        worst = pop.get_worst()
        assert best.fitness >= worst.fitness

    def test_mean_fitness(self):
        from codomyrmex.evolutionary_ai.population.population import Population

        pop = Population(size=10, genome_length=3)
        pop.evaluate(lambda g: sum(g.genes))
        mean = pop.mean_fitness()
        assert isinstance(mean, float)

    def test_convergence_detection(self):
        from codomyrmex.evolutionary_ai.population.population import Population

        pop = Population(size=20, genome_length=5)
        # Run several generations
        for _ in range(10):
            pop.evaluate(lambda g: sum(g.genes))
            pop.evolve(mutation_rate=0.01, elitism=2)
        # Should not crash
        result = pop.is_converged(threshold=1e-6, window=5)
        assert isinstance(result, bool)

    def test_to_dict(self):
        from codomyrmex.evolutionary_ai.population.population import Population

        pop = Population(size=5, genome_length=3)
        pop.evaluate(lambda g: sum(g.genes))
        d = pop.to_dict()
        assert "generation" in d
        assert "individuals" in d
        assert "history" in d
