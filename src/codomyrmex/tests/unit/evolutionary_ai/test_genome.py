"""
Unit tests for evolutionary_ai.genome — Zero-Mock compliant.
"""

import math

import pytest

from codomyrmex.evolutionary_ai.genome.genome import (
    Genome,
    Individual,
)


@pytest.mark.unit
class TestIndividual:
    def test_individual_init(self):
        ind = Individual(genes=[1, 2, 3], fitness=10.5, metadata={"id": "test"})
        assert ind.genes == [1, 2, 3]
        assert ind.fitness == 10.5
        assert ind.metadata == {"id": "test"}

    def test_individual_comparison(self):
        ind1 = Individual(genes=[1], fitness=10.0)
        ind2 = Individual(genes=[2], fitness=20.0)
        ind3 = Individual(genes=[3], fitness=None)

        assert ind1 < ind2
        assert not (ind2 < ind1)
        assert ind3 < ind1
        assert not (ind1 < ind3)
        assert not (ind3 < ind3)

    def test_individual_equality(self):
        ind1 = Individual(genes=[1, 2, 3])
        ind2 = Individual(genes=[1, 2, 3])
        ind3 = Individual(genes=[1, 2, 4])

        assert ind1 == ind2
        assert ind1 != ind3
        assert ind1 != "not an individual"

@pytest.mark.unit
class TestGenome:
    def test_genome_random(self):
        g = Genome.random(length=10, low=0.0, high=1.0)
        assert len(g) == 10
        assert all(0.0 <= x <= 1.0 for x in g.genes)

    def test_genome_zeros(self):
        g = Genome.zeros(length=5)
        assert g.genes == [0.0] * 5

    def test_genome_clone(self):
        g1 = Genome(genes=[0.1, 0.2], fitness=0.5, metadata={"a": 1})
        g2 = g1.clone()

        assert g1 == g2
        assert g1.fitness == g2.fitness
        assert g1.metadata == g2.metadata

        # Verify independence
        g2.genes[0] = 0.9
        g2.metadata["a"] = 2
        assert g1.genes[0] == 0.1
        assert g1.metadata["a"] == 1

    def test_genome_distance(self):
        g1 = Genome(genes=[0.0, 0.0])
        g2 = Genome(genes=[3.0, 4.0])
        assert g1.distance(g2) == pytest.approx(5.0)

    def test_genome_distance_error(self):
        g1 = Genome(genes=[0.0])
        g2 = Genome(genes=[0.0, 0.0])
        with pytest.raises(ValueError, match="Cannot compute distance"):
            g1.distance(g2)

    def test_genome_clamp(self):
        g = Genome(genes=[-1.0, 0.5, 2.0])
        clamped = g.clamp(low=0.0, high=1.0)
        assert clamped.genes == [0.0, 0.5, 1.0]
        assert clamped.fitness is None

    def test_genome_stats(self):
        g = Genome(genes=[1.0, 2.0, 3.0])
        stats = g.stats()
        assert stats.mean == 2.0
        assert stats.min_val == 1.0
        assert stats.max_val == 3.0
        assert stats.length == 3
        assert stats.std == pytest.approx(math.sqrt(2/3))

    def test_genome_stats_empty(self):
        g = Genome(genes=[])
        stats = g.stats()
        assert stats.length == 0
        assert stats.mean == 0.0

    def test_genome_serialization(self):
        g1 = Genome(genes=[0.1, 0.2], fitness=0.8, metadata={"m": "data"})
        data = g1.to_dict()
        g2 = Genome.from_dict(data)

        assert g1 == g2
        assert g1.fitness == g2.fitness
        assert g1.metadata == g2.metadata

    def test_genome_dunders(self):
        g = Genome(genes=[1.0, 2.0, 3.0])
        assert len(g) == 3
        assert g[1] == 2.0
        assert "Genome" in repr(g)
