"""
Unit tests for evolutionary_ai.operators — Zero-Mock compliant.
"""

import pytest

from codomyrmex.evolutionary_ai.genome.genome import Individual
from codomyrmex.evolutionary_ai.operators.operators import (
    BitFlipMutation,
    BlendCrossover,
    GaussianMutation,
    ScrambleMutation,
    SinglePointCrossover,
    SwapMutation,
    TwoPointCrossover,
    UniformCrossover,
)


@pytest.mark.unit
class TestMutationOperators:
    def test_bit_flip_mutation(self):
        mut = BitFlipMutation(mutation_rate=1.0)
        ind = Individual(genes=[0, 1, 0, 1])
        mutated = mut.mutate(ind)
        assert mutated.genes == [1, 0, 1, 0]
        assert mutated is not ind

    def test_swap_mutation(self):
        mut = SwapMutation(mutation_rate=1.0)
        ind = Individual(genes=[1, 2, 3])
        mutated = mut.mutate(ind)
        assert len(mutated.genes) == 3
        assert sorted(mutated.genes) == [1, 2, 3]

    def test_gaussian_mutation(self):
        mut = GaussianMutation(mutation_rate=1.0, sigma=0.1, bounds=(0.0, 1.0))
        ind = Individual(genes=[0.5, 0.5, 0.5])
        mutated = mut.mutate(ind)
        assert all(0.0 <= g <= 1.0 for g in mutated.genes)
        assert mutated.genes != [0.5, 0.5, 0.5]

    def test_scramble_mutation(self):
        mut = ScrambleMutation(mutation_rate=1.0)
        ind = Individual(genes=list(range(10)))
        mutated = mut.mutate(ind)
        assert len(mutated.genes) == 10
        assert sorted(mutated.genes) == list(range(10))


@pytest.mark.unit
class TestCrossoverOperators:
    def test_single_point_crossover(self):
        cross = SinglePointCrossover(crossover_rate=1.0)
        p1 = Individual(genes=[0, 0, 0, 0])
        p2 = Individual(genes=[1, 1, 1, 1])
        c1, _c2 = cross.crossover(p1, p2)

        # Verify crossover happened at some point
        found_point = False
        for i in range(1, 4):
            if c1.genes[:i] == [0] * i and c1.genes[i:] == [1] * (4 - i):
                found_point = True
                break
        assert found_point

    def test_two_point_crossover(self):
        cross = TwoPointCrossover(crossover_rate=1.0)
        p1 = Individual(genes=[0] * 10)
        p2 = Individual(genes=[1] * 10)
        c1, c2 = cross.crossover(p1, p2)
        assert len(c1.genes) == 10
        assert len(c2.genes) == 10
        assert any(g == 0 for g in c1.genes)
        assert any(g == 1 for g in c1.genes)

    def test_uniform_crossover(self):
        cross = UniformCrossover(crossover_rate=1.0, mixing_ratio=0.5)
        p1 = Individual(genes=[0] * 100)
        p2 = Individual(genes=[1] * 100)
        c1, _c2 = cross.crossover(p1, p2)
        # Statistics: approximately 50/50
        zeros = sum(1 for g in c1.genes if g == 0)
        ones = sum(1 for g in c1.genes if g == 1)
        assert zeros + ones == 100
        assert 30 < zeros < 70

    def test_blend_crossover(self):
        cross = BlendCrossover(crossover_rate=1.0, alpha=0.5)
        p1 = Individual(genes=[10.0, 10.0])
        p2 = Individual(genes=[20.0, 20.0])
        c1, c2 = cross.crossover(p1, p2)
        # Range with alpha=0.5 is [10 - 0.5*10, 20 + 0.5*10] = [5, 25]
        for g in c1.genes + c2.genes:
            assert 5.0 <= g <= 25.0

    def test_no_crossover_if_rate_zero(self):
        cross = SinglePointCrossover(crossover_rate=0.0)
        p1 = Individual(genes=[0, 0])
        p2 = Individual(genes=[1, 1])
        c1, c2 = cross.crossover(p1, p2)
        assert c1.genes == [0, 0]
        assert c2.genes == [1, 1]
