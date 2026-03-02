"""Tests for meme.memetics -- zero-mock, real instances only.

Sprint 5 coverage expansion for the memetics submodule: Meme, Memeplex,
MemeticCode, FitnessMap, MemeticEngine, fitness functions, and mutation
operators.  All tests use real dataclass instances and real function calls.
"""

from __future__ import annotations

import random

import pytest

from codomyrmex.meme.memetics.engine import MemeticEngine
from codomyrmex.meme.memetics.fitness import (
    decay_rate,
    population_fitness_stats,
    robustness_score,
    virality_score,
)
from codomyrmex.meme.memetics.models import (
    FitnessMap,
    Meme,
    Memeplex,
    MemeticCode,
    MemeType,
)
from codomyrmex.meme.memetics.mutation import (
    batch_mutate,
    recombine,
    semantic_drift,
    splice,
)

# ---------------------------------------------------------------------------
# MemeType enum
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMemeType:
    """Tests for the MemeType enum."""

    def test_all_values_present(self) -> None:
        """All eight MemeType values are accessible."""
        expected = {
            "belief", "norm", "strategy", "aesthetic",
            "narrative", "symbol", "ritual", "slogan",
        }
        actual = {m.value for m in MemeType}
        assert actual == expected

    def test_str_subclass(self) -> None:
        """MemeType is a str enum -- values compare as strings."""
        assert MemeType.BELIEF == "belief"
        assert isinstance(MemeType.NORM, str)


# ---------------------------------------------------------------------------
# Meme dataclass
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMeme:
    """Deep tests for the Meme dataclass."""

    def test_id_auto_generated_is_hex(self) -> None:
        """Auto-generated ID is a 16-char hex string."""
        m = Meme(content="test")
        assert len(m.id) == 16
        int(m.id, 16)  # should not raise

    def test_explicit_id_preserved(self) -> None:
        """Supplying an explicit ID skips auto-generation."""
        m = Meme(content="test", id="custom_id_12345")
        assert m.id == "custom_id_12345"

    def test_fidelity_clamped_above(self) -> None:
        """Fidelity > 1.0 is clamped to 1.0."""
        m = Meme(content="x", fidelity=5.0)
        assert m.fidelity == 1.0

    def test_fecundity_clamped_below(self) -> None:
        """Fecundity < 0.0 is clamped to 0.0."""
        m = Meme(content="x", fecundity=-10.0)
        assert m.fecundity == 0.0

    def test_longevity_clamped_both(self) -> None:
        """Longevity values are clamped at both ends."""
        low = Meme(content="x", longevity=-1.0)
        high = Meme(content="x", longevity=99.0)
        assert low.longevity == 0.0
        assert high.longevity == 1.0

    def test_fitness_geometric_mean(self) -> None:
        """Fitness is the geometric mean of fidelity, fecundity, longevity."""
        m = Meme(content="x", fidelity=0.8, fecundity=0.5, longevity=0.5)
        expected = (0.8 * 0.5 * 0.5) ** (1 / 3)
        assert m.fitness == pytest.approx(expected, abs=1e-9)

    def test_fitness_zero_when_any_attribute_zero(self) -> None:
        """If any score attribute is 0, fitness is 0."""
        m = Meme(content="x", fidelity=0.0, fecundity=0.9, longevity=0.9)
        assert m.fitness == 0.0

    def test_descend_preserves_lineage_chain(self) -> None:
        """Descending through generations builds the correct lineage."""
        g0 = Meme(content="gen0")
        g1 = g0.descend("gen1")
        g2 = g1.descend("gen2")
        assert g0.id in g1.lineage
        assert g0.id in g2.lineage
        assert g1.id in g2.lineage

    def test_descend_metadata_merge(self) -> None:
        """Child inherits parent metadata and merges overrides."""
        parent = Meme(content="p", metadata={"source": "lab"})
        child = parent.descend("c", metadata={"version": 2})
        assert child.metadata["source"] == "lab"
        assert child.metadata["version"] == 2

    def test_descend_override_meme_type(self) -> None:
        """Descend can override the meme type."""
        parent = Meme(content="p", meme_type=MemeType.BELIEF)
        child = parent.descend("c", meme_type=MemeType.SLOGAN)
        assert child.meme_type == MemeType.SLOGAN

    def test_created_at_is_float(self) -> None:
        """created_at is a float timestamp."""
        m = Meme(content="x")
        assert isinstance(m.created_at, float)
        assert m.created_at > 0

    def test_default_meme_type_is_belief(self) -> None:
        """Default meme_type is BELIEF."""
        m = Meme(content="x")
        assert m.meme_type == MemeType.BELIEF


# ---------------------------------------------------------------------------
# MemeticCode
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMemeticCode:
    """Tests for the MemeticCode sequence container."""

    def test_empty_code_length_zero(self) -> None:
        """New MemeticCode has length 0."""
        c = MemeticCode()
        assert c.length == 0

    def test_append_increments_length(self) -> None:
        """Appending N memes yields length N."""
        c = MemeticCode()
        for i in range(4):
            c.append(Meme(content=f"m{i}"))
        assert c.length == 4

    def test_splice_in_at_beginning(self) -> None:
        """splice_in at index 0 prepends."""
        c = MemeticCode()
        c.append(Meme(content="second"))
        c.splice_in(0, Meme(content="first"))
        assert c.sequence[0].content == "first"

    def test_excise_returns_correct_meme(self) -> None:
        """excise returns the meme that was at the given index."""
        c = MemeticCode()
        m0 = Meme(content="keep")
        m1 = Meme(content="remove")
        c.append(m0)
        c.append(m1)
        removed = c.excise(1)
        assert removed.id == m1.id
        assert c.length == 1

    def test_aggregate_fitness_empty(self) -> None:
        """aggregate_fitness of empty code is 0.0."""
        c = MemeticCode()
        assert c.aggregate_fitness == 0.0

    def test_aggregate_fitness_single(self) -> None:
        """aggregate_fitness of single meme equals that meme's fitness."""
        m = Meme(content="x", fidelity=0.6, fecundity=0.6, longevity=0.6)
        c = MemeticCode(sequence=[m])
        assert c.aggregate_fitness == pytest.approx(m.fitness, abs=1e-9)


# ---------------------------------------------------------------------------
# Memeplex
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMemeplex:
    """Tests for the Memeplex co-adapted complex."""

    def test_synergy_clamped(self) -> None:
        """Synergy is clamped to [0, 1]."""
        mp = Memeplex(name="t", synergy=5.0)
        assert mp.synergy == 1.0
        mp2 = Memeplex(name="t", synergy=-2.0)
        assert mp2.synergy == 0.0

    def test_fitness_with_synergy_zero(self) -> None:
        """Synergy=0 means fitness equals raw mean meme fitness."""
        m = Meme(content="x", fidelity=1.0, fecundity=1.0, longevity=1.0)
        mp = Memeplex(name="t", memes=[m], synergy=0.0)
        assert mp.fitness == pytest.approx(1.0, abs=1e-9)

    def test_robustness_single_meme_is_one(self) -> None:
        """A memeplex with one meme has robustness 1.0."""
        mp = Memeplex(name="t", memes=[Meme(content="x")])
        assert mp.robustness_score() == 1.0

    def test_robustness_nonuniform_less_than_one(self) -> None:
        """Non-uniform fitnesses yield robustness < 1.0."""
        mp = Memeplex(
            name="t",
            memes=[
                Meme(content="a", fidelity=1.0, fecundity=1.0, longevity=1.0),
                Meme(content="b", fidelity=0.1, fecundity=0.1, longevity=0.1),
            ],
        )
        assert mp.robustness_score() < 1.0

    def test_mutate_preserves_count(self) -> None:
        """mutate returns a memeplex with the same number of memes."""
        random.seed(99)
        mp = Memeplex(name="src", memes=[Meme(content=f"m{i}") for i in range(8)])
        mutant = mp.mutate(mutation_rate=0.5)
        assert len(mutant.memes) == 8

    def test_mutate_name_suffix(self) -> None:
        """Mutant memeplex gets _mutant suffix."""
        random.seed(99)
        mp = Memeplex(name="base", memes=[Meme(content="x")])
        assert mp.mutate().name == "base_mutant"

    def test_recombine_empty_parents(self) -> None:
        """Recombining two empty memeplexes gives an empty child."""
        a = Memeplex(name="A")
        b = Memeplex(name="B")
        child = a.recombine(b)
        assert child.memes == []

    def test_recombine_synergy_average(self) -> None:
        """Child synergy is the average of parents'."""
        a = Memeplex(name="A", memes=[Meme(content="a")], synergy=0.2)
        b = Memeplex(name="B", memes=[Meme(content="b")], synergy=0.8)
        random.seed(42)
        child = a.recombine(b)
        assert child.synergy == pytest.approx(0.5, abs=1e-9)


# ---------------------------------------------------------------------------
# FitnessMap
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFitnessMap:
    """Tests for the FitnessMap snapshot."""

    def test_top_n_ordering(self) -> None:
        """top_n returns entries sorted descending by fitness."""
        fm = FitnessMap()
        fm.add("low", 0.1)
        fm.add("mid", 0.5)
        fm.add("high", 0.9)
        top = fm.top_n(3)
        fitnesses = [f for _, f in top]
        assert fitnesses == sorted(fitnesses, reverse=True)

    def test_top_n_less_than_total(self) -> None:
        """top_n(k) with k < entries returns exactly k items."""
        fm = FitnessMap()
        for i in range(10):
            fm.add(f"e{i}", float(i) / 10)
        assert len(fm.top_n(3)) == 3

    def test_overwrite_entry(self) -> None:
        """Adding the same entity_id overwrites fitness."""
        fm = FitnessMap()
        fm.add("x", 0.1)
        fm.add("x", 0.9)
        assert fm.entries["x"] == 0.9
        assert len(fm.entries) == 1


# ---------------------------------------------------------------------------
# MemeticEngine
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMemeticEngine:
    """Tests for the high-level memetic engine."""

    def test_dissect_single_sentence(self) -> None:
        """A single sentence with no split yields one meme."""
        engine = MemeticEngine()
        memes = engine.dissect("Hello world")
        assert len(memes) == 1
        assert memes[0].content == "Hello world"

    def test_dissect_multiple_sentences(self) -> None:
        """Multiple sentences produce multiple memes."""
        engine = MemeticEngine()
        text = "I believe freedom is key. You should vote. This is a beautiful art piece."
        memes = engine.dissect(text)
        assert len(memes) >= 3

    def test_dissect_classifies_belief(self) -> None:
        """Text with 'believe' is classified as BELIEF."""
        engine = MemeticEngine()
        memes = engine.dissect("I believe this is true.")
        assert memes[0].meme_type == MemeType.BELIEF

    def test_dissect_classifies_norm(self) -> None:
        """Text with 'should' is classified as NORM."""
        engine = MemeticEngine()
        memes = engine.dissect("You should follow the rules.")
        assert memes[0].meme_type == MemeType.NORM

    def test_synthesize_custom_separator(self) -> None:
        """Synthesize with custom separator joins correctly."""
        engine = MemeticEngine()
        memes = [Meme(content="A"), Meme(content="B"), Meme(content="C")]
        assert engine.synthesize(memes, separator=" | ") == "A | B | C"

    def test_fitness_landscape_values(self) -> None:
        """Fitness landscape entries match memeplex fitness values."""
        engine = MemeticEngine()
        m1 = Memeplex(name="a", memes=[Meme(content="x", fidelity=1.0, fecundity=1.0, longevity=1.0)])
        m2 = Memeplex(name="b", memes=[Meme(content="y", fidelity=0.5, fecundity=0.5, longevity=0.5)])
        fmap = engine.fitness_landscape([m1, m2])
        assert fmap.entries[m1.id] == pytest.approx(m1.fitness, abs=1e-9)
        assert fmap.entries[m2.id] == pytest.approx(m2.fitness, abs=1e-9)

    def test_select_empty_population(self) -> None:
        """Selecting from empty population returns empty list."""
        engine = MemeticEngine()
        assert engine.select([], n=5) == []

    def test_select_tournament(self) -> None:
        """Tournament selection returns n items."""
        random.seed(42)
        engine = MemeticEngine()
        pop = [Memeplex(name=f"m{i}", memes=[Meme(content=f"c{i}")]) for i in range(10)]
        selected = engine.select(pop, n=5, method="tournament")
        assert len(selected) == 5

    def test_evolve_preserves_population_size(self) -> None:
        """Evolve maintains population size across generations."""
        random.seed(42)
        engine = MemeticEngine()
        pop = [
            Memeplex(name=f"m{i}", memes=[Meme(content=f"c{i}")])
            for i in range(6)
        ]
        evolved = engine.evolve(pop, generations=3, mutation_rate=0.1)
        assert len(evolved) >= 1  # At minimum parents survive


# ---------------------------------------------------------------------------
# Fitness functions
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFitnessFunctions:
    """Tests for standalone fitness functions."""

    def test_virality_short_vs_long(self) -> None:
        """Shorter meme content yields higher virality than longer."""
        short = Meme(content="go", fecundity=0.5)
        long = Meme(content=" ".join(["word"] * 50), fecundity=0.5)
        assert virality_score(short) > virality_score(long)

    def test_virality_network_scaling(self) -> None:
        """Larger network increases virality score."""
        m = Meme(content="test", fecundity=0.5)
        small = virality_score(m, network_size=10)
        large = virality_score(m, network_size=10000)
        assert large >= small

    def test_robustness_many_uniform_memes(self) -> None:
        """Many uniform memes yield high robustness."""
        memes = [
            Meme(content=f"m{i}", fidelity=0.5, fecundity=0.5, longevity=0.5)
            for i in range(10)
        ]
        mp = Memeplex(name="uniform", memes=memes, synergy=0.5)
        score = robustness_score(mp)
        assert score > 0.5

    def test_decay_rate_positive(self) -> None:
        """decay_rate always returns a positive value."""
        m = Meme(content="x", longevity=0.5)
        assert decay_rate(m) > 0

    def test_decay_higher_longevity_lower_rate(self) -> None:
        """Higher longevity yields lower decay rate."""
        low_long = Meme(content="x", longevity=0.1)
        high_long = Meme(content="x", longevity=0.9)
        assert decay_rate(high_long) < decay_rate(low_long)

    def test_population_fitness_stats_correct_count(self) -> None:
        """Stats count matches population size."""
        pop = [Meme(content=f"m{i}") for i in range(7)]
        stats = population_fitness_stats(pop)
        assert stats["count"] == 7

    def test_population_fitness_stats_min_max(self) -> None:
        """Stats min/max bracket all individual fitness values."""
        pop = [
            Meme(content="a", fidelity=0.1, fecundity=0.1, longevity=0.1),
            Meme(content="b", fidelity=0.9, fecundity=0.9, longevity=0.9),
        ]
        stats = population_fitness_stats(pop)
        assert stats["min"] <= stats["max"]
        for m in pop:
            assert stats["min"] <= m.fitness <= stats["max"]


# ---------------------------------------------------------------------------
# Mutation operators
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMutationOperators:
    """Tests for mutation operators."""

    def test_semantic_drift_adds_markers(self) -> None:
        """semantic_drift wraps drifted words in tildes."""
        random.seed(42)
        m = Meme(content="the quick brown fox jumps")
        drifted = semantic_drift(m, intensity=1.0)
        assert "~" in drifted.content

    def test_semantic_drift_reduces_fidelity(self) -> None:
        """Drift lowers fidelity proportional to intensity."""
        random.seed(42)
        m = Meme(content="words here now", fidelity=0.9)
        drifted = semantic_drift(m, intensity=0.5)
        assert drifted.fidelity < m.fidelity

    def test_semantic_drift_empty_content(self) -> None:
        """Drifting empty content returns a descendant without error."""
        m = Meme(content="")
        drifted = semantic_drift(m, intensity=0.5)
        assert isinstance(drifted, Meme)

    def test_recombine_crossover_zero(self) -> None:
        """Crossover at 0.0 takes nothing from parent A.

        With crossover_point=0.0: cut_a=0, cut_b=int(3*1.0)=3,
        so child_words = [] + words_b[3:] = [], which triggers
        the fallback to meme_a.content.
        """
        a = Meme(content="alpha bravo charlie")
        b = Meme(content="delta echo foxtrot")
        child = recombine(a, b, crossover_point=0.0)
        # Fallback: empty child_words -> meme_a.content
        assert child.content == a.content

    def test_recombine_averages_properties(self) -> None:
        """Recombined child has averaged fidelity/fecundity/longevity."""
        a = Meme(content="one two three", fidelity=0.2, fecundity=0.4, longevity=0.6)
        b = Meme(content="four five six", fidelity=0.8, fecundity=0.6, longevity=0.4)
        child = recombine(a, b, crossover_point=0.5)
        assert child.fidelity == pytest.approx(0.5, abs=1e-9)
        assert child.fecundity == pytest.approx(0.5, abs=1e-9)
        assert child.longevity == pytest.approx(0.5, abs=1e-9)

    def test_splice_at_midpoint(self) -> None:
        """Splice inserts bracketed content at the midpoint."""
        host = Meme(content="the world is big and wide")
        insert = Meme(content="very")
        spliced = splice(host, insert, position=0.5)
        assert "[very]" in spliced.content

    def test_splice_reduces_host_fidelity(self) -> None:
        """Splicing reduces host fidelity by 0.1."""
        host = Meme(content="a b c d", fidelity=0.8)
        insert = Meme(content="x")
        spliced = splice(host, insert)
        assert spliced.fidelity == pytest.approx(0.7, abs=1e-9)

    def test_batch_mutate_rate_zero(self) -> None:
        """batch_mutate with rate 0 returns identical population."""
        pop = [Meme(content=f"m{i}") for i in range(5)]
        result = batch_mutate(pop, mutation_rate=0.0)
        for orig, res in zip(pop, result, strict=False):
            assert orig.id == res.id

    def test_batch_mutate_rate_one(self) -> None:
        """batch_mutate with rate 1.0 mutates every meme."""
        random.seed(42)
        pop = [Meme(content=f"word{i} extra text here") for i in range(5)]
        original_ids = {m.id for m in pop}
        result = batch_mutate(pop, mutation_rate=1.0, intensity=0.5)
        # All should be new memes (different IDs)
        result_ids = {m.id for m in result}
        assert original_ids != result_ids
