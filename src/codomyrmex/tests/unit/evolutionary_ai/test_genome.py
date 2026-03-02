"""
Unit tests for evolutionary_ai.genome — Zero-Mock compliant.

Covers: BinaryGenome (random/copy/to_list/__len__/flip),
RealValuedGenome (random/copy/to_list/__len__/clip),
PermutationGenome (random/from_elements/copy/to_list/__len__/swap).
"""

import pytest

from codomyrmex.evolutionary_ai.genome import (
    BinaryGenome,
    PermutationGenome,
    RealValuedGenome,
)

# ── BinaryGenome ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestBinaryGenome:
    def test_random_correct_length(self):
        g = BinaryGenome.random(10)
        assert len(g.bits) == 10

    def test_random_only_zero_or_one(self):
        g = BinaryGenome.random(50)
        assert all(b in (0, 1) for b in g.bits)

    def test_len_reflects_bits(self):
        g = BinaryGenome(bits=[1, 0, 1])
        assert len(g) == 3

    def test_to_list_returns_copy(self):
        g = BinaryGenome(bits=[1, 0, 1])
        lst = g.to_list()
        assert lst == [1, 0, 1]
        lst.append(99)
        # Mutating the list should not affect the genome
        assert len(g.bits) == 3

    def test_copy_returns_equal_genome(self):
        g = BinaryGenome(bits=[1, 0, 0, 1])
        g2 = g.copy()
        assert g2.bits == g.bits

    def test_copy_is_independent(self):
        g = BinaryGenome(bits=[1, 0, 0, 1])
        g2 = g.copy()
        g2.bits[0] = 0
        assert g.bits[0] == 1  # original unchanged

    def test_flip_toggles_bit(self):
        g = BinaryGenome(bits=[0, 1, 0])
        g.flip(0)
        assert g.bits[0] == 1

    def test_flip_zero_to_one(self):
        g = BinaryGenome(bits=[0, 0, 0])
        g.flip(1)
        assert g.bits[1] == 1

    def test_flip_one_to_zero(self):
        g = BinaryGenome(bits=[1, 1, 1])
        g.flip(2)
        assert g.bits[2] == 0


# ── RealValuedGenome ──────────────────────────────────────────────────


@pytest.mark.unit
class TestRealValuedGenome:
    def test_random_correct_length(self):
        g = RealValuedGenome.random(5)
        assert len(g.values) == 5

    def test_random_values_within_bounds(self):
        g = RealValuedGenome.random(20, lower=-1.0, upper=1.0)
        assert all(-1.0 <= v <= 1.0 for v in g.values)

    def test_random_default_bounds(self):
        g = RealValuedGenome.random(10)
        assert all(0.0 <= v <= 1.0 for v in g.values)

    def test_random_sets_lower_bounds(self):
        g = RealValuedGenome.random(3, lower=-5.0, upper=5.0)
        assert g.lower_bounds == [-5.0, -5.0, -5.0]

    def test_random_sets_upper_bounds(self):
        g = RealValuedGenome.random(3, lower=-5.0, upper=5.0)
        assert g.upper_bounds == [5.0, 5.0, 5.0]

    def test_len_reflects_values(self):
        g = RealValuedGenome(values=[1.0, 2.0, 3.0])
        assert len(g) == 3

    def test_to_list_returns_copy(self):
        g = RealValuedGenome(values=[1.0, 2.0])
        lst = g.to_list()
        assert lst == [1.0, 2.0]
        lst.append(99.0)
        assert len(g.values) == 2

    def test_copy_equals_original(self):
        g = RealValuedGenome(values=[1.0, 2.0], lower_bounds=[0.0, 0.0])
        g2 = g.copy()
        assert g2.values == g.values

    def test_copy_is_independent(self):
        g = RealValuedGenome(values=[1.0, 2.0])
        g2 = g.copy()
        g2.values[0] = 99.0
        assert g.values[0] == 1.0

    def test_copy_with_none_bounds(self):
        g = RealValuedGenome(values=[1.0])
        g2 = g.copy()
        assert g2.lower_bounds is None
        assert g2.upper_bounds is None

    def test_clip_clamps_values_within_bounds(self):
        g = RealValuedGenome(
            values=[5.0, -5.0, 0.5],
            lower_bounds=[0.0, 0.0, 0.0],
            upper_bounds=[1.0, 1.0, 1.0],
        )
        g.clip()
        assert g.values[0] == pytest.approx(1.0)
        assert g.values[1] == pytest.approx(0.0)
        assert g.values[2] == pytest.approx(0.5)

    def test_clip_no_bounds_unchanged(self):
        g = RealValuedGenome(values=[1000.0, -1000.0])
        g.clip()
        assert g.values[0] == 1000.0
        assert g.values[1] == -1000.0


# ── PermutationGenome ─────────────────────────────────────────────────


@pytest.mark.unit
class TestPermutationGenome:
    def test_random_correct_length(self):
        g = PermutationGenome.random(5)
        assert len(g.elements) == 5

    def test_random_is_permutation(self):
        g = PermutationGenome.random(6)
        assert sorted(g.elements) == list(range(6))

    def test_from_elements_stores_elements(self):
        g = PermutationGenome.from_elements(["a", "b", "c"])
        assert g.elements == ["a", "b", "c"]

    def test_from_elements_is_copy(self):
        source = [1, 2, 3]
        g = PermutationGenome.from_elements(source)
        source.append(4)
        assert len(g.elements) == 3

    def test_len_reflects_elements(self):
        g = PermutationGenome(elements=[0, 1, 2, 3])
        assert len(g) == 4

    def test_to_list_returns_copy(self):
        g = PermutationGenome(elements=[0, 1, 2])
        lst = g.to_list()
        assert lst == [0, 1, 2]
        lst.append(99)
        assert len(g.elements) == 3

    def test_copy_equals_original(self):
        g = PermutationGenome(elements=[2, 0, 1])
        g2 = g.copy()
        assert g2.elements == g.elements

    def test_copy_is_independent(self):
        g = PermutationGenome(elements=[0, 1, 2])
        g2 = g.copy()
        g2.elements[0] = 99
        assert g.elements[0] == 0

    def test_swap_exchanges_elements(self):
        g = PermutationGenome(elements=[0, 1, 2, 3])
        g.swap(0, 3)
        assert g.elements[0] == 3
        assert g.elements[3] == 0

    def test_swap_maintains_all_elements(self):
        g = PermutationGenome(elements=[0, 1, 2, 3])
        g.swap(1, 2)
        assert sorted(g.elements) == [0, 1, 2, 3]
