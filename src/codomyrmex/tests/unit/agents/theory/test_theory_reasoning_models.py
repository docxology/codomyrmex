"""Zero-mock tests for codomyrmex.agents.theory.reasoning_models.

Covers:
  - ReasoningType enum values and membership
  - ReasoningModel ABC cannot be instantiated directly
  - SymbolicReasoningModel: construction, defaults, add_rule, add_fact,
    reason(), _apply_rule() indirectly, explain()
  - NeuralReasoningModel: construction, defaults, learn_pattern, reason(),
    _match_pattern() indirectly, explain()
  - HybridReasoningModel: construction, delegation to symbolic/neural,
    reason() structure, explain() structure
  - Edge cases: empty premises, missing facts, overlapping facts/premises,
    independent mutable defaults, operator coverage
"""

import pytest

from codomyrmex.agents.theory.reasoning_models import (
    HybridReasoningModel,
    NeuralReasoningModel,
    ReasoningModel,
    ReasoningType,
    SymbolicReasoningModel,
)

# ===========================================================================
# ReasoningType
# ===========================================================================


class TestReasoningType:
    """Enum membership and string values."""

    def test_has_three_members(self):
        assert len(ReasoningType) == 3

    def test_symbolic_value(self):
        assert ReasoningType.SYMBOLIC.value == "symbolic"

    def test_neural_value(self):
        assert ReasoningType.NEURAL.value == "neural"

    def test_hybrid_value(self):
        assert ReasoningType.HYBRID.value == "hybrid"

    def test_members_are_distinct(self):
        members = list(ReasoningType)
        assert len({m.value for m in members}) == 3

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("SYMBOLIC", ReasoningType.SYMBOLIC),
            ("NEURAL", ReasoningType.NEURAL),
            ("HYBRID", ReasoningType.HYBRID),
        ],
    )
    def test_lookup_by_name(self, name, expected):
        assert ReasoningType[name] is expected


# ===========================================================================
# ReasoningModel ABC
# ===========================================================================


class TestReasoningModelABC:
    """Abstract base class cannot be instantiated directly."""

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            ReasoningModel("x", ReasoningType.SYMBOLIC)  # type: ignore[abstract]


# ===========================================================================
# SymbolicReasoningModel — construction and defaults
# ===========================================================================


class TestSymbolicReasoningModelConstruction:
    """Construction, name, type, and mutable defaults."""

    def test_default_name(self):
        m = SymbolicReasoningModel()
        assert m.name == "symbolic"

    def test_custom_name(self):
        m = SymbolicReasoningModel(name="logic_engine")
        assert m.name == "logic_engine"

    def test_reasoning_type_is_symbolic(self):
        m = SymbolicReasoningModel()
        assert m.reasoning_type is ReasoningType.SYMBOLIC

    def test_rules_start_empty(self):
        m = SymbolicReasoningModel()
        assert m.rules == []

    def test_facts_start_empty(self):
        m = SymbolicReasoningModel()
        assert m.facts == {}

    def test_independent_rules_default(self):
        """Two instances must not share the same rules list."""
        a = SymbolicReasoningModel()
        b = SymbolicReasoningModel()
        a.add_rule({"conditions": [], "conclusion": {"x": 1}})
        assert b.rules == []

    def test_independent_facts_default(self):
        """Two instances must not share the same facts dict."""
        a = SymbolicReasoningModel()
        b = SymbolicReasoningModel()
        a.add_fact("temperature", 100)
        assert "temperature" not in b.facts


# ===========================================================================
# SymbolicReasoningModel — add_rule / add_fact
# ===========================================================================


class TestSymbolicReasoningModelMutation:
    def test_add_rule_appends(self):
        m = SymbolicReasoningModel()
        rule = {"conditions": [{"fact": "x", "operator": "==", "value": 1}], "conclusion": {"result": "yes"}}
        m.add_rule(rule)
        assert len(m.rules) == 1
        assert m.rules[0] is rule

    def test_add_multiple_rules(self):
        m = SymbolicReasoningModel()
        m.add_rule({"conditions": [], "conclusion": {"a": 1}})
        m.add_rule({"conditions": [], "conclusion": {"b": 2}})
        assert len(m.rules) == 2

    def test_add_fact_stores_value(self):
        m = SymbolicReasoningModel()
        m.add_fact("sky_color", "blue")
        assert m.facts["sky_color"] == "blue"

    def test_add_fact_overwrites(self):
        m = SymbolicReasoningModel()
        m.add_fact("count", 1)
        m.add_fact("count", 2)
        assert m.facts["count"] == 2


# ===========================================================================
# SymbolicReasoningModel — reason()
# ===========================================================================


class TestSymbolicReasoningModelReason:
    def test_reason_result_keys(self):
        m = SymbolicReasoningModel()
        result = m.reason({"x": 1})
        assert "premises" in result
        assert "knowledge" in result
        assert "conclusions" in result
        assert "reasoning_type" in result

    def test_reason_type_is_symbolic(self):
        m = SymbolicReasoningModel()
        result = m.reason({})
        assert result["reasoning_type"] == "symbolic"

    def test_reason_no_rules_no_conclusions(self):
        m = SymbolicReasoningModel()
        result = m.reason({"a": 1})
        assert result["conclusions"] == []

    def test_reason_merges_facts_and_premises(self):
        m = SymbolicReasoningModel()
        m.add_fact("base", True)
        result = m.reason({"extra": 42})
        assert result["knowledge"]["base"] is True
        assert result["knowledge"]["extra"] == 42

    def test_reason_premises_override_facts(self):
        """Premises win when the same key appears in both."""
        m = SymbolicReasoningModel()
        m.add_fact("val", 1)
        result = m.reason({"val": 99})
        assert result["knowledge"]["val"] == 99

    def test_reason_rule_fires_on_equality(self):
        m = SymbolicReasoningModel()
        rule = {
            "conditions": [{"fact": "status", "operator": "==", "value": "active"}],
            "conclusion": {"action": "process"},
        }
        m.add_rule(rule)
        result = m.reason({"status": "active"})
        assert {"action": "process"} in result["conclusions"]

    def test_reason_rule_does_not_fire_when_condition_fails(self):
        m = SymbolicReasoningModel()
        rule = {
            "conditions": [{"fact": "status", "operator": "==", "value": "active"}],
            "conclusion": {"action": "process"},
        }
        m.add_rule(rule)
        result = m.reason({"status": "inactive"})
        assert result["conclusions"] == []

    def test_reason_rule_not_equal_operator(self):
        m = SymbolicReasoningModel()
        rule = {
            "conditions": [{"fact": "flag", "operator": "!=", "value": False}],
            "conclusion": {"result": "ok"},
        }
        m.add_rule(rule)
        result = m.reason({"flag": True})
        assert {"result": "ok"} in result["conclusions"]

    def test_reason_rule_greater_than_operator(self):
        m = SymbolicReasoningModel()
        rule = {
            "conditions": [{"fact": "score", "operator": ">", "value": 50}],
            "conclusion": {"grade": "pass"},
        }
        m.add_rule(rule)
        result = m.reason({"score": 75})
        assert {"grade": "pass"} in result["conclusions"]

    def test_reason_rule_less_than_operator(self):
        m = SymbolicReasoningModel()
        rule = {
            "conditions": [{"fact": "temp", "operator": "<", "value": 0}],
            "conclusion": {"state": "frozen"},
        }
        m.add_rule(rule)
        result = m.reason({"temp": -5})
        assert {"state": "frozen"} in result["conclusions"]

    def test_reason_rule_missing_fact_does_not_fire(self):
        m = SymbolicReasoningModel()
        rule = {
            "conditions": [{"fact": "absent_fact", "operator": "==", "value": 1}],
            "conclusion": {"x": 1},
        }
        m.add_rule(rule)
        result = m.reason({})
        assert result["conclusions"] == []

    def test_reason_multiple_rules_some_fire(self):
        m = SymbolicReasoningModel()
        m.add_rule({
            "conditions": [{"fact": "a", "operator": "==", "value": 1}],
            "conclusion": {"fired": "rule1"},
        })
        m.add_rule({
            "conditions": [{"fact": "b", "operator": "==", "value": 2}],
            "conclusion": {"fired": "rule2"},
        })
        result = m.reason({"a": 1, "b": 99})
        assert len(result["conclusions"]) == 1
        assert {"fired": "rule1"} in result["conclusions"]

    def test_reason_empty_conditions_rule_always_fires(self):
        m = SymbolicReasoningModel()
        m.add_rule({"conditions": [], "conclusion": {"always": True}})
        result = m.reason({})
        assert {"always": True} in result["conclusions"]


# ===========================================================================
# SymbolicReasoningModel — explain()
# ===========================================================================


class TestSymbolicReasoningModelExplain:
    def test_explain_returns_string(self):
        m = SymbolicReasoningModel()
        result = m.reason({"x": 1})
        explanation = m.explain(result)
        assert isinstance(explanation, str)

    def test_explain_mentions_premises(self):
        m = SymbolicReasoningModel()
        result = m.reason({"color": "red"})
        explanation = m.explain(result)
        assert "color" in explanation or "premises" in explanation.lower()

    def test_explain_mentions_rule_count(self):
        m = SymbolicReasoningModel()
        m.add_rule({"conditions": [], "conclusion": {}})
        result = m.reason({})
        explanation = m.explain(result)
        assert "1" in explanation

    def test_explain_mentions_conclusions(self):
        m = SymbolicReasoningModel()
        m.add_rule({"conditions": [], "conclusion": {"tag": "hit"}})
        result = m.reason({})
        explanation = m.explain(result)
        assert "1" in explanation  # 1 conclusion derived


# ===========================================================================
# NeuralReasoningModel — construction and defaults
# ===========================================================================


class TestNeuralReasoningModelConstruction:
    def test_default_name(self):
        m = NeuralReasoningModel()
        assert m.name == "neural"

    def test_custom_name(self):
        m = NeuralReasoningModel(name="pattern_net")
        assert m.name == "pattern_net"

    def test_reasoning_type_is_neural(self):
        m = NeuralReasoningModel()
        assert m.reasoning_type is ReasoningType.NEURAL

    def test_patterns_start_empty(self):
        m = NeuralReasoningModel()
        assert m.patterns == {}

    def test_independent_patterns_default(self):
        a = NeuralReasoningModel()
        b = NeuralReasoningModel()
        a.learn_pattern("p1", {"key": "val"})
        assert "p1" not in b.patterns


# ===========================================================================
# NeuralReasoningModel — learn_pattern / reason()
# ===========================================================================


class TestNeuralReasoningModelBehavior:
    def test_learn_pattern_stores(self):
        m = NeuralReasoningModel()
        m.learn_pattern("spam_detector", {"subject": "win"})
        assert "spam_detector" in m.patterns
        assert m.patterns["spam_detector"] == {"subject": "win"}

    def test_reason_result_keys(self):
        m = NeuralReasoningModel()
        result = m.reason({"a": 1})
        assert "premises" in result
        assert "matched_patterns" in result
        assert "reasoning_type" in result

    def test_reason_type_is_neural(self):
        m = NeuralReasoningModel()
        result = m.reason({})
        assert result["reasoning_type"] == "neural"

    def test_reason_no_patterns_no_matches(self):
        m = NeuralReasoningModel()
        result = m.reason({"x": 1})
        assert result["matched_patterns"] == []

    def test_reason_pattern_matches_when_keys_present(self):
        m = NeuralReasoningModel()
        m.learn_pattern("greet", {"hello": None, "world": None})
        result = m.reason({"hello": "there", "world": "earth", "extra": 99})
        assert "greet" in result["matched_patterns"]

    def test_reason_pattern_no_match_missing_key(self):
        m = NeuralReasoningModel()
        m.learn_pattern("greet", {"hello": None, "world": None})
        result = m.reason({"hello": "there"})  # "world" missing
        assert "greet" not in result["matched_patterns"]

    def test_reason_non_dict_pattern_never_matches(self):
        m = NeuralReasoningModel()
        m.learn_pattern("bad_pattern", ["list", "not", "dict"])
        result = m.reason({"list": 1})
        assert "bad_pattern" not in result["matched_patterns"]

    def test_reason_multiple_patterns_selective_match(self):
        m = NeuralReasoningModel()
        m.learn_pattern("p_ab", {"a": None, "b": None})
        m.learn_pattern("p_c", {"c": None})
        result = m.reason({"a": 1, "b": 2})
        assert "p_ab" in result["matched_patterns"]
        assert "p_c" not in result["matched_patterns"]

    def test_explain_returns_string(self):
        m = NeuralReasoningModel()
        result = m.reason({})
        explanation = m.explain(result)
        assert isinstance(explanation, str)

    def test_explain_mentions_matched_count(self):
        m = NeuralReasoningModel()
        m.learn_pattern("p1", {"x": None})
        result = m.reason({"x": 42})
        explanation = m.explain(result)
        assert "1" in explanation


# ===========================================================================
# HybridReasoningModel
# ===========================================================================


class TestHybridReasoningModelConstruction:
    def test_default_name(self):
        m = HybridReasoningModel()
        assert m.name == "hybrid"

    def test_custom_name(self):
        m = HybridReasoningModel(name="combo")
        assert m.name == "combo"

    def test_reasoning_type_is_hybrid(self):
        m = HybridReasoningModel()
        assert m.reasoning_type is ReasoningType.HYBRID

    def test_has_symbolic_sublayer(self):
        m = HybridReasoningModel()
        assert isinstance(m.symbolic, SymbolicReasoningModel)

    def test_has_neural_sublayer(self):
        m = HybridReasoningModel()
        assert isinstance(m.neural, NeuralReasoningModel)

    def test_sublayers_are_independent_instances(self):
        a = HybridReasoningModel()
        b = HybridReasoningModel()
        a.symbolic.add_fact("x", 1)
        assert "x" not in b.symbolic.facts


class TestHybridReasoningModelReason:
    def test_reason_result_keys(self):
        m = HybridReasoningModel()
        result = m.reason({"p": 1})
        assert "premises" in result
        assert "symbolic" in result
        assert "neural" in result
        assert "reasoning_type" in result

    def test_reason_type_is_hybrid(self):
        m = HybridReasoningModel()
        result = m.reason({})
        assert result["reasoning_type"] == "hybrid"

    def test_reason_delegates_symbolic(self):
        m = HybridReasoningModel()
        m.symbolic.add_rule({"conditions": [], "conclusion": {"sym": "fired"}})
        result = m.reason({})
        assert result["symbolic"]["reasoning_type"] == "symbolic"
        assert {"sym": "fired"} in result["symbolic"]["conclusions"]

    def test_reason_delegates_neural(self):
        m = HybridReasoningModel()
        m.neural.learn_pattern("np1", {"key": None})
        result = m.reason({"key": "val"})
        assert result["neural"]["reasoning_type"] == "neural"
        assert "np1" in result["neural"]["matched_patterns"]

    def test_reason_premises_passed_to_both_layers(self):
        m = HybridReasoningModel()
        result = m.reason({"input": 42})
        assert result["symbolic"]["premises"] == {"input": 42}
        assert result["neural"]["premises"] == {"input": 42}

    def test_explain_returns_string(self):
        m = HybridReasoningModel()
        result = m.reason({})
        explanation = m.explain(result)
        assert isinstance(explanation, str)

    def test_explain_contains_both_sections(self):
        m = HybridReasoningModel()
        result = m.reason({})
        explanation = m.explain(result)
        assert "Symbolic" in explanation
        assert "Neural" in explanation
