"""Tests for meme.narrative -- zero-mock, real instances only.

Sprint 5 coverage expansion for the narrative submodule: Narrative,
NarrativeArc, NarrativeTemplate, Archetype, NarrativeEngine,
structure arcs, and synthesize_myth.  All tests use real dataclass
instances and real function calls.
"""

from __future__ import annotations

import pytest

from codomyrmex.meme.narrative.models import (
    Archetype,
    Narrative,
    NarrativeArc,
    NarrativeTemplate,
)
from codomyrmex.meme.narrative.engine import NarrativeEngine
from codomyrmex.meme.narrative.myth import synthesize_myth
from codomyrmex.meme.narrative.structure import (
    fichtean_curve_arc,
    freytag_pyramid_arc,
    heros_journey_arc,
)


# ---------------------------------------------------------------------------
# Archetype enum
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestArchetype:
    """Tests for the Archetype Jungian/Campbellian enum."""

    def test_all_eight_values(self) -> None:
        """All eight archetypes are present."""
        expected = {
            "hero", "shadow", "mentor", "trickster",
            "herald", "threshold_guardian", "shapeshifter", "ally",
        }
        actual = {a.value for a in Archetype}
        assert actual == expected

    def test_str_subclass(self) -> None:
        """Archetype is a str enum."""
        assert isinstance(Archetype.HERO, str)
        assert Archetype.SHADOW == "shadow"


# ---------------------------------------------------------------------------
# NarrativeArc dataclass
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestNarrativeArc:
    """Tests for the NarrativeArc dataclass."""

    def test_creation_minimal(self) -> None:
        """NarrativeArc with just a name and empty curves."""
        arc = NarrativeArc(name="flat")
        assert arc.name == "flat"
        assert arc.tension_curve == []
        assert arc.emotional_valence == []

    def test_tension_curve_stored(self) -> None:
        """Tension curve values are preserved."""
        curve = [0.1, 0.5, 1.0, 0.3]
        arc = NarrativeArc(name="test", tension_curve=curve)
        assert arc.tension_curve == curve

    def test_emotional_valence_stored(self) -> None:
        """Emotional valence values are preserved."""
        valence = [-0.5, 0.0, 0.8]
        arc = NarrativeArc(name="test", emotional_valence=valence)
        assert arc.emotional_valence == valence


# ---------------------------------------------------------------------------
# NarrativeTemplate dataclass
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestNarrativeTemplate:
    """Tests for the NarrativeTemplate dataclass."""

    def test_creation(self) -> None:
        """NarrativeTemplate stores name, stages, and roles."""
        template = NarrativeTemplate(
            name="Hero's Journey",
            stages=["Ordinary World", "Call", "Threshold"],
            roles=[Archetype.HERO, Archetype.MENTOR],
        )
        assert template.name == "Hero's Journey"
        assert len(template.stages) == 3
        assert Archetype.HERO in template.roles

    def test_empty_stages(self) -> None:
        """Template with empty stages is valid."""
        template = NarrativeTemplate(name="empty", stages=[], roles=[])
        assert template.stages == []


# ---------------------------------------------------------------------------
# Narrative dataclass
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestNarrative:
    """Tests for the Narrative dataclass."""

    def test_auto_id_generation(self) -> None:
        """ID is auto-generated as a UUID string."""
        arc = NarrativeArc(name="test")
        n = Narrative(title="Test", theme="test", arc=arc)
        assert n.id  # non-empty
        assert len(n.id) == 36  # UUID format

    def test_explicit_id_preserved(self) -> None:
        """Supplying an explicit ID skips auto-generation."""
        arc = NarrativeArc(name="test")
        n = Narrative(title="T", theme="t", arc=arc, id="custom-id")
        assert n.id == "custom-id"

    def test_characters_stored(self) -> None:
        """Characters map is stored and retrievable."""
        arc = NarrativeArc(name="test")
        chars = {"Luke": Archetype.HERO, "Vader": Archetype.SHADOW}
        n = Narrative(title="T", theme="t", arc=arc, characters=chars)
        assert n.characters["Luke"] == Archetype.HERO

    def test_cultural_resonance_default(self) -> None:
        """Default cultural_resonance is 0.5."""
        arc = NarrativeArc(name="test")
        n = Narrative(title="T", theme="t", arc=arc)
        assert n.cultural_resonance == 0.5

    def test_content_segments_default_empty(self) -> None:
        """content_segments defaults to empty list."""
        arc = NarrativeArc(name="test")
        n = Narrative(title="T", theme="t", arc=arc)
        assert n.content_segments == []

    def test_metadata_default_empty(self) -> None:
        """metadata defaults to empty dict."""
        arc = NarrativeArc(name="test")
        n = Narrative(title="T", theme="t", arc=arc)
        assert n.metadata == {}

    def test_created_at_is_float(self) -> None:
        """created_at is a float timestamp."""
        arc = NarrativeArc(name="test")
        n = Narrative(title="T", theme="t", arc=arc)
        assert isinstance(n.created_at, float)
        assert n.created_at > 0


# ---------------------------------------------------------------------------
# Structure arc factory functions
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestStructureArcs:
    """Tests for the pre-built narrative arc factories."""

    def test_heros_journey_name(self) -> None:
        """Hero's Journey arc has correct name."""
        arc = heros_journey_arc()
        assert arc.name == "Hero's Journey"

    def test_heros_journey_twelve_stages(self) -> None:
        """Hero's Journey has 12 tension stages."""
        arc = heros_journey_arc()
        assert len(arc.tension_curve) == 12

    def test_heros_journey_valence_matches_tension_length(self) -> None:
        """Valence array length matches tension curve length."""
        arc = heros_journey_arc()
        assert len(arc.emotional_valence) == len(arc.tension_curve)

    def test_freytag_pyramid_five_acts(self) -> None:
        """Freytag's Pyramid has 5 stages."""
        arc = freytag_pyramid_arc()
        assert len(arc.tension_curve) == 5

    def test_freytag_climax_is_max(self) -> None:
        """Climax (index 2) is the maximum tension in Freytag's Pyramid."""
        arc = freytag_pyramid_arc()
        assert max(arc.tension_curve) == arc.tension_curve[2]

    def test_fichtean_curve_eight_stages(self) -> None:
        """Fichtean Curve has 8 stages."""
        arc = fichtean_curve_arc()
        assert len(arc.tension_curve) == 8

    def test_fichtean_climax_near_end(self) -> None:
        """Fichtean Curve climax (1.0) is at index 6."""
        arc = fichtean_curve_arc()
        assert arc.tension_curve[6] == 1.0

    def test_fichtean_resolution_drops(self) -> None:
        """Fichtean Curve resolution (last stage) is the lowest tension."""
        arc = fichtean_curve_arc()
        assert arc.tension_curve[-1] == min(arc.tension_curve)


# ---------------------------------------------------------------------------
# NarrativeEngine
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestNarrativeEngine:
    """Tests for the NarrativeEngine orchestrator."""

    def test_analyze_returns_narrative(self) -> None:
        """analyze returns a Narrative instance."""
        engine = NarrativeEngine()
        result = engine.analyze("The hero fought bravely. The mentor guided the way.")
        assert isinstance(result, Narrative)

    def test_analyze_title(self) -> None:
        """Analyzed narrative has title 'Analyzed Narrative'."""
        engine = NarrativeEngine()
        result = engine.analyze("Some text here.")
        assert result.title == "Analyzed Narrative"

    def test_analyze_detects_hero_character(self) -> None:
        """Text mentioning 'hero' populates the characters map."""
        engine = NarrativeEngine()
        result = engine.analyze("The hero saved the village from the villain.")
        assert "Hero" in result.characters
        assert result.characters["Hero"] == Archetype.HERO

    def test_analyze_detects_villain_as_shadow(self) -> None:
        """Text mentioning 'villain' maps to SHADOW archetype."""
        engine = NarrativeEngine()
        result = engine.analyze("The villain destroyed everything.")
        assert "Villain" in result.characters
        assert result.characters["Villain"] == Archetype.SHADOW

    def test_analyze_tension_curve_length(self) -> None:
        """Tension curve length matches number of sentences."""
        engine = NarrativeEngine()
        text = "First sentence. Second sentence. Third sentence."
        result = engine.analyze(text)
        assert len(result.arc.tension_curve) == 3

    def test_analyze_content_segments(self) -> None:
        """content_segments contain the split sentences."""
        engine = NarrativeEngine()
        text = "Alpha bravo. Charlie delta."
        result = engine.analyze(text)
        assert len(result.content_segments) == 2

    def test_generate_from_template(self) -> None:
        """generate produces text with one line per stage."""
        engine = NarrativeEngine()
        template = NarrativeTemplate(
            name="Simple",
            stages=["Setup", "Conflict", "Resolution"],
            roles=[Archetype.HERO],
        )
        story = engine.generate(template, {"protagonist": "Alice", "context": "a forest"})
        lines = story.strip().split("\n")
        assert len(lines) == 3
        assert "Alice" in story
        assert "a forest" in story

    def test_generate_uses_default_params(self) -> None:
        """generate uses default protagonist/context when not provided."""
        engine = NarrativeEngine()
        template = NarrativeTemplate(
            name="Default",
            stages=["Act1"],
            roles=[],
        )
        story = engine.generate(template, {})
        assert "Hero" in story  # default protagonist
        assert "the world" in story  # default context

    def test_insurgent_counter_title(self) -> None:
        """Counter-narrative title starts with 'Counter:'."""
        engine = NarrativeEngine()
        original = Narrative(
            title="Progress",
            theme="Innovation",
            arc=NarrativeArc(name="test"),
        )
        counter = engine.insurgent_counter(original)
        assert counter.title.startswith("Counter:")

    def test_insurgent_counter_theme(self) -> None:
        """Counter-narrative theme starts with 'Anti-'."""
        engine = NarrativeEngine()
        original = Narrative(
            title="Growth",
            theme="Expansion",
            arc=NarrativeArc(name="test"),
        )
        counter = engine.insurgent_counter(original)
        assert counter.theme.startswith("Anti-")

    def test_insurgent_counter_content_segments(self) -> None:
        """Counter-narrative has exactly 2 content segments."""
        engine = NarrativeEngine()
        original = Narrative(
            title="Story",
            theme="Theme",
            arc=NarrativeArc(name="test"),
            content_segments=["seg1", "seg2", "seg3"],
        )
        counter = engine.insurgent_counter(original)
        assert len(counter.content_segments) == 2

    def test_insurgent_counter_does_not_mutate_original(self) -> None:
        """Counter-narrative creation does not mutate the original."""
        engine = NarrativeEngine()
        original = Narrative(
            title="Original",
            theme="Truth",
            arc=NarrativeArc(name="test"),
        )
        engine.insurgent_counter(original)
        assert original.title == "Original"
        assert original.theme == "Truth"


# ---------------------------------------------------------------------------
# synthesize_myth
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSynthesizMyth:
    """Tests for the synthesize_myth function."""

    def test_returns_narrative(self) -> None:
        """synthesize_myth returns a Narrative instance."""
        archetypes = {"Neo": Archetype.HERO, "Smith": Archetype.SHADOW}
        myth = synthesize_myth("technology", archetypes, theme="liberation")
        assert isinstance(myth, Narrative)

    def test_title_contains_hero_name(self) -> None:
        """Myth title mentions the hero character."""
        archetypes = {"Prometheus": Archetype.HERO, "Zeus": Archetype.SHADOW}
        myth = synthesize_myth("mythology", archetypes)
        assert "Prometheus" in myth.title

    def test_theme_stored(self) -> None:
        """Supplied theme is stored in the narrative."""
        archetypes = {"H": Archetype.HERO}
        myth = synthesize_myth("test", archetypes, theme="justice")
        assert myth.theme == "justice"

    def test_content_segments_mention_domain(self) -> None:
        """Content segments reference the domain."""
        archetypes = {"Alice": Archetype.HERO, "Queen": Archetype.SHADOW}
        myth = synthesize_myth("wonderland", archetypes)
        combined = " ".join(myth.content_segments)
        assert "wonderland" in combined

    def test_content_has_four_segments(self) -> None:
        """Myth has exactly 4 content segments."""
        archetypes = {"H": Archetype.HERO, "S": Archetype.SHADOW}
        myth = synthesize_myth("domain", archetypes)
        assert len(myth.content_segments) == 4

    def test_cultural_resonance_high(self) -> None:
        """Myths have high cultural resonance (0.8)."""
        archetypes = {"H": Archetype.HERO}
        myth = synthesize_myth("domain", archetypes)
        assert myth.cultural_resonance == 0.8

    def test_metadata_includes_domain(self) -> None:
        """Metadata contains the domain key."""
        archetypes = {"H": Archetype.HERO}
        myth = synthesize_myth("crypto", archetypes)
        assert myth.metadata.get("domain") == "crypto"

    def test_arc_is_heros_journey(self) -> None:
        """Myth uses the Hero's Journey arc."""
        archetypes = {"H": Archetype.HERO}
        myth = synthesize_myth("domain", archetypes)
        assert myth.arc.name == "Hero's Journey"

    def test_no_hero_archetype_uses_default(self) -> None:
        """When no HERO archetype is provided, uses 'The Hero' default."""
        archetypes = {"Loki": Archetype.TRICKSTER}
        myth = synthesize_myth("norse", archetypes)
        assert "The Hero" in myth.title

    def test_no_shadow_archetype_uses_default(self) -> None:
        """When no SHADOW archetype, uses 'The Shadow' in content."""
        archetypes = {"H": Archetype.HERO}
        myth = synthesize_myth("domain", archetypes)
        combined = " ".join(myth.content_segments)
        assert "The Shadow" in combined
