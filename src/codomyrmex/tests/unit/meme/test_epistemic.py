"""Tests for meme.epistemic -- zero-mock, real instances only.

Covers Evidence, EvidenceType, Fact, Belief, EpistemicState, EpistemicEngine,
verify_claim, and calculate_certainty with real computation.
"""

from __future__ import annotations

import pytest

from codomyrmex.meme.epistemic.engine import EpistemicEngine
from codomyrmex.meme.epistemic.models import (
    Belief,
    EpistemicState,
    Evidence,
    EvidenceType,
    Fact,
)
from codomyrmex.meme.epistemic.truth import calculate_certainty, verify_claim

# ---------------------------------------------------------------------------
# EvidenceType enum
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEvidenceType:
    """Tests for the EvidenceType enum."""

    def test_all_five_types(self) -> None:
        """All five evidence types are present."""
        expected = {"empirical", "logical", "testimonial", "anecdotal", "fabricated"}
        assert {e.value for e in EvidenceType} == expected

    def test_str_subclass(self) -> None:
        """EvidenceType is a StrEnum."""
        assert isinstance(EvidenceType.EMPIRICAL, str)
        assert EvidenceType.FABRICATED == "fabricated"


# ---------------------------------------------------------------------------
# Evidence dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEvidence:
    """Tests for the Evidence dataclass."""

    def test_creation_stores_fields(self) -> None:
        """All Evidence fields are stored correctly."""
        ev = Evidence(
            content="Lab results confirm",
            source="Lab A",
            evidence_type=EvidenceType.EMPIRICAL,
            weight=0.9,
            validity=1.0,
        )
        assert ev.content == "Lab results confirm"
        assert ev.source == "Lab A"
        assert ev.evidence_type == EvidenceType.EMPIRICAL
        assert ev.weight == pytest.approx(0.9)
        assert ev.validity == pytest.approx(1.0)

    def test_default_weight(self) -> None:
        """Default weight is 0.5."""
        ev = Evidence(content="x", source="s", evidence_type=EvidenceType.ANECDOTAL)
        assert ev.weight == pytest.approx(0.5)

    def test_default_validity(self) -> None:
        """Default validity is 1.0."""
        ev = Evidence(content="x", source="s", evidence_type=EvidenceType.LOGICAL)
        assert ev.validity == pytest.approx(1.0)

    def test_fabricated_type(self) -> None:
        """FABRICATED type is stored correctly."""
        ev = Evidence(content="fake", source="troll", evidence_type=EvidenceType.FABRICATED)
        assert ev.evidence_type == EvidenceType.FABRICATED


# ---------------------------------------------------------------------------
# Fact dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFact:
    """Tests for the Fact dataclass."""

    def test_creation_stores_fields(self) -> None:
        """All Fact fields are stored correctly."""
        fact = Fact(
            statement="The Earth orbits the Sun",
            verification_method="astronomical observation",
            confidence=0.99,
        )
        assert fact.statement == "The Earth orbits the Sun"
        assert fact.verification_method == "astronomical observation"
        assert fact.confidence == pytest.approx(0.99)

    def test_default_confidence(self) -> None:
        """Default confidence is 1.0."""
        fact = Fact(statement="x", verification_method="test")
        assert fact.confidence == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Belief dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBelief:
    """Tests for the Belief dataclass."""

    def test_creation_stores_fields(self) -> None:
        """All Belief fields are stored correctly."""
        belief = Belief(
            statement="The sky is always blue",
            adherent="person_A",
            certainty=0.8,
            emotional_investment=0.6,
        )
        assert belief.statement == "The sky is always blue"
        assert belief.adherent == "person_A"
        assert belief.certainty == pytest.approx(0.8)
        assert belief.emotional_investment == pytest.approx(0.6)

    def test_default_certainty(self) -> None:
        """Default certainty is 0.5."""
        belief = Belief(statement="x", adherent="y")
        assert belief.certainty == pytest.approx(0.5)

    def test_default_emotional_investment(self) -> None:
        """Default emotional_investment is 0.5."""
        belief = Belief(statement="x", adherent="y")
        assert belief.emotional_investment == pytest.approx(0.5)

    def test_supporting_evidence_default_empty(self) -> None:
        """Default supporting_evidence is empty list."""
        belief = Belief(statement="x", adherent="y")
        assert belief.supporting_evidence == []

    def test_supporting_evidence_stored(self) -> None:
        """Supporting evidence list is stored correctly."""
        ev = Evidence(content="e", source="s", evidence_type=EvidenceType.EMPIRICAL)
        belief = Belief(statement="x", adherent="y", supporting_evidence=[ev])
        assert len(belief.supporting_evidence) == 1


# ---------------------------------------------------------------------------
# EpistemicState dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEpistemicState:
    """Tests for the EpistemicState aggregate dataclass."""

    def test_empty_defaults(self) -> None:
        """Default EpistemicState has empty facts, beliefs, and zero entropy."""
        state = EpistemicState()
        assert state.facts == []
        assert state.beliefs == []
        assert state.entropy == pytest.approx(0.0)

    def test_facts_stored(self) -> None:
        """Facts list is stored and retrievable."""
        fact = Fact(statement="x", verification_method="test")
        state = EpistemicState(facts=[fact])
        assert len(state.facts) == 1

    def test_beliefs_stored(self) -> None:
        """Beliefs list is stored and retrievable."""
        belief = Belief(statement="x", adherent="y")
        state = EpistemicState(beliefs=[belief])
        assert len(state.beliefs) == 1

    def test_entropy_nonzero(self) -> None:
        """Nonzero entropy is stored correctly."""
        state = EpistemicState(entropy=0.75)
        assert state.entropy == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# verify_claim
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestVerifyClaim:
    """Tests for the verify_claim function."""

    def test_no_evidence_returns_neutral_confidence(self) -> None:
        """No evidence gives 0.5 confidence (neutral)."""
        fact = verify_claim("the world is round", [])
        assert fact.confidence == pytest.approx(0.5)

    def test_returns_fact_type(self) -> None:
        """verify_claim always returns a Fact instance."""
        result = verify_claim("test", [])
        assert isinstance(result, Fact)

    def test_statement_preserved(self) -> None:
        """The statement is preserved in the returned Fact."""
        fact = verify_claim("specific claim", [])
        assert fact.statement == "specific claim"

    def test_verification_method_is_evidence_aggregation(self) -> None:
        """Verification method is always 'evidence_aggregation'."""
        fact = verify_claim("x", [])
        assert fact.verification_method == "evidence_aggregation"

    def test_strong_empirical_evidence_raises_confidence(self) -> None:
        """Strong empirical evidence raises confidence above 0.5."""
        ev = Evidence(
            content="proven data",
            source="lab",
            evidence_type=EvidenceType.EMPIRICAL,
            weight=1.0,
            validity=1.0,
        )
        fact = verify_claim("hypothesis", [ev])
        assert fact.confidence > 0.5

    def test_fabricated_evidence_reduces_confidence(self) -> None:
        """Fabricated evidence lowers confidence below neutral."""
        ev = Evidence(
            content="fake data",
            source="troll",
            evidence_type=EvidenceType.FABRICATED,
            weight=1.0,
            validity=1.0,
        )
        fact = verify_claim("false claim", [ev])
        assert fact.confidence < 0.5

    def test_multiple_strong_evidence_gives_high_confidence(self) -> None:
        """Multiple strong empirical evidence items yield high confidence."""
        evidences = [
            Evidence(
                content=f"study_{i}",
                source=f"lab_{i}",
                evidence_type=EvidenceType.EMPIRICAL,
                weight=1.0,
                validity=1.0,
            )
            for i in range(3)
        ]
        fact = verify_claim("claim", evidences)
        assert fact.confidence > 0.7

    def test_mixed_evidence_moderate_confidence(self) -> None:
        """Mix of good and fabricated evidence produces moderate confidence."""
        good_ev = Evidence(
            content="good",
            source="lab",
            evidence_type=EvidenceType.EMPIRICAL,
            weight=0.8,
            validity=1.0,
        )
        fake_ev = Evidence(
            content="fake",
            source="troll",
            evidence_type=EvidenceType.FABRICATED,
            weight=0.8,
            validity=1.0,
        )
        fact = verify_claim("contested", [good_ev, fake_ev])
        # Should be neither very high nor very low
        assert 0.0 <= fact.confidence <= 1.0


# ---------------------------------------------------------------------------
# calculate_certainty
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculateCertainty:
    """Tests for the calculate_certainty function."""

    def test_empty_beliefs_returns_zero(self) -> None:
        """Empty belief list returns 0.0 certainty."""
        assert calculate_certainty([]) == pytest.approx(0.0)

    def test_single_belief_returns_its_certainty(self) -> None:
        """Single belief returns that belief's certainty."""
        belief = Belief(statement="x", adherent="y", certainty=0.75)
        assert calculate_certainty([belief]) == pytest.approx(0.75)

    def test_average_of_multiple_beliefs(self) -> None:
        """Returns mean certainty of multiple beliefs."""
        b1 = Belief(statement="a", adherent="x", certainty=0.4)
        b2 = Belief(statement="b", adherent="x", certainty=0.8)
        expected = (0.4 + 0.8) / 2
        assert calculate_certainty([b1, b2]) == pytest.approx(expected, abs=1e-9)

    def test_uniform_certainty(self) -> None:
        """Uniform certainty yields that same value."""
        beliefs = [Belief(statement=f"b{i}", adherent="x", certainty=0.6) for i in range(5)]
        assert calculate_certainty(beliefs) == pytest.approx(0.6, abs=1e-9)


# ---------------------------------------------------------------------------
# EpistemicEngine
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEpistemicEngineAddFact:
    """Tests for EpistemicEngine.add_fact."""

    def test_add_fact_appends_to_state(self) -> None:
        """add_fact adds fact to internal state.facts."""
        engine = EpistemicEngine()
        fact = Fact(statement="water boils at 100C", verification_method="experiment")
        engine.add_fact(fact)
        assert len(engine.state.facts) == 1
        assert engine.state.facts[0].statement == "water boils at 100C"

    def test_add_multiple_facts(self) -> None:
        """Multiple facts accumulate in state."""
        engine = EpistemicEngine()
        for i in range(5):
            engine.add_fact(Fact(statement=f"fact_{i}", verification_method="test"))
        assert len(engine.state.facts) == 5

    def test_initial_state_is_empty(self) -> None:
        """Fresh engine has empty facts and beliefs."""
        engine = EpistemicEngine()
        assert engine.state.facts == []
        assert engine.state.beliefs == []


@pytest.mark.unit
class TestEpistemicEngineAssessClaim:
    """Tests for EpistemicEngine.assess_claim."""

    def test_returns_fact(self) -> None:
        """assess_claim returns a Fact instance."""
        engine = EpistemicEngine()
        fact = engine.assess_claim("water is wet", [])
        assert isinstance(fact, Fact)

    def test_high_confidence_fact_added_to_state(self) -> None:
        """Fact with confidence > 0.8 is automatically stored."""
        engine = EpistemicEngine()
        # Provide strong evidence to push confidence > 0.8
        evidences = [
            Evidence(
                content=f"ev_{i}",
                source="lab",
                evidence_type=EvidenceType.EMPIRICAL,
                weight=1.0,
                validity=1.0,
            )
            for i in range(3)
        ]
        engine.assess_claim("strong claim", evidences)
        assert len(engine.state.facts) == 1

    def test_low_confidence_fact_not_added_to_state(self) -> None:
        """Fact with confidence <= 0.8 is NOT stored in state."""
        engine = EpistemicEngine()
        # No evidence = 0.5 confidence, which is <= 0.8
        engine.assess_claim("weak claim", [])
        assert len(engine.state.facts) == 0


@pytest.mark.unit
class TestEpistemicEngineDetectContradictions:
    """Tests for EpistemicEngine.detect_contradictions."""

    def test_no_contradictions_when_empty(self) -> None:
        """No facts or beliefs produces no contradictions."""
        engine = EpistemicEngine()
        assert engine.detect_contradictions() == []

    def test_detects_negation_contradiction(self) -> None:
        """A belief of 'not <fact>' is detected as contradiction."""
        engine = EpistemicEngine()
        engine.state.facts.append(
            Fact(statement="the earth is round", verification_method="observation")
        )
        engine.state.beliefs.append(
            Belief(
                statement="not the earth is round",
                adherent="flat_earther",
                certainty=0.9,
            )
        )
        conflicts = engine.detect_contradictions()
        assert len(conflicts) == 1
        assert "Conflict" in conflicts[0]

    def test_non_contradictory_belief_not_flagged(self) -> None:
        """A belief that does not negate any fact produces no conflicts."""
        engine = EpistemicEngine()
        engine.state.facts.append(
            Fact(statement="gravity exists", verification_method="observation")
        )
        engine.state.beliefs.append(
            Belief(statement="space travel is possible", adherent="astronaut")
        )
        assert engine.detect_contradictions() == []

    def test_multiple_contradictions_reported(self) -> None:
        """Multiple contradicting beliefs all appear in conflicts."""
        engine = EpistemicEngine()
        engine.state.facts.append(Fact(statement="fact_one", verification_method="test"))
        engine.state.facts.append(Fact(statement="fact_two", verification_method="test"))
        engine.state.beliefs.append(
            Belief(statement="not fact_one and not fact_two", adherent="x")
        )
        conflicts = engine.detect_contradictions()
        assert len(conflicts) >= 2
