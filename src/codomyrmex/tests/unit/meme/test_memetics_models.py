"""Tests for meme.memetics.models."""

from codomyrmex.meme.memetics.models import (
    FitnessMap,
    Meme,
    Memeplex,
    MemeticCode,
    MemeType,
)


class TestMemeType:
    def test_all_values(self):
        values = {t.value for t in MemeType}
        assert "belief" in values
        assert "norm" in values
        assert "strategy" in values
        assert "narrative" in values
        assert "symbol" in values

    def test_str_enum_equals_string(self):
        assert MemeType.BELIEF == "belief"


class TestMeme:
    def test_construction(self):
        m = Meme(content="Evolution happens")
        assert m.content == "Evolution happens"
        assert m.meme_type == MemeType.BELIEF

    def test_id_auto_generated(self):
        m = Meme(content="test meme")
        assert len(m.id) == 16  # sha256 hex[:16]

    def test_id_provided(self):
        m = Meme(content="test", id="custom-id")
        assert m.id == "custom-id"

    def test_scores_clamped_high(self):
        m = Meme(content="t", fidelity=2.0, fecundity=2.0, longevity=2.0)
        assert m.fidelity == 1.0
        assert m.fecundity == 1.0
        assert m.longevity == 1.0

    def test_scores_clamped_low(self):
        m = Meme(content="t", fidelity=-1.0, fecundity=-5.0, longevity=-0.1)
        assert m.fidelity == 0.0
        assert m.fecundity == 0.0
        assert m.longevity == 0.0

    def test_fitness_geometric_mean(self):
        m = Meme(content="t", fidelity=1.0, fecundity=1.0, longevity=1.0)
        assert m.fitness == 1.0

    def test_fitness_zero_when_any_zero(self):
        m = Meme(content="t", fidelity=0.0, fecundity=0.8, longevity=0.9)
        assert m.fitness == 0.0

    def test_fitness_typical(self):
        m = Meme(content="t", fidelity=0.8, fecundity=0.5, longevity=0.5)
        expected = (0.8 * 0.5 * 0.5) ** (1 / 3)
        assert abs(m.fitness - expected) < 1e-9

    def test_descend_creates_child(self):
        parent = Meme(content="original")
        child = parent.descend("mutated")
        assert child.content == "mutated"
        assert parent.id in child.lineage

    def test_descend_inherits_properties(self):
        parent = Meme(content="original", fidelity=0.9, meme_type=MemeType.NORM)
        child = parent.descend("child")
        assert child.fidelity == 0.9
        assert child.meme_type == MemeType.NORM

    def test_descend_allows_overrides(self):
        parent = Meme(content="original", fidelity=0.9)
        child = parent.descend("child", fidelity=0.5)
        assert child.fidelity == 0.5

    def test_descend_lineage_chain(self):
        gp = Meme(content="grandparent")
        p = gp.descend("parent")
        c = p.descend("child")
        assert gp.id in c.lineage
        assert p.id in c.lineage

    def test_independent_default_lineage(self):
        m1 = Meme(content="a")
        m2 = Meme(content="b")
        m1.lineage.append("x")
        assert m2.lineage == []

    def test_created_at_is_set(self):
        m = Meme(content="t")
        assert m.created_at > 0


class TestMemeticCode:
    def test_empty_code(self):
        code = MemeticCode()
        assert code.length == 0
        assert code.aggregate_fitness == 0.0

    def test_append(self):
        code = MemeticCode()
        m = Meme(content="t")
        code.append(m)
        assert code.length == 1

    def test_splice_in(self):
        code = MemeticCode()
        m1 = Meme(content="a")
        m2 = Meme(content="b")
        code.append(m1)
        code.splice_in(0, m2)
        assert code.sequence[0] is m2
        assert code.sequence[1] is m1

    def test_excise(self):
        code = MemeticCode()
        m = Meme(content="t")
        code.append(m)
        removed = code.excise(0)
        assert removed is m
        assert code.length == 0

    def test_aggregate_fitness(self):
        code = MemeticCode()
        m1 = Meme(content="a", fidelity=1.0, fecundity=1.0, longevity=1.0)
        m2 = Meme(content="b", fidelity=0.5, fecundity=0.5, longevity=0.5)
        code.append(m1)
        code.append(m2)
        expected = (m1.fitness + m2.fitness) / 2
        assert abs(code.aggregate_fitness - expected) < 1e-9

    def test_independent_default_sequence(self):
        c1 = MemeticCode()
        c2 = MemeticCode()
        c1.append(Meme(content="x"))
        assert c2.length == 0


class TestMemeplex:
    def test_construction(self):
        mp = Memeplex(name="Western Values")
        assert mp.name == "Western Values"
        assert len(mp.id) == 16
        assert mp.synergy == 0.5

    def test_id_provided(self):
        mp = Memeplex(name="t", id="custom")
        assert mp.id == "custom"

    def test_synergy_clamped(self):
        mp = Memeplex(name="t", synergy=2.0)
        assert mp.synergy == 1.0
        mp2 = Memeplex(name="t", synergy=-1.0)
        assert mp2.synergy == 0.0

    def test_fitness_empty(self):
        mp = Memeplex(name="t")
        assert mp.fitness == 0.0

    def test_fitness_with_memes(self):
        m = Meme(content="t", fidelity=0.8, fecundity=0.5, longevity=0.5)
        mp = Memeplex(name="t", memes=[m], synergy=0.0)
        assert abs(mp.fitness - m.fitness * 1.0) < 1e-9

    def test_fitness_with_synergy(self):
        m = Meme(content="t", fidelity=1.0, fecundity=1.0, longevity=1.0)
        mp = Memeplex(name="t", memes=[m], synergy=0.5)
        assert mp.fitness == 1.0 * 1.5

    def test_robustness_single_meme(self):
        m = Meme(content="t")
        mp = Memeplex(name="t", memes=[m])
        assert mp.robustness_score() == 1.0

    def test_robustness_empty(self):
        mp = Memeplex(name="t")
        assert mp.robustness_score() == 1.0

    def test_robustness_uniform_is_1(self):
        memes = [
            Meme(content="t", fidelity=0.8, fecundity=0.5, longevity=0.5),
            Meme(content="t", fidelity=0.8, fecundity=0.5, longevity=0.5),
        ]
        mp = Memeplex(name="t", memes=memes)
        score = mp.robustness_score()
        assert score > 0.99  # Perfectly uniform → robustness ≈ 1

    def test_mutate_returns_new_memeplex(self):
        m = Meme(content="original", fidelity=0.8, fecundity=0.5, longevity=0.5)
        mp = Memeplex(name="base", memes=[m])
        # Use mutation_rate=1.0 to guarantee mutation
        mutant = mp.mutate(mutation_rate=1.0)
        assert mutant.name == "base_mutant"
        assert len(mutant.memes) == 1
        assert (
            mutant.memes[0].content != "original"
            or "[mutated]" in mutant.memes[0].content
        )

    def test_recombine_empty(self):
        mp1 = Memeplex(name="a")
        mp2 = Memeplex(name="b")
        child = mp1.recombine(mp2)
        assert child.memes == []

    def test_recombine_produces_child(self):
        m1 = Meme(content="a")
        m2 = Meme(content="b")
        mp1 = Memeplex(name="mp1", memes=[m1])
        mp2 = Memeplex(name="mp2", memes=[m2])
        child = mp1.recombine(mp2)
        assert "mp1xmp2" in child.name
        assert child.synergy == (mp1.synergy + mp2.synergy) / 2

    def test_independent_default_memes(self):
        mp1 = Memeplex(name="a")
        mp2 = Memeplex(name="b")
        mp1.memes.append(Meme(content="x"))
        assert len(mp2.memes) == 0


class TestFitnessMap:
    def test_empty(self):
        fm = FitnessMap()
        assert fm.mean_fitness == 0.0
        assert fm.max_fitness == 0.0
        assert fm.min_fitness == 0.0

    def test_add_entry(self):
        fm = FitnessMap()
        fm.add("m1", 0.8)
        assert fm.entries["m1"] == 0.8

    def test_mean_fitness(self):
        fm = FitnessMap()
        fm.add("a", 0.6)
        fm.add("b", 0.4)
        assert abs(fm.mean_fitness - 0.5) < 1e-9

    def test_max_fitness(self):
        fm = FitnessMap()
        fm.add("a", 0.3)
        fm.add("b", 0.9)
        assert fm.max_fitness == 0.9

    def test_min_fitness(self):
        fm = FitnessMap()
        fm.add("a", 0.3)
        fm.add("b", 0.9)
        assert fm.min_fitness == 0.3

    def test_top_n(self):
        fm = FitnessMap()
        fm.add("low", 0.1)
        fm.add("mid", 0.5)
        fm.add("high", 0.9)
        top2 = fm.top_n(2)
        assert len(top2) == 2
        assert top2[0][0] == "high"
        assert top2[1][0] == "mid"

    def test_top_n_larger_than_entries(self):
        fm = FitnessMap()
        fm.add("a", 0.5)
        top = fm.top_n(10)
        assert len(top) == 1

    def test_timestamp_set(self):
        fm = FitnessMap()
        assert fm.timestamp > 0

    def test_independent_default_entries(self):
        fm1 = FitnessMap()
        fm2 = FitnessMap()
        fm1.add("x", 1.0)
        assert fm2.entries == {}
