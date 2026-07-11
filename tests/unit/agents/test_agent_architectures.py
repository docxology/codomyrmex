"""
Unit tests for agents.theory.agent_architectures — Zero-Mock compliant.

Covers: ArchitectureType, ReactiveArchitecture (add_rule/perceive/decide/act),
KnowledgeBase (add/get/remove/clear/has/list/query), DeliberativeArchitecture
(set_goal/plan/perceive/decide/act), HybridArchitecture (perceive/decide/act).
"""

import pytest

from codomyrmex.agents.theory.agent_architectures import (
    ArchitectureType,
    DeliberativeArchitecture,
    HybridArchitecture,
    KnowledgeBase,
    ReactiveArchitecture,
)

# ── ArchitectureType enum ─────────────────────────────────────────────


@pytest.mark.unit
class TestArchitectureType:
    def test_values(self):
        assert ArchitectureType.REACTIVE.value == "reactive"
        assert ArchitectureType.DELIBERATIVE.value == "deliberative"
        assert ArchitectureType.HYBRID.value == "hybrid"

    def test_three_types(self):
        assert len(list(ArchitectureType)) == 3


# ── ReactiveArchitecture ──────────────────────────────────────────────


@pytest.mark.unit
class TestReactiveArchitecture:
    def test_default_name(self):
        r = ReactiveArchitecture()
        assert r.name == "reactive"

    def test_architecture_type(self):
        r = ReactiveArchitecture()
        assert r.architecture_type == ArchitectureType.REACTIVE

    def test_starts_empty_rules(self):
        r = ReactiveArchitecture()
        assert r.rules == []

    def test_add_rule_appended(self):
        r = ReactiveArchitecture()
        r.add_rule(lambda env: True, lambda env: {"action": "go"})
        assert len(r.rules) == 1

    def test_add_multiple_rules(self):
        r = ReactiveArchitecture()
        for _ in range(3):
            r.add_rule(lambda env: False, lambda env: {})
        assert len(r.rules) == 3

    def test_perceive_passthrough(self):
        r = ReactiveArchitecture()
        env = {"x": 1, "y": 2}
        assert r.perceive(env) == env

    def test_decide_first_matching_rule(self):
        r = ReactiveArchitecture()
        r.add_rule(lambda env: False, lambda env: {"result": "first"})
        r.add_rule(lambda env: True, lambda env: {"result": "second"})
        decision = r.decide({"sensor": 5})
        # Action should be the lambda that returns {"result": "second"}
        assert decision["action"] is not None

    def test_decide_no_match_returns_none_action(self):
        r = ReactiveArchitecture()
        r.add_rule(lambda env: False, lambda env: {"result": "x"})
        decision = r.decide({"val": 1})
        assert decision["action"] is None

    def test_decide_no_rules_returns_none_action(self):
        r = ReactiveArchitecture()
        decision = r.decide({})
        assert decision["action"] is None

    def test_act_calls_action_function(self):
        r = ReactiveArchitecture()

        def my_action(args):
            return {"done": args.get("x")}

        decision = {"action": my_action, "args": {"x": 42}}
        result = r.act(decision)
        assert result["done"] == 42

    def test_act_no_action_returns_no_action(self):
        r = ReactiveArchitecture()
        result = r.act({"action": None})
        assert result == {"result": "no_action"}

    def test_full_perceive_decide_act_cycle(self):
        r = ReactiveArchitecture()

        def is_hot(env):
            return env.get("temp", 0) > 30

        def cool_down(args):
            return {"action": "turn_on_ac"}

        r.add_rule(is_hot, cool_down)

        perception = r.perceive({"temp": 35})
        decision = r.decide(perception)
        result = r.act(decision)
        assert result["action"] == "turn_on_ac"


# ── KnowledgeBase ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestKnowledgeBase:
    def test_starts_empty(self):
        kb = KnowledgeBase()
        assert kb.facts == {}

    def test_add_and_get_fact(self):
        kb = KnowledgeBase()
        kb.add_fact("color", "blue")
        assert kb.get_fact("color") == "blue"

    def test_get_missing_returns_none(self):
        kb = KnowledgeBase()
        assert kb.get_fact("ghost") is None

    def test_overwrite_fact(self):
        kb = KnowledgeBase()
        kb.add_fact("x", 1)
        kb.add_fact("x", 2)
        assert kb.get_fact("x") == 2

    def test_remove_existing_fact(self):
        kb = KnowledgeBase()
        kb.add_fact("k", "v")
        result = kb.remove_fact("k")
        assert result is True
        assert kb.get_fact("k") is None

    def test_remove_missing_fact_returns_false(self):
        kb = KnowledgeBase()
        assert kb.remove_fact("nonexistent") is False

    def test_clear_removes_all(self):
        kb = KnowledgeBase()
        kb.add_fact("a", 1)
        kb.add_fact("b", 2)
        kb.clear()
        assert kb.facts == {}

    def test_has_fact_true(self):
        kb = KnowledgeBase()
        kb.add_fact("key", "val")
        assert kb.has_fact("key") is True

    def test_has_fact_false(self):
        kb = KnowledgeBase()
        assert kb.has_fact("missing") is False

    def test_list_facts_empty(self):
        kb = KnowledgeBase()
        assert kb.list_facts() == []

    def test_list_facts_returns_keys(self):
        kb = KnowledgeBase()
        kb.add_fact("a", 1)
        kb.add_fact("b", 2)
        keys = kb.list_facts()
        assert set(keys) == {"a", "b"}

    def test_query_with_custom_function(self):
        kb = KnowledgeBase()
        kb.add_fact("score", 95)
        kb.add_fact("level", 3)
        result = kb.query(lambda facts: sum(facts.values()))
        assert result == 98

    def test_query_filter(self):
        kb = KnowledgeBase()
        kb.add_fact("x", 10)
        kb.add_fact("y", 20)
        result = kb.query(lambda facts: {k: v for k, v in facts.items() if v > 15})
        assert result == {"y": 20}


# ── DeliberativeArchitecture ──────────────────────────────────────────


@pytest.mark.unit
class TestDeliberativeArchitecture:
    def test_default_name(self):
        d = DeliberativeArchitecture()
        assert d.name == "deliberative"

    def test_architecture_type(self):
        d = DeliberativeArchitecture()
        assert d.architecture_type == ArchitectureType.DELIBERATIVE

    def test_starts_no_goals(self):
        d = DeliberativeArchitecture()
        assert d.goals == []

    def test_set_goal_appends(self):
        d = DeliberativeArchitecture()
        d.set_goal({"type": "reach", "target": "B"})
        assert len(d.goals) == 1

    def test_set_multiple_goals(self):
        d = DeliberativeArchitecture()
        d.set_goal({"id": 1})
        d.set_goal({"id": 2})
        assert len(d.goals) == 2

    def test_plan_returns_list(self):
        d = DeliberativeArchitecture()
        goal = {"type": "simple", "target": "X"}
        plan = d.plan(goal, {"position": "A"})
        assert isinstance(plan, list)
        assert len(plan) > 0

    def test_plan_complex_goal(self):
        d = DeliberativeArchitecture()
        goal = {"type": "complex"}
        plan = d.plan(goal, {})
        assert any(step["action"] == "decompose_goal" for step in plan)

    def test_plan_simple_goal(self):
        d = DeliberativeArchitecture()
        goal = {"type": "simple"}
        plan = d.plan(goal, {})
        assert any(step["action"] == "achieve_goal" for step in plan)

    def test_plan_stores_state_in_kb(self):
        d = DeliberativeArchitecture()
        d.plan({"type": "x"}, {"temp": 30})
        assert d.kb.has_fact("state_temp")

    def test_perceive_updates_kb(self):
        d = DeliberativeArchitecture()
        d.perceive({"weather": "sunny"})
        assert d.kb.has_fact("weather")

    def test_perceive_returns_raw_and_interpreted(self):
        d = DeliberativeArchitecture()
        p = d.perceive({"a": 1})
        assert "raw" in p
        assert "interpreted" in p
        assert p["raw"] == {"a": 1}

    def test_decide_no_goals_returns_none(self):
        d = DeliberativeArchitecture()
        p = d.perceive({})
        dec = d.decide(p)
        assert dec["action"] is None
        assert dec["plan"] == []

    def test_decide_with_goal_returns_action(self):
        d = DeliberativeArchitecture()
        d.set_goal({"type": "simple"})
        p = d.perceive({"state": "start"})
        dec = d.decide(p)
        assert dec["action"] is not None
        assert "plan" in dec

    def test_act_with_action(self):
        d = DeliberativeArchitecture()
        action = {"action_type": "move"}
        result = d.act({"action": action})
        assert result["result"] == "executed"
        assert result["action"] == action

    def test_act_no_action(self):
        d = DeliberativeArchitecture()
        result = d.act({"action": None})
        assert result["result"] == "no_action"


# ── HybridArchitecture ────────────────────────────────────────────────


@pytest.mark.unit
class TestHybridArchitecture:
    def test_default_name(self):
        h = HybridArchitecture()
        assert h.name == "hybrid"

    def test_architecture_type(self):
        h = HybridArchitecture()
        assert h.architecture_type == ArchitectureType.HYBRID

    def test_has_reactive_and_deliberative_layers(self):
        h = HybridArchitecture()
        assert isinstance(h.reactive, ReactiveArchitecture)
        assert isinstance(h.deliberative, DeliberativeArchitecture)

    def test_perceive_returns_both_layers(self):
        h = HybridArchitecture()
        p = h.perceive({"sensor": 7})
        assert "reactive" in p
        assert "deliberative" in p

    def test_decide_uses_reactive_when_rule_matches(self):
        h = HybridArchitecture()

        def always_true(env):
            return True

        def action(args):
            return {"done": True}

        h.reactive.add_rule(always_true, action)
        p = h.perceive({"val": 1})
        dec = h.decide(p)
        assert dec["action"] is not None
        assert h.mode == "reactive"

    def test_decide_falls_back_to_deliberative(self):
        h = HybridArchitecture()
        # No reactive rules → falls back to deliberative
        p = h.perceive({})
        h.decide(p)
        assert h.mode == "deliberative"

    def test_act_reactive_mode(self):
        h = HybridArchitecture()

        def true_cond(env):
            return True

        def answer_action(args):
            return {"mode": "reactive_result"}

        h.reactive.add_rule(true_cond, answer_action)
        p = h.perceive({"x": 1})
        dec = h.decide(p)
        result = h.act(dec)
        assert result["mode"] == "reactive_result"

    def test_act_deliberative_mode(self):
        h = HybridArchitecture()
        h.deliberative.set_goal({"type": "simple"})
        p = h.perceive({"start": "here"})
        dec = h.decide(p)
        # After decide with no reactive rules, mode should be deliberative
        result = h.act(dec)
        # Deliberative act returns {"result": "executed", ...} or {"result": "no_action"}
        assert "result" in result
