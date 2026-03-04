"""Tests for meme.neurolinguistic -- zero-mock, real instances only.

Covers PatternType, CognitiveFrame, LinguisticPattern, BiasInstance,
NeurolinguisticEngine, analyze_frames, reframe, detect_patterns,
milton_model_patterns, and meta_model_patterns.
"""

from __future__ import annotations

import pytest

from codomyrmex.meme.neurolinguistic.engine import NeurolinguisticEngine
from codomyrmex.meme.neurolinguistic.framing import analyze_frames, reframe
from codomyrmex.meme.neurolinguistic.models import (
    BiasInstance,
    CognitiveFrame,
    LinguisticPattern,
    PatternType,
    PersuasionAttempt,
)
from codomyrmex.meme.neurolinguistic.patterns import (
    detect_patterns,
    meta_model_patterns,
    milton_model_patterns,
)

# ---------------------------------------------------------------------------
# PatternType enum
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPatternType:
    """Tests for the PatternType enum."""

    def test_four_types_present(self) -> None:
        """All four pattern types are present."""
        expected = {"hypnotic", "clarifying", "persuasive", "deceptive"}
        assert {pt.value for pt in PatternType} == expected

    def test_str_subclass(self) -> None:
        """PatternType is a StrEnum."""
        assert isinstance(PatternType.HYPNOTIC, str)
        assert PatternType.DECEPTIVE == "deceptive"


# ---------------------------------------------------------------------------
# CognitiveFrame dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCognitiveFrame:
    """Tests for the CognitiveFrame dataclass."""

    def test_creation_stores_name(self) -> None:
        """name field is stored correctly."""
        frame = CognitiveFrame(name="Tax Relief")
        assert frame.name == "Tax Relief"

    def test_keywords_default_empty(self) -> None:
        """Default keywords is empty list."""
        frame = CognitiveFrame(name="x")
        assert frame.keywords == []

    def test_roles_default_empty(self) -> None:
        """Default roles is empty dict."""
        frame = CognitiveFrame(name="x")
        assert frame.roles == {}

    def test_logic_default_empty(self) -> None:
        """Default logic is empty string."""
        frame = CognitiveFrame(name="x")
        assert frame.logic == ""

    def test_strength_default(self) -> None:
        """Default strength is 0.5."""
        frame = CognitiveFrame(name="x")
        assert frame.strength == pytest.approx(0.5)

    def test_explicit_fields_stored(self) -> None:
        """Explicit field values are stored correctly."""
        frame = CognitiveFrame(
            name="Freedom",
            keywords=["liberty", "choice", "rights"],
            roles={"citizen": "hero", "state": "threat"},
            logic="freedom enables flourishing",
            strength=0.9,
        )
        assert frame.keywords == ["liberty", "choice", "rights"]
        assert frame.roles["citizen"] == "hero"
        assert frame.logic == "freedom enables flourishing"
        assert frame.strength == pytest.approx(0.9)


# ---------------------------------------------------------------------------
# LinguisticPattern dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLinguisticPattern:
    """Tests for the LinguisticPattern dataclass."""

    def test_creation(self) -> None:
        """LinguisticPattern stores name and pattern_type."""
        lp = LinguisticPattern(name="Double Bind", pattern_type=PatternType.HYPNOTIC)
        assert lp.name == "Double Bind"
        assert lp.pattern_type == PatternType.HYPNOTIC

    def test_template_default_empty(self) -> None:
        """Default template is empty string."""
        lp = LinguisticPattern(name="x", pattern_type=PatternType.CLARIFYING)
        assert lp.template == ""

    def test_description_stored(self) -> None:
        """Description is stored when supplied."""
        lp = LinguisticPattern(
            name="x",
            pattern_type=PatternType.PERSUASIVE,
            description="A persuasive technique",
        )
        assert lp.description == "A persuasive technique"


# ---------------------------------------------------------------------------
# BiasInstance dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBiasInstance:
    """Tests for the BiasInstance dataclass."""

    def test_creation_stores_fields(self) -> None:
        """All BiasInstance fields are stored correctly."""
        bias = BiasInstance(
            bias_name="Confirmation Bias",
            trigger="selective news consumption",
            impact_score=0.8,
        )
        assert bias.bias_name == "Confirmation Bias"
        assert bias.trigger == "selective news consumption"
        assert bias.impact_score == pytest.approx(0.8)

    def test_impact_score_default(self) -> None:
        """Default impact_score is 0.5."""
        bias = BiasInstance(bias_name="x", trigger="y")
        assert bias.impact_score == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# PersuasionAttempt dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPersuasionAttempt:
    """Tests for the PersuasionAttempt dataclass."""

    def test_creation_stores_fields(self) -> None:
        """All PersuasionAttempt fields are stored correctly."""
        attempt = PersuasionAttempt(
            target="group_A",
            technique="social proof",
            content="Everyone is doing it.",
            success_prob=0.7,
        )
        assert attempt.target == "group_A"
        assert attempt.technique == "social proof"
        assert attempt.content == "Everyone is doing it."
        assert attempt.success_prob == pytest.approx(0.7)

    def test_timestamp_is_float(self) -> None:
        """timestamp is a float."""
        import time
        before = time.time()
        attempt = PersuasionAttempt(target="x", technique="y", content="z", success_prob=0.5)
        after = time.time()
        assert before <= attempt.timestamp <= after


# ---------------------------------------------------------------------------
# milton_model_patterns and meta_model_patterns
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPatternLibraries:
    """Tests for the built-in pattern library functions."""

    def test_milton_model_returns_list(self) -> None:
        """milton_model_patterns returns a non-empty list."""
        patterns = milton_model_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_milton_model_all_hypnotic(self) -> None:
        """All Milton Model patterns have HYPNOTIC type."""
        for pattern in milton_model_patterns():
            assert pattern.pattern_type == PatternType.HYPNOTIC

    def test_milton_model_has_mind_read(self) -> None:
        """Milton Model includes the 'Mind Read' pattern."""
        names = {p.name for p in milton_model_patterns()}
        assert "Mind Read" in names

    def test_meta_model_returns_list(self) -> None:
        """meta_model_patterns returns a non-empty list."""
        patterns = meta_model_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_meta_model_all_clarifying(self) -> None:
        """All Meta Model patterns have CLARIFYING type."""
        for pattern in meta_model_patterns():
            assert pattern.pattern_type == PatternType.CLARIFYING

    def test_meta_model_has_universal_quantifier(self) -> None:
        """Meta Model includes the Universal Quantifier Challenge."""
        names = {p.name for p in meta_model_patterns()}
        assert "Universal Quantifier Challenge" in names

    def test_patterns_have_non_empty_descriptions(self) -> None:
        """All patterns have non-empty descriptions."""
        for pattern in milton_model_patterns() + meta_model_patterns():
            assert len(pattern.description) > 0


# ---------------------------------------------------------------------------
# detect_patterns
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDetectPatterns:
    """Tests for the detect_patterns function."""

    def test_always_triggers_universal_quantifier(self) -> None:
        """Text with 'always' triggers the Universal Quantifier pattern."""
        patterns = detect_patterns("You should always follow the rules.")
        assert len(patterns) == 1
        assert patterns[0].name == "Universal Quantifier"

    def test_never_triggers_universal_quantifier(self) -> None:
        """Text with 'never' triggers the Universal Quantifier pattern."""
        patterns = detect_patterns("You should never give up.")
        assert len(patterns) == 1

    def test_no_trigger_words_returns_empty(self) -> None:
        """Text without trigger words returns empty list."""
        patterns = detect_patterns("The sky is blue today.")
        assert patterns == []

    def test_detected_pattern_type_is_deceptive(self) -> None:
        """Detected Universal Quantifier has DECEPTIVE type."""
        patterns = detect_patterns("This always works perfectly.")
        assert patterns[0].pattern_type == PatternType.DECEPTIVE

    def test_case_insensitive_detection(self) -> None:
        """Detection is case-insensitive ('ALWAYS' should trigger)."""
        patterns = detect_patterns("ALWAYS remember this.")
        assert len(patterns) == 1


# ---------------------------------------------------------------------------
# analyze_frames
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAnalyzeFrames:
    """Tests for the analyze_frames function."""

    def test_empty_frames_returns_empty(self) -> None:
        """No registered frames produces no active frames."""
        result = analyze_frames("text about freedom", [])
        assert result == []

    def test_keyword_match_activates_frame(self) -> None:
        """Frame with matching keyword appears in active frames."""
        frame = CognitiveFrame(name="Freedom", keywords=["freedom", "liberty"])
        result = analyze_frames("freedom is important", [frame])
        assert len(result) == 1
        assert result[0].name == "Freedom"

    def test_no_keyword_match_does_not_activate(self) -> None:
        """Frame without matching keyword is not activated."""
        frame = CognitiveFrame(name="Economy", keywords=["gdp", "inflation"])
        result = analyze_frames("the weather is nice today", [frame])
        assert result == []

    def test_multiple_frames_partial_activation(self) -> None:
        """Only frames with matching keywords are returned."""
        freedom_frame = CognitiveFrame(name="Freedom", keywords=["freedom"])
        economy_frame = CognitiveFrame(name="Economy", keywords=["economy"])
        result = analyze_frames("freedom is the foundation of democracy", [freedom_frame, economy_frame])
        names = [f.name for f in result]
        assert "Freedom" in names
        assert "Economy" not in names

    def test_case_insensitive_keyword_matching(self) -> None:
        """Keyword matching is case-insensitive."""
        frame = CognitiveFrame(name="Safety", keywords=["Safety"])
        result = analyze_frames("safety is paramount", [frame])
        assert len(result) == 1


# ---------------------------------------------------------------------------
# reframe
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestReframe:
    """Tests for the reframe function."""

    def test_reframe_substitutes_primary_keyword(self) -> None:
        """Primary source keyword is replaced with target keyword."""
        src = CognitiveFrame(name="Tax", keywords=["burden"])
        tgt = CognitiveFrame(name="Investment", keywords=["investment"])
        result = reframe("This is a tax burden", src, tgt)
        assert "investment" in result
        assert "burden" not in result

    def test_empty_source_keywords_returns_unchanged(self) -> None:
        """Empty source keywords returns original content."""
        src = CognitiveFrame(name="Empty", keywords=[])
        tgt = CognitiveFrame(name="Target", keywords=["new"])
        result = reframe("original text", src, tgt)
        assert result == "original text"

    def test_empty_target_keywords_returns_unchanged(self) -> None:
        """Empty target keywords returns original content."""
        src = CognitiveFrame(name="Src", keywords=["old"])
        tgt = CognitiveFrame(name="Empty", keywords=[])
        result = reframe("old content here", src, tgt)
        assert result == "old content here"

    def test_no_keyword_in_text_returns_unchanged(self) -> None:
        """If source keyword not in text, returns original."""
        src = CognitiveFrame(name="S", keywords=["missing"])
        tgt = CognitiveFrame(name="T", keywords=["replacement"])
        result = reframe("this text has no trigger", src, tgt)
        assert result == "this text has no trigger"


# ---------------------------------------------------------------------------
# NeurolinguisticEngine
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNeurolinguisticEngineRegister:
    """Tests for NeurolinguisticEngine frame registration."""

    def test_register_frame_adds_to_list(self) -> None:
        """register_frame appends frame to known_frames."""
        engine = NeurolinguisticEngine()
        frame = CognitiveFrame(name="Justice", keywords=["justice", "fair"])
        engine.register_frame(frame)
        assert len(engine.known_frames) == 1

    def test_register_multiple_frames(self) -> None:
        """Multiple frames can be registered."""
        engine = NeurolinguisticEngine()
        for i in range(3):
            engine.register_frame(CognitiveFrame(name=f"frame_{i}"))
        assert len(engine.known_frames) == 3

    def test_initial_known_frames_empty(self) -> None:
        """Fresh engine starts with no known frames."""
        engine = NeurolinguisticEngine()
        assert engine.known_frames == []


@pytest.mark.unit
class TestNeurolinguisticEngineAudit:
    """Tests for NeurolinguisticEngine.audit."""

    def test_audit_returns_dict_with_expected_keys(self) -> None:
        """audit result has 'frames', 'patterns', 'score' keys."""
        engine = NeurolinguisticEngine()
        result = engine.audit("simple text")
        assert "frames" in result
        assert "patterns" in result
        assert "score" in result

    def test_audit_no_frames_no_patterns(self) -> None:
        """With no registered frames and no trigger words, score is 0."""
        engine = NeurolinguisticEngine()
        result = engine.audit("simple neutral text here")
        assert result["score"] == 0

    def test_audit_detects_universal_quantifier(self) -> None:
        """'always' in text triggers Universal Quantifier pattern."""
        engine = NeurolinguisticEngine()
        result = engine.audit("This always works perfectly every time.")
        assert len(result["patterns"]) == 1

    def test_audit_detects_registered_frame(self) -> None:
        """Registered frame keyword in text shows as active frame."""
        engine = NeurolinguisticEngine()
        engine.register_frame(CognitiveFrame(name="Freedom", keywords=["liberty"]))
        result = engine.audit("liberty is the greatest value")
        assert len(result["frames"]) == 1
        assert result["frames"][0].name == "Freedom"

    def test_audit_score_accumulates(self) -> None:
        """Score = len(frames) + len(patterns) for combined detection."""
        engine = NeurolinguisticEngine()
        engine.register_frame(CognitiveFrame(name="F", keywords=["trigger"]))
        result = engine.audit("trigger always matters")
        # 1 frame + 1 pattern = 2
        assert result["score"] == 2


@pytest.mark.unit
class TestNeurolinguisticEngineSpin:
    """Tests for NeurolinguisticEngine.spin."""

    def test_spin_unknown_frame_returns_original(self) -> None:
        """spin with unknown frame name returns original text."""
        engine = NeurolinguisticEngine()
        result = engine.spin("original content", "UnknownFrame")
        assert result == "original content"

    def test_spin_injects_keyword(self) -> None:
        """spin injects first keyword of target frame into text."""
        engine = NeurolinguisticEngine()
        engine.register_frame(CognitiveFrame(name="Growth", keywords=["opportunity", "progress"]))
        result = engine.spin("Here is the situation.", "Growth")
        assert "opportunity" in result
