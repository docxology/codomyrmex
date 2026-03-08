"""Zero-mock tests for the relations module core behavior.

Covers:
  - strength_scoring.py: Interaction, StrengthConfig, RelationStrengthScorer,
    DecayFunction, StrengthScore — all decay modes, score(), score_all(), top_relations()
  - mcp_tools.py: relations_score_strength MCP tool

No mocks — all tests use real in-memory data with controlled timestamps.
"""

from __future__ import annotations

import math
import time

import pytest

try:
    from codomyrmex.relations.strength_scoring import (
        DecayFunction,
        Interaction,
        RelationStrengthScorer,
        StrengthConfig,
        StrengthScore,
    )

    HAS_RELATIONS = True
except ImportError:
    HAS_RELATIONS = False

if not HAS_RELATIONS:
    pytest.skip("relations module not available", allow_module_level=True)

# Fixed "now" for deterministic tests
NOW = 1_000_000.0
ONE_DAY = 86400.0
ONE_YEAR = ONE_DAY * 365


# ---------------------------------------------------------------------------
# Interaction dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestInteractionDataclass:
    """Interaction creation and field tests."""

    def test_minimal_creation(self):
        ix = Interaction(source="a", target="b", interaction_type="message", timestamp=NOW)
        assert ix.source == "a"
        assert ix.target == "b"
        assert ix.interaction_type == "message"
        assert ix.timestamp == NOW

    def test_default_weight_is_one(self):
        ix = Interaction(source="a", target="b", interaction_type="call", timestamp=NOW)
        assert ix.weight == 1.0

    def test_custom_weight(self):
        ix = Interaction(
            source="a", target="b", interaction_type="meeting", timestamp=NOW, weight=3.0
        )
        assert ix.weight == 3.0

    def test_default_metadata_empty(self):
        ix = Interaction(source="a", target="b", interaction_type="note", timestamp=NOW)
        assert ix.metadata == {}


# ---------------------------------------------------------------------------
# StrengthConfig dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestStrengthConfig:
    """StrengthConfig defaults and construction tests."""

    def test_default_decay_exponential(self):
        cfg = StrengthConfig()
        assert cfg.decay_function == DecayFunction.EXPONENTIAL

    def test_default_half_life_30_days(self):
        cfg = StrengthConfig()
        assert cfg.half_life == pytest.approx(ONE_DAY * 30)

    def test_default_max_age_one_year(self):
        cfg = StrengthConfig()
        assert cfg.max_age == pytest.approx(ONE_YEAR)

    def test_custom_type_weights(self):
        cfg = StrengthConfig(type_weights={"meeting": 5.0, "email": 1.0})
        assert cfg.type_weights["meeting"] == 5.0
        assert cfg.type_weights["email"] == 1.0

    def test_default_min_score_zero(self):
        cfg = StrengthConfig()
        assert cfg.min_score == 0.0


# ---------------------------------------------------------------------------
# DecayFunction values (all four modes)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDecayFunctions:
    """_decay_weight tests for all four decay modes using a controlled scorer."""

    def _scorer(self, decay_function, half_life=ONE_DAY * 30, max_age=ONE_YEAR):
        cfg = StrengthConfig(
            decay_function=decay_function,
            half_life=half_life,
            max_age=max_age,
        )
        return RelationStrengthScorer(config=cfg)

    def test_none_decay_always_returns_one(self):
        scorer = self._scorer(DecayFunction.NONE)
        assert scorer._decay_weight(0) == 1.0
        assert scorer._decay_weight(ONE_DAY) == 1.0
        assert scorer._decay_weight(ONE_YEAR * 10) == 1.0

    def test_exponential_at_age_zero(self):
        scorer = self._scorer(DecayFunction.EXPONENTIAL, half_life=ONE_DAY)
        assert scorer._decay_weight(0) == pytest.approx(1.0)

    def test_exponential_at_half_life(self):
        scorer = self._scorer(DecayFunction.EXPONENTIAL, half_life=ONE_DAY)
        # At age == half_life, weight should be 0.5
        assert scorer._decay_weight(ONE_DAY) == pytest.approx(0.5, rel=1e-6)

    def test_exponential_at_two_half_lives(self):
        scorer = self._scorer(DecayFunction.EXPONENTIAL, half_life=ONE_DAY)
        assert scorer._decay_weight(2 * ONE_DAY) == pytest.approx(0.25, rel=1e-6)

    def test_linear_at_age_zero(self):
        scorer = self._scorer(DecayFunction.LINEAR, max_age=ONE_DAY)
        assert scorer._decay_weight(0) == pytest.approx(1.0)

    def test_linear_at_max_age_is_zero(self):
        scorer = self._scorer(DecayFunction.LINEAR, max_age=ONE_DAY)
        assert scorer._decay_weight(ONE_DAY) == pytest.approx(0.0, abs=1e-9)

    def test_linear_at_midpoint(self):
        scorer = self._scorer(DecayFunction.LINEAR, max_age=ONE_DAY)
        assert scorer._decay_weight(ONE_DAY / 2) == pytest.approx(0.5, rel=1e-6)

    def test_linear_beyond_max_age_is_zero(self):
        scorer = self._scorer(DecayFunction.LINEAR, max_age=ONE_DAY)
        assert scorer._decay_weight(2 * ONE_DAY) == 0.0

    def test_step_within_max_age(self):
        scorer = self._scorer(DecayFunction.STEP, max_age=ONE_DAY)
        assert scorer._decay_weight(ONE_DAY) == 1.0

    def test_step_beyond_max_age(self):
        scorer = self._scorer(DecayFunction.STEP, max_age=ONE_DAY)
        assert scorer._decay_weight(ONE_DAY + 1) == 0.0

    def test_negative_age_returns_one_for_all_functions(self):
        for fn in DecayFunction:
            scorer = self._scorer(fn)
            assert scorer._decay_weight(-100) == 1.0


# ---------------------------------------------------------------------------
# RelationStrengthScorer basic behavior
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRelationStrengthScorerBasic:
    """Core scorer behavior with real timestamps."""

    def _fresh_scorer(self, **cfg_kwargs):
        cfg = StrengthConfig(decay_function=DecayFunction.NONE, **cfg_kwargs)
        return RelationStrengthScorer(config=cfg)

    def test_empty_scorer_returns_zero_score(self):
        scorer = self._fresh_scorer()
        score = scorer.score("a", "b", now=NOW)
        assert score.raw_score == 0.0
        assert score.interaction_count == 0

    def test_single_interaction_counted(self):
        scorer = self._fresh_scorer()
        scorer.add_interaction(
            Interaction(source="a", target="b", interaction_type="msg", timestamp=NOW)
        )
        score = scorer.score("a", "b", now=NOW)
        assert score.interaction_count == 1

    def test_single_interaction_raw_score(self):
        scorer = self._fresh_scorer()
        scorer.add_interaction(
            Interaction(source="a", target="b", interaction_type="msg", timestamp=NOW, weight=2.0)
        )
        score = scorer.score("a", "b", now=NOW)
        assert score.raw_score == pytest.approx(2.0)

    def test_bidirectional_counted(self):
        """a->b and b->a interactions both count toward the pair."""
        scorer = self._fresh_scorer()
        scorer.add_interaction(
            Interaction(source="a", target="b", interaction_type="msg", timestamp=NOW)
        )
        scorer.add_interaction(
            Interaction(source="b", target="a", interaction_type="reply", timestamp=NOW)
        )
        score = scorer.score("a", "b", now=NOW)
        assert score.interaction_count == 2

    def test_type_weight_applied(self):
        cfg = StrengthConfig(
            decay_function=DecayFunction.NONE,
            type_weights={"meeting": 5.0},
        )
        scorer = RelationStrengthScorer(config=cfg)
        scorer.add_interaction(
            Interaction(source="a", target="b", interaction_type="meeting", timestamp=NOW)
        )
        score = scorer.score("a", "b", now=NOW)
        assert score.raw_score == pytest.approx(5.0)

    def test_unknown_type_defaults_to_weight_one(self):
        cfg = StrengthConfig(
            decay_function=DecayFunction.NONE,
            type_weights={"meeting": 5.0},
        )
        scorer = RelationStrengthScorer(config=cfg)
        scorer.add_interaction(
            Interaction(source="a", target="b", interaction_type="unknown_type", timestamp=NOW)
        )
        score = scorer.score("a", "b", now=NOW)
        assert score.raw_score == pytest.approx(1.0)

    def test_different_pairs_independent(self):
        scorer = self._fresh_scorer()
        scorer.add_interaction(
            Interaction(source="a", target="b", interaction_type="msg", timestamp=NOW)
        )
        score_ab = scorer.score("a", "b", now=NOW)
        score_ac = scorer.score("a", "c", now=NOW)
        assert score_ab.raw_score > 0
        assert score_ac.raw_score == 0.0

    def test_clear_removes_all_interactions(self):
        scorer = self._fresh_scorer()
        scorer.add_interaction(
            Interaction(source="a", target="b", interaction_type="msg", timestamp=NOW)
        )
        scorer.clear()
        assert scorer.interaction_count == 0
        score = scorer.score("a", "b", now=NOW)
        assert score.raw_score == 0.0


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRelationStrengthScorerEdgeCases:
    """Edge cases and boundary conditions."""

    def test_add_interactions_bulk(self):
        scorer = RelationStrengthScorer(config=StrengthConfig(decay_function=DecayFunction.NONE))
        interactions = [
            Interaction(source="a", target="b", interaction_type="msg", timestamp=NOW - i * 100)
            for i in range(5)
        ]
        scorer.add_interactions(interactions)
        assert scorer.interaction_count == 5

    def test_exponential_decay_reduces_score_over_time(self):
        half_life = ONE_DAY
        cfg = StrengthConfig(decay_function=DecayFunction.EXPONENTIAL, half_life=half_life)
        scorer = RelationStrengthScorer(config=cfg)
        scorer.add_interaction(
            Interaction(source="a", target="b", interaction_type="msg", timestamp=NOW - half_life)
        )
        score = scorer.score("a", "b", now=NOW)
        # One half-life ago => weight ~ 0.5, so raw_score ~ 0.5
        assert score.raw_score == pytest.approx(0.5, rel=1e-3)

    def test_min_score_clamps_to_zero(self):
        cfg = StrengthConfig(
            decay_function=DecayFunction.STEP,
            max_age=ONE_DAY,
            min_score=10.0,  # require > 10 to be non-zero
        )
        scorer = RelationStrengthScorer(config=cfg)
        # interaction within max_age but low weight => raw = 1.0 < min_score
        scorer.add_interaction(
            Interaction(source="a", target="b", interaction_type="msg", timestamp=NOW)
        )
        score = scorer.score("a", "b", now=NOW)
        assert score.raw_score == 0.0

    def test_latest_interaction_timestamp(self):
        scorer = RelationStrengthScorer(config=StrengthConfig(decay_function=DecayFunction.NONE))
        t1 = NOW - 100
        t2 = NOW - 10
        scorer.add_interaction(
            Interaction(source="a", target="b", interaction_type="msg", timestamp=t1)
        )
        scorer.add_interaction(
            Interaction(source="a", target="b", interaction_type="msg", timestamp=t2)
        )
        score = scorer.score("a", "b", now=NOW)
        assert score.latest_interaction == t2


# ---------------------------------------------------------------------------
# score_all normalized scoring
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestScoreAll:
    """score_all normalization behavior."""

    def test_empty_scorer_returns_empty_list(self):
        scorer = RelationStrengthScorer()
        assert scorer.score_all(now=NOW) == []

    def test_normalized_score_strongest_is_one(self):
        scorer = RelationStrengthScorer(config=StrengthConfig(decay_function=DecayFunction.NONE))
        scorer.add_interaction(
            Interaction(source="a", target="b", interaction_type="msg", timestamp=NOW, weight=10.0)
        )
        scorer.add_interaction(
            Interaction(source="a", target="c", interaction_type="msg", timestamp=NOW, weight=2.0)
        )
        scores = scorer.score_all(now=NOW)
        max_normalized = max(s.normalized_score for s in scores)
        assert max_normalized == pytest.approx(1.0)

    def test_results_sorted_by_raw_score_desc(self):
        scorer = RelationStrengthScorer(config=StrengthConfig(decay_function=DecayFunction.NONE))
        scorer.add_interaction(
            Interaction(source="a", target="b", interaction_type="msg", timestamp=NOW, weight=5.0)
        )
        scorer.add_interaction(
            Interaction(source="a", target="c", interaction_type="msg", timestamp=NOW, weight=1.0)
        )
        scores = scorer.score_all(now=NOW)
        raw_scores = [s.raw_score for s in scores]
        assert raw_scores == sorted(raw_scores, reverse=True)

    def test_all_pairs_covered(self):
        scorer = RelationStrengthScorer(config=StrengthConfig(decay_function=DecayFunction.NONE))
        scorer.add_interaction(
            Interaction(source="a", target="b", interaction_type="msg", timestamp=NOW)
        )
        scorer.add_interaction(
            Interaction(source="c", target="d", interaction_type="msg", timestamp=NOW)
        )
        scores = scorer.score_all(now=NOW)
        assert len(scores) == 2


# ---------------------------------------------------------------------------
# top_relations
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTopRelations:
    """top_relations top-N selection tests."""

    def _scorer_with_contacts(self):
        scorer = RelationStrengthScorer(config=StrengthConfig(decay_function=DecayFunction.NONE))
        for partner, weight in [("b", 5.0), ("c", 3.0), ("d", 1.0), ("e", 0.5)]:
            scorer.add_interaction(
                Interaction(
                    source="a",
                    target=partner,
                    interaction_type="msg",
                    timestamp=NOW,
                    weight=weight,
                )
            )
        return scorer

    def test_top_n_limits_results(self):
        scorer = self._scorer_with_contacts()
        top2 = scorer.top_relations("a", now=NOW, n=2)
        assert len(top2) <= 2

    def test_top_relations_sorted_desc(self):
        scorer = self._scorer_with_contacts()
        tops = scorer.top_relations("a", now=NOW, n=4)
        raw_scores = [s.raw_score for s in tops]
        assert raw_scores == sorted(raw_scores, reverse=True)

    def test_top_relation_is_strongest(self):
        scorer = self._scorer_with_contacts()
        tops = scorer.top_relations("a", now=NOW, n=1)
        assert tops[0].raw_score == pytest.approx(5.0)

    def test_entity_with_no_interactions_returns_empty(self):
        scorer = self._scorer_with_contacts()
        tops = scorer.top_relations("z", now=NOW, n=5)
        assert tops == []


# ---------------------------------------------------------------------------
# MCP tool: relations_score_strength
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRelationsMcpTool:
    """relations_score_strength MCP tool real behavior tests."""

    def test_success_status(self):
        from codomyrmex.relations.mcp_tools import relations_score_strength

        interactions = [
            {"type": "email", "timestamp": NOW - ONE_DAY, "weight": 1.0},
        ]
        result = relations_score_strength(
            source="alice",
            target="bob",
            interactions=interactions,
            decay_function="none",
            half_life_days=30.0,
        )
        assert result["status"] == "success"

    def test_result_fields_present(self):
        from codomyrmex.relations.mcp_tools import relations_score_strength

        interactions = [{"type": "msg", "timestamp": NOW, "weight": 2.0}]
        result = relations_score_strength(
            source="alice",
            target="bob",
            interactions=interactions,
            decay_function="none",
        )
        assert "source" in result
        assert "target" in result
        assert "raw_score" in result
        assert "interaction_count" in result

    def test_interaction_count_correct(self):
        from codomyrmex.relations.mcp_tools import relations_score_strength

        interactions = [
            {"type": "msg", "timestamp": NOW - 100, "weight": 1.0},
            {"type": "call", "timestamp": NOW - 200, "weight": 1.0},
        ]
        result = relations_score_strength(
            source="a",
            target="b",
            interactions=interactions,
            decay_function="none",
        )
        assert result["interaction_count"] == 2

    def test_no_interactions_score_zero(self):
        from codomyrmex.relations.mcp_tools import relations_score_strength

        result = relations_score_strength(
            source="a",
            target="b",
            interactions=[],
            decay_function="none",
        )
        assert result["status"] == "success"
        assert result["raw_score"] == pytest.approx(0.0)

    def test_invalid_decay_function_error(self):
        from codomyrmex.relations.mcp_tools import relations_score_strength

        result = relations_score_strength(
            source="a",
            target="b",
            interactions=[{"type": "msg", "timestamp": NOW}],
            decay_function="invalid_function",
        )
        assert result["status"] == "error"

    def test_source_target_in_result(self):
        from codomyrmex.relations.mcp_tools import relations_score_strength

        result = relations_score_strength(
            source="alice",
            target="bob",
            interactions=[{"type": "msg", "timestamp": NOW}],
            decay_function="none",
        )
        assert result["source"] == "alice"
        assert result["target"] == "bob"
