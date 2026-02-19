"""Comprehensive tests for the meme module.

Tests cover the core memetics engine (Meme, Memeplex, MemeticCode, FitnessMap),
semiotic analysis (Sign, SignType, SemioticAnalyzer, DriftReport),
narrative structures (Narrative, NarrativeArc, NarrativeEngine),
contagion models, cultural dynamics, and swarm intelligence.
"""

import importlib
import math
import random

import pytest

from codomyrmex.meme import (
    Meme,
    Memeplex,
    MemeticCode,
    FitnessMap,
    MemeticEngine,
    Sign,
    SignType,
    DriftReport,
    SemioticAnalyzer,
    Narrative,
    NarrativeArc,
    Archetype,
    NarrativeEngine,
    ContagionModel,
    CascadeType,
    Cascade,
    PropagationTrace,
    ResonanceMap,
    CulturalState,
    CulturalDynamicsEngine,
    PowerMap,
)
from codomyrmex.meme.memetics.mutation import semantic_drift, recombine, splice
from codomyrmex.meme.memetics.fitness import (
    virality_score,
    robustness_score,
    decay_rate,
    population_fitness_stats,
)
from codomyrmex.meme.narrative.structure import (
    heros_journey_arc,
    freytag_pyramid_arc,
    fichtean_curve_arc,
)


# ---------------------------------------------------------------------------
# Module imports
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_meme_module_importable():
    """Verify that the meme module can be explicitly imported."""
    from codomyrmex import meme
    assert meme is not None


@pytest.mark.unit
def test_meme_submodules_exist():
    """Verify that key submodules are importable."""
    submodules = [
        "codomyrmex.meme.memetics",
        "codomyrmex.meme.semiotic",
        "codomyrmex.meme.contagion",
        "codomyrmex.meme.narrative",
        "codomyrmex.meme.cultural_dynamics",
        "codomyrmex.meme.swarm",
        "codomyrmex.meme.neurolinguistic",
        "codomyrmex.meme.ideoscape",
        "codomyrmex.meme.rhizome",
        "codomyrmex.meme.epistemic",
        "codomyrmex.meme.hyperreality",
        "codomyrmex.meme.cybernetic",
    ]
    for module_name in submodules:
        mod = importlib.import_module(module_name)
        assert mod is not None, f"Failed to import {module_name}"


# ---------------------------------------------------------------------------
# Meme
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_meme_creation():
    """Test Meme creation with default values."""
    meme = Meme(content="The earth is round.")
    assert meme.content == "The earth is round."
    assert meme.id  # auto-generated
    assert 0.0 <= meme.fidelity <= 1.0
    assert 0.0 <= meme.fecundity <= 1.0
    assert 0.0 <= meme.longevity <= 1.0


@pytest.mark.unit
def test_meme_fitness_property():
    """Test Meme fitness is geometric mean of attributes."""
    meme = Meme(content="test", fidelity=1.0, fecundity=1.0, longevity=1.0)
    assert meme.fitness == 1.0

    meme2 = Meme(content="test", fidelity=0.0, fecundity=0.5, longevity=0.5)
    assert meme2.fitness == 0.0  # Any zero makes geometric mean zero


@pytest.mark.unit
def test_meme_clamping():
    """Test Meme clamps values to [0, 1]."""
    meme = Meme(content="test", fidelity=2.0, fecundity=-0.5, longevity=0.5)
    assert meme.fidelity == 1.0
    assert meme.fecundity == 0.0


@pytest.mark.unit
def test_meme_descend():
    """Test Meme descend creates a child with lineage."""
    parent = Meme(content="original idea")
    child = parent.descend("mutated idea")
    assert child.content == "mutated idea"
    assert parent.id in child.lineage


@pytest.mark.unit
def test_meme_unique_ids():
    """Test Memes get unique IDs."""
    m1 = Meme(content="idea one")
    m2 = Meme(content="idea two")
    assert m1.id != m2.id


# ---------------------------------------------------------------------------
# MemeticCode
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_memetic_code_append():
    """Test MemeticCode append and length."""
    code = MemeticCode()
    assert code.length == 0
    code.append(Meme(content="meme-1"))
    code.append(Meme(content="meme-2"))
    assert code.length == 2


@pytest.mark.unit
def test_memetic_code_splice_in():
    """Test MemeticCode splice_in inserts at position."""
    code = MemeticCode()
    code.append(Meme(content="first"))
    code.append(Meme(content="third"))
    code.splice_in(1, Meme(content="second"))
    assert code.sequence[1].content == "second"
    assert code.length == 3


@pytest.mark.unit
def test_memetic_code_excise():
    """Test MemeticCode excise removes and returns meme."""
    code = MemeticCode()
    code.append(Meme(content="keep"))
    code.append(Meme(content="remove"))
    removed = code.excise(1)
    assert removed.content == "remove"
    assert code.length == 1


@pytest.mark.unit
def test_memetic_code_aggregate_fitness():
    """Test MemeticCode aggregate_fitness is mean."""
    code = MemeticCode()
    assert code.aggregate_fitness == 0.0
    code.append(Meme(content="a", fidelity=1.0, fecundity=1.0, longevity=1.0))
    assert code.aggregate_fitness == 1.0


# ---------------------------------------------------------------------------
# Memeplex
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_memeplex_creation():
    """Test Memeplex creation."""
    m = Memeplex(name="democracy", memes=[
        Meme(content="freedom of speech"),
        Meme(content="voting rights"),
    ])
    assert m.name == "democracy"
    assert len(m.memes) == 2
    assert m.id  # auto-generated


@pytest.mark.unit
def test_memeplex_fitness():
    """Test Memeplex fitness includes synergy bonus."""
    m = Memeplex(
        name="test",
        memes=[Meme(content="a", fidelity=1.0, fecundity=1.0, longevity=1.0)],
        synergy=0.5,
    )
    # fitness = mean_fitness * (1 + synergy) = 1.0 * 1.5 = 1.5
    assert m.fitness == 1.5


@pytest.mark.unit
def test_memeplex_empty_fitness():
    """Test Memeplex with no memes has zero fitness."""
    m = Memeplex(name="empty")
    assert m.fitness == 0.0


@pytest.mark.unit
def test_memeplex_robustness():
    """Test Memeplex robustness_score for uniform memes."""
    m = Memeplex(
        name="uniform",
        memes=[
            Meme(content="a", fidelity=0.5, fecundity=0.5, longevity=0.5),
            Meme(content="b", fidelity=0.5, fecundity=0.5, longevity=0.5),
        ],
    )
    # Uniform fitnesses => robustness should be 1.0 (perfect uniformity)
    assert m.robustness_score() == 1.0


@pytest.mark.unit
def test_memeplex_mutate():
    """Test Memeplex mutate produces a new memeplex."""
    random.seed(42)
    m = Memeplex(
        name="original",
        memes=[Meme(content="idea") for _ in range(5)],
    )
    mutant = m.mutate(mutation_rate=1.0)
    assert mutant.name == "original_mutant"
    assert len(mutant.memes) == 5


@pytest.mark.unit
def test_memeplex_recombine():
    """Test Memeplex recombine produces offspring."""
    random.seed(42)
    a = Memeplex(name="A", memes=[Meme(content="a1"), Meme(content="a2")])
    b = Memeplex(name="B", memes=[Meme(content="b1"), Meme(content="b2")])
    child = a.recombine(b)
    assert "A" in child.name and "B" in child.name


# ---------------------------------------------------------------------------
# FitnessMap
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_fitness_map_operations():
    """Test FitnessMap add, mean, max, min, top_n."""
    fm = FitnessMap()
    fm.add("a", 0.5)
    fm.add("b", 1.0)
    fm.add("c", 0.2)
    assert fm.mean_fitness == pytest.approx((0.5 + 1.0 + 0.2) / 3, abs=1e-6)
    assert fm.max_fitness == 1.0
    assert fm.min_fitness == 0.2
    top = fm.top_n(2)
    assert top[0] == ("b", 1.0)


@pytest.mark.unit
def test_fitness_map_empty():
    """Test FitnessMap with no entries."""
    fm = FitnessMap()
    assert fm.mean_fitness == 0.0
    assert fm.max_fitness == 0.0


# ---------------------------------------------------------------------------
# MemeticEngine
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_memetic_engine_dissect():
    """Test MemeticEngine dissect breaks text into memes."""
    engine = MemeticEngine()
    memes = engine.dissect("I believe this is true. You should do your duty.")
    assert len(memes) >= 2
    # Check types are assigned
    for m in memes:
        assert m.meme_type is not None


@pytest.mark.unit
def test_memetic_engine_synthesize():
    """Test MemeticEngine synthesize joins memes."""
    engine = MemeticEngine()
    memes = [Meme(content="Hello"), Meme(content="world")]
    text = engine.synthesize(memes)
    assert text == "Hello world"


@pytest.mark.unit
def test_memetic_engine_fitness_landscape():
    """Test MemeticEngine fitness_landscape computes map."""
    engine = MemeticEngine()
    pop = [
        Memeplex(name="A", memes=[Meme(content="a")]),
        Memeplex(name="B", memes=[Meme(content="b")]),
    ]
    fmap = engine.fitness_landscape(pop)
    assert len(fmap.entries) == 2


@pytest.mark.unit
def test_memetic_engine_select_truncation():
    """Test MemeticEngine truncation selection."""
    engine = MemeticEngine()
    pop = [
        Memeplex(name=f"m{i}", memes=[Meme(content=f"c{i}", fidelity=0.1 * i, fecundity=0.1 * i, longevity=0.1 * i)])
        for i in range(1, 6)
    ]
    selected = engine.select(pop, n=2, method="truncation")
    assert len(selected) == 2
    # Should be the two fittest
    assert selected[0].fitness >= selected[1].fitness


# ---------------------------------------------------------------------------
# Mutation functions
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_semantic_drift():
    """Test semantic_drift modifies meme content."""
    random.seed(42)
    meme = Meme(content="ideas spread through culture quickly")
    drifted = semantic_drift(meme, intensity=0.5)
    assert drifted.content != meme.content
    assert drifted.fidelity < meme.fidelity


@pytest.mark.unit
def test_recombine_memes():
    """Test recombine produces offspring from two parent memes."""
    a = Meme(content="the sky is blue today")
    b = Meme(content="water flows downhill always")
    child = recombine(a, b, crossover_point=0.5)
    assert child.content  # Should have some content
    assert a.id in child.lineage or b.id in child.lineage


@pytest.mark.unit
def test_splice_memes():
    """Test splice inserts one meme's content into another."""
    host = Meme(content="the world is big")
    insert = Meme(content="very")
    spliced = splice(host, insert, position=0.5)
    assert "[very]" in spliced.content


# ---------------------------------------------------------------------------
# Fitness functions
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_virality_score():
    """Test virality_score is in [0, 1]."""
    meme = Meme(content="short catchy phrase", fecundity=0.9)
    score = virality_score(meme, network_size=10000)
    assert 0.0 <= score <= 1.0


@pytest.mark.unit
def test_robustness_score_func():
    """Test robustness_score function for memeplex."""
    mp = Memeplex(
        name="robust",
        memes=[Meme(content=f"m{i}", fidelity=0.5, fecundity=0.5, longevity=0.5) for i in range(5)],
        synergy=0.8,
    )
    score = robustness_score(mp)
    assert 0.0 <= score <= 1.0


@pytest.mark.unit
def test_decay_rate_func():
    """Test decay_rate returns positive value."""
    meme = Meme(content="ephemeral idea", longevity=0.1)
    rate = decay_rate(meme, half_life_days=7.0)
    assert rate > 0
    # Higher longevity should give lower decay
    meme2 = Meme(content="enduring idea", longevity=0.9)
    rate2 = decay_rate(meme2, half_life_days=7.0)
    assert rate2 < rate


@pytest.mark.unit
def test_population_fitness_stats_func():
    """Test population_fitness_stats returns correct keys."""
    pop = [Meme(content=f"m{i}", fidelity=0.5, fecundity=0.5, longevity=0.5) for i in range(10)]
    stats = population_fitness_stats(pop)
    assert "mean" in stats
    assert "std" in stats
    assert "min" in stats
    assert "max" in stats
    assert stats["count"] == 10


@pytest.mark.unit
def test_population_fitness_stats_empty():
    """Test population_fitness_stats with empty population."""
    stats = population_fitness_stats([])
    assert stats["count"] == 0
    assert stats["mean"] == 0.0


# ---------------------------------------------------------------------------
# Semiotic
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_sign_creation():
    """Test Sign creation and id generation."""
    sign = Sign(signifier="fire", signified="danger")
    assert sign.signifier == "fire"
    assert sign.sign_type == SignType.SYMBOL
    assert sign.id  # auto-generated


@pytest.mark.unit
def test_sign_type_enum():
    """Test SignType enum values."""
    assert SignType.ICON.value == "icon"
    assert SignType.INDEX.value == "index"
    assert SignType.SYMBOL.value == "symbol"


@pytest.mark.unit
def test_semiotic_analyzer_decode():
    """Test SemioticAnalyzer decode extracts signs from text."""
    analyzer = SemioticAnalyzer()
    signs = analyzer.decode("The flag represents freedom and democracy here now.")
    assert len(signs) > 0
    signifiers = {s.signifier for s in signs}
    assert "flag" in signifiers


@pytest.mark.unit
def test_semiotic_analyzer_drift():
    """Test SemioticAnalyzer drift between two corpora."""
    analyzer = SemioticAnalyzer()
    corpus_a = ["The economy is growing rapidly with new innovation."]
    corpus_b = ["The economy is shrinking due to global crisis and war."]
    report = analyzer.drift(corpus_a, corpus_b)
    assert isinstance(report, DriftReport)
    assert 0.0 <= report.drift_magnitude <= 1.0


@pytest.mark.unit
def test_drift_report_stability_ratio():
    """Test DriftReport stability_ratio property."""
    report = DriftReport(
        shifted_signs=[Sign(signifier="a", signified="b")],
        stable_signs=[Sign(signifier="c", signified="d"), Sign(signifier="e", signified="f")],
    )
    assert report.stability_ratio == pytest.approx(2 / 3, abs=1e-6)


# ---------------------------------------------------------------------------
# Narrative
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_narrative_arc_creation():
    """Test NarrativeArc creation."""
    arc = NarrativeArc(name="Test Arc", tension_curve=[0.1, 0.5, 1.0, 0.3])
    assert arc.name == "Test Arc"
    assert len(arc.tension_curve) == 4


@pytest.mark.unit
def test_heros_journey_arc():
    """Test hero's journey arc structure."""
    arc = heros_journey_arc()
    assert arc.name == "Hero's Journey"
    assert len(arc.tension_curve) == 12
    assert len(arc.emotional_valence) == 12


@pytest.mark.unit
def test_freytag_pyramid_arc():
    """Test Freytag's Pyramid arc structure."""
    arc = freytag_pyramid_arc()
    assert arc.name == "Freytag's Pyramid"
    assert len(arc.tension_curve) == 5


@pytest.mark.unit
def test_fichtean_curve_arc():
    """Test Fichtean Curve arc structure."""
    arc = fichtean_curve_arc()
    assert arc.name == "Fichtean Curve"
    assert max(arc.tension_curve) == 1.0


@pytest.mark.unit
def test_narrative_creation():
    """Test Narrative dataclass creation."""
    arc = NarrativeArc(name="Test", tension_curve=[0.5])
    n = Narrative(title="My Story", theme="Redemption", arc=arc)
    assert n.title == "My Story"
    assert n.id  # auto-generated UUID


@pytest.mark.unit
def test_archetype_enum():
    """Test Archetype enum values."""
    assert Archetype.HERO.value == "hero"
    assert Archetype.SHADOW.value == "shadow"
    assert Archetype.MENTOR.value == "mentor"


@pytest.mark.unit
@pytest.mark.skip(reason="Narrative analysis requires configured NLP backend")
def test_narrative_engine_analyze():
    """Test NarrativeEngine analyze produces a Narrative."""
    engine = NarrativeEngine()
    narrative = engine.analyze("Once upon a time, a hero saved the world.")
    assert isinstance(narrative, Narrative)
    assert narrative.title == "Analyzed Narrative"


@pytest.mark.unit
def test_narrative_engine_insurgent_counter():
    """Test NarrativeEngine insurgent_counter produces a counter-narrative."""
    engine = NarrativeEngine()
    original = Narrative(
        title="Progress",
        theme="Innovation",
        arc=NarrativeArc(name="test", tension_curve=[0.5]),
    )
    counter = engine.insurgent_counter(original)
    assert "Counter" in counter.title
    assert "Anti" in counter.theme


# ---------------------------------------------------------------------------
# Contagion models
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_contagion_model_creation():
    """Test ContagionModel dataclass creation."""
    model = ContagionModel(infection_rate=0.5, recovery_rate=0.2, network_size=500)
    assert model.infection_rate == 0.5
    assert model.network_size == 500


@pytest.mark.unit
def test_cascade_type_enum():
    """Test CascadeType enum values."""
    assert CascadeType.VIRAL.value == "viral"
    assert CascadeType.DAMPENED.value == "dampened"


@pytest.mark.unit
def test_cascade_creation():
    """Test Cascade dataclass creation."""
    cascade = Cascade(seed_id="meme-001", size=150, depth=5, velocity=10.0)
    assert cascade.size == 150
    assert cascade.cascade_type == CascadeType.ORGANIC


@pytest.mark.unit
def test_propagation_trace():
    """Test PropagationTrace peak and total infected."""
    trace = PropagationTrace(
        time_steps=[0, 1, 2, 3],
        infected_counts=[0, 10, 50, 20],
        susceptible_counts=[1000, 990, 940, 920],
        recovered_counts=[0, 0, 10, 60],
    )
    assert trace.peak_infected() == 50
    assert trace.total_infected() == 80  # 60 recovered + 20 infected at end


@pytest.mark.unit
def test_resonance_map():
    """Test ResonanceMap dataclass."""
    rm = ResonanceMap(nodes={"n1": 0.9, "n2": 0.3}, clusters=[["n1"]])
    assert rm.nodes["n1"] == 0.9
    assert len(rm.clusters) == 1


# ---------------------------------------------------------------------------
# Cultural dynamics
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_cultural_dynamics_imports():
    """Test CulturalDynamicsEngine and related classes import."""
    assert CulturalDynamicsEngine is not None
    assert CulturalState is not None
    assert PowerMap is not None
