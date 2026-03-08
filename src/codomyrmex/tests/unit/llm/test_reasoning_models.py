"""Tests for llm.models.reasoning."""

import json

from codomyrmex.llm.models.reasoning import (
    DEPTH_TO_STEPS,
    Conclusion,
    ReasoningStep,
    ReasoningTrace,
    ThinkingDepth,
)


class TestThinkingDepth:
    def test_all_values(self):
        values = {d.value for d in ThinkingDepth}
        assert "shallow" in values
        assert "normal" in values
        assert "deep" in values
        assert "exhaustive" in values

    def test_str_enum_equals_string(self):
        assert ThinkingDepth.NORMAL == "normal"


class TestDepthToSteps:
    def test_shallow_is_1(self):
        assert DEPTH_TO_STEPS[ThinkingDepth.SHALLOW] == 1

    def test_normal_is_3(self):
        assert DEPTH_TO_STEPS[ThinkingDepth.NORMAL] == 3

    def test_deep_is_5(self):
        assert DEPTH_TO_STEPS[ThinkingDepth.DEEP] == 5

    def test_exhaustive_is_8(self):
        assert DEPTH_TO_STEPS[ThinkingDepth.EXHAUSTIVE] == 8

    def test_all_depths_covered(self):
        for depth in ThinkingDepth:
            assert depth in DEPTH_TO_STEPS


class TestReasoningStep:
    def test_construction(self):
        step = ReasoningStep(thought="The sky is blue due to Rayleigh scattering.")
        assert step.thought == "The sky is blue due to Rayleigh scattering."
        assert step.confidence == 0.5
        assert step.step_type == "reasoning"

    def test_confidence_clamped_high(self):
        step = ReasoningStep(thought="t", confidence=2.0)
        assert step.confidence == 1.0

    def test_confidence_clamped_low(self):
        step = ReasoningStep(thought="t", confidence=-0.5)
        assert step.confidence == 0.0

    def test_step_id_auto_generated(self):
        step = ReasoningStep(thought="t")
        assert len(step.step_id) == 12

    def test_step_id_unique(self):
        s1 = ReasoningStep(thought="a")
        s2 = ReasoningStep(thought="b")
        assert s1.step_id != s2.step_id

    def test_timestamp_auto_set(self):
        step = ReasoningStep(thought="t")
        assert "T" in step.timestamp  # ISO format

    def test_to_dict(self):
        step = ReasoningStep(
            thought="Hypothesis: cause is X.",
            confidence=0.8,
            evidence=["Fact A", "Fact B"],
            step_type="hypothesis",
        )
        d = step.to_dict()
        assert d["thought"] == "Hypothesis: cause is X."
        assert d["confidence"] == 0.8
        assert d["evidence"] == ["Fact A", "Fact B"]
        assert d["step_type"] == "hypothesis"

    def test_from_dict(self):
        step = ReasoningStep(thought="original", confidence=0.7)
        d = step.to_dict()
        restored = ReasoningStep.from_dict(d)
        assert restored.thought == "original"
        assert restored.confidence == 0.7
        assert restored.step_id == step.step_id

    def test_from_dict_defaults(self):
        step = ReasoningStep.from_dict({"thought": "minimal"})
        assert step.thought == "minimal"
        assert step.confidence == 0.5
        assert step.evidence == []

    def test_independent_default_evidence(self):
        s1 = ReasoningStep(thought="a")
        s2 = ReasoningStep(thought="b")
        s1.evidence.append("evidence")
        assert s2.evidence == []


class TestConclusion:
    def test_construction(self):
        c = Conclusion(action="Proceed", justification="All checks pass.")
        assert c.action == "Proceed"
        assert c.justification == "All checks pass."
        assert c.confidence == 0.5

    def test_confidence_clamped_high(self):
        c = Conclusion(action="a", justification="j", confidence=1.5)
        assert c.confidence == 1.0

    def test_confidence_clamped_low(self):
        c = Conclusion(action="a", justification="j", confidence=-0.1)
        assert c.confidence == 0.0

    def test_to_dict(self):
        c = Conclusion(
            action="Refactor",
            justification="Technical debt is high.",
            confidence=0.9,
            alternatives=["Wait", "Rewrite"],
            risks=["May break API"],
        )
        d = c.to_dict()
        assert d["action"] == "Refactor"
        assert d["confidence"] == 0.9
        assert "Wait" in d["alternatives"]
        assert "May break API" in d["risks"]

    def test_from_dict(self):
        c = Conclusion(action="Deploy", justification="Tests pass.", confidence=0.85)
        d = c.to_dict()
        restored = Conclusion.from_dict(d)
        assert restored.action == "Deploy"
        assert restored.confidence == 0.85

    def test_from_dict_defaults(self):
        c = Conclusion.from_dict({"action": "Skip", "justification": "Low priority"})
        assert c.action == "Skip"
        assert c.confidence == 0.5
        assert c.alternatives == []

    def test_independent_default_risks(self):
        c1 = Conclusion(action="a", justification="j")
        c2 = Conclusion(action="b", justification="k")
        c1.risks.append("risk")
        assert c2.risks == []


class TestReasoningTrace:
    def test_empty_trace(self):
        trace = ReasoningTrace()
        assert trace.step_count == 0
        assert trace.is_complete is False
        assert trace.mean_confidence == 0.0

    def test_trace_id_auto_generated(self):
        t = ReasoningTrace()
        assert len(t.trace_id) == 32  # uuid4().hex

    def test_add_step(self):
        trace = ReasoningTrace()
        step = ReasoningStep(thought="Step 1", confidence=0.8)
        trace.add_step(step)
        assert trace.step_count == 1
        assert abs(trace.total_confidence - 0.8) < 1e-9

    def test_add_multiple_steps(self):
        trace = ReasoningTrace()
        trace.add_step(ReasoningStep(thought="s1", confidence=0.6))
        trace.add_step(ReasoningStep(thought="s2", confidence=0.8))
        assert trace.step_count == 2
        assert abs(trace.mean_confidence - 0.7) < 1e-9

    def test_set_conclusion(self):
        trace = ReasoningTrace()
        trace.add_step(ReasoningStep(thought="analysis", confidence=0.8))
        c = Conclusion(action="Go", justification="OK", confidence=0.9)
        trace.set_conclusion(c)
        assert trace.is_complete is True
        assert trace.conclusion.action == "Go"

    def test_set_conclusion_updates_confidence(self):
        trace = ReasoningTrace()
        trace.add_step(ReasoningStep(thought="s1", confidence=0.6))
        c = Conclusion(action="x", justification="y", confidence=0.9)
        trace.set_conclusion(c)
        # 0.6 * 0.7 + 0.9 * 0.3 = 0.42 + 0.27 = 0.69
        assert abs(trace.total_confidence - 0.69) < 1e-6

    def test_to_dict(self):
        trace = ReasoningTrace(prompt="What is 2+2?", depth=ThinkingDepth.SHALLOW)
        step = ReasoningStep(thought="It equals 4.", confidence=1.0)
        trace.add_step(step)
        d = trace.to_dict()
        assert d["prompt"] == "What is 2+2?"
        assert d["depth"] == "shallow"
        assert d["step_count"] == 1
        assert len(d["steps"]) == 1
        assert d["is_complete"] is False

    def test_to_dict_with_conclusion(self):
        trace = ReasoningTrace()
        trace.set_conclusion(Conclusion(action="Done", justification="j", confidence=0.9))
        d = trace.to_dict()
        assert d["is_complete"] is True
        assert "conclusion" in d
        assert d["conclusion"]["action"] == "Done"

    def test_from_dict_roundtrip(self):
        trace = ReasoningTrace(prompt="Test", depth=ThinkingDepth.DEEP)
        trace.add_step(ReasoningStep(thought="step1", confidence=0.75))
        trace.set_conclusion(Conclusion(action="OK", justification="all good", confidence=0.8))
        d = trace.to_dict()
        restored = ReasoningTrace.from_dict(d)
        assert restored.prompt == "Test"
        assert restored.depth == ThinkingDepth.DEEP
        assert len(restored.steps) == 1
        assert restored.steps[0].thought == "step1"
        assert restored.conclusion is not None
        assert restored.conclusion.action == "OK"

    def test_to_json_roundtrip(self):
        trace = ReasoningTrace(prompt="JSON test")
        trace.add_step(ReasoningStep(thought="thinking", confidence=0.6))
        json_str = trace.to_json()
        parsed = json.loads(json_str)
        assert parsed["prompt"] == "JSON test"
        restored = ReasoningTrace.from_json(json_str)
        assert restored.prompt == "JSON test"
        assert restored.step_count == 1

    def test_from_dict_no_conclusion(self):
        trace = ReasoningTrace()
        d = trace.to_dict()
        # conclusion key should not be present if None
        assert "conclusion" not in d
        restored = ReasoningTrace.from_dict(d)
        assert restored.conclusion is None

    def test_independent_default_steps(self):
        t1 = ReasoningTrace()
        t2 = ReasoningTrace()
        t1.add_step(ReasoningStep(thought="x"))
        assert t2.step_count == 0

    def test_default_depth(self):
        trace = ReasoningTrace()
        assert trace.depth == ThinkingDepth.NORMAL
