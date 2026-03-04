"""Tests for llm/models/reasoning.py and llm/chain_of_thought.py."""

from __future__ import annotations

import pytest

from codomyrmex.llm.chain_of_thought import (
    ChainOfThought,
    StructuralConclusionSynthesizer,
    StructuralStepGenerator,
)
from codomyrmex.llm.models.reasoning import (
    DEPTH_TO_STEPS,
    Conclusion,
    ReasoningStep,
    ReasoningTrace,
    ThinkingDepth,
)

# ── ReasoningStep ─────────────────────────────────────────────────


class TestReasoningStep:
    """Test suite for ReasoningStep."""
    def test_create_basic(self) -> None:
        """Verify create basic behavior."""
        step = ReasoningStep(thought="Analyze the input")
        assert step.thought == "Analyze the input"
        assert step.confidence == 0.5
        assert step.evidence == []
        assert step.step_type == "reasoning"
        assert step.step_id  # non-empty

    def test_confidence_clamped(self) -> None:
        """Verify confidence clamped behavior."""
        step = ReasoningStep(thought="x", confidence=1.5)
        assert step.confidence == 1.0
        step2 = ReasoningStep(thought="x", confidence=-0.5)
        assert step2.confidence == 0.0

    def test_serialization_roundtrip(self) -> None:
        """Verify serialization roundtrip behavior."""
        step = ReasoningStep(
            thought="Check boundaries",
            confidence=0.8,
            evidence=["Input validated"],
            step_type="verification",
        )
        d = step.to_dict()
        restored = ReasoningStep.from_dict(d)
        assert restored.thought == step.thought
        assert restored.confidence == step.confidence
        assert restored.evidence == step.evidence
        assert restored.step_type == step.step_type


# ── Conclusion ────────────────────────────────────────────────────


class TestConclusion:
    """Test suite for Conclusion."""
    def test_create_basic(self) -> None:
        """Verify create basic behavior."""
        c = Conclusion(action="Deploy", justification="All tests pass")
        assert c.action == "Deploy"
        assert c.confidence == 0.5
        assert c.alternatives == []
        assert c.risks == []

    def test_confidence_clamped(self) -> None:
        """Verify confidence clamped behavior."""
        c = Conclusion(action="x", justification="y", confidence=2.0)
        assert c.confidence == 1.0

    def test_serialization_roundtrip(self) -> None:
        """Verify serialization roundtrip behavior."""
        c = Conclusion(
            action="Refactor",
            justification="Code smell detected",
            confidence=0.75,
            alternatives=["Rewrite", "Ignore"],
            risks=["May break API"],
        )
        d = c.to_dict()
        restored = Conclusion.from_dict(d)
        assert restored.action == c.action
        assert restored.justification == c.justification
        assert restored.alternatives == c.alternatives
        assert restored.risks == c.risks


# ── ReasoningTrace ────────────────────────────────────────────────


class TestReasoningTrace:
    """Test suite for ReasoningTrace."""
    def test_empty_trace(self) -> None:
        """Verify empty trace behavior."""
        trace = ReasoningTrace(prompt="Test")
        assert trace.step_count == 0
        assert not trace.is_complete
        assert trace.mean_confidence == 0.0

    def test_add_steps(self) -> None:
        """Verify add steps behavior."""
        trace = ReasoningTrace()
        trace.add_step(ReasoningStep(thought="A", confidence=0.6))
        trace.add_step(ReasoningStep(thought="B", confidence=0.8))
        assert trace.step_count == 2
        assert trace.mean_confidence == pytest.approx(0.7)

    def test_set_conclusion(self) -> None:
        """Verify set conclusion behavior."""
        trace = ReasoningTrace()
        trace.add_step(ReasoningStep(thought="A", confidence=0.8))
        c = Conclusion(action="Do it", justification="High confidence", confidence=0.9)
        trace.set_conclusion(c)
        assert trace.is_complete
        # total = mean*0.7 + conclusion*0.3 = 0.8*0.7 + 0.9*0.3 = 0.83
        assert trace.total_confidence == pytest.approx(0.83)

    def test_json_roundtrip(self) -> None:
        """Verify json roundtrip behavior."""
        trace = ReasoningTrace(prompt="How?", depth=ThinkingDepth.DEEP)
        trace.add_step(ReasoningStep(thought="Step 1", confidence=0.7))
        trace.set_conclusion(Conclusion(action="Act", justification="Reason"))
        j = trace.to_json()
        restored = ReasoningTrace.from_json(j)
        assert restored.prompt == "How?"
        assert restored.step_count == 1
        assert restored.is_complete
        assert restored.depth == ThinkingDepth.DEEP

    def test_to_dict_contains_expected_keys(self) -> None:
        """Verify to dict contains expected keys behavior."""
        trace = ReasoningTrace(prompt="P")
        d = trace.to_dict()
        assert "trace_id" in d
        assert "steps" in d
        assert "step_count" in d
        assert "is_complete" in d
        assert d["step_count"] == 0
        assert d["is_complete"] is False


# ── ThinkingDepth ─────────────────────────────────────────────────


class TestThinkingDepth:
    """Test suite for ThinkingDepth."""
    def test_depth_mapping(self) -> None:
        """Verify depth mapping behavior."""
        assert DEPTH_TO_STEPS[ThinkingDepth.SHALLOW] == 1
        assert DEPTH_TO_STEPS[ThinkingDepth.NORMAL] == 3
        assert DEPTH_TO_STEPS[ThinkingDepth.DEEP] == 5
        assert DEPTH_TO_STEPS[ThinkingDepth.EXHAUSTIVE] == 8


# ── StructuralStepGenerator ──────────────────────────────────────


class TestStructuralStepGenerator:
    """Test suite for StructuralStepGenerator."""
    def test_shallow_produces_one_step(self) -> None:
        """Verify shallow produces one step behavior."""
        gen = StructuralStepGenerator()
        steps = gen.generate_steps("test", ThinkingDepth.SHALLOW)
        assert len(steps) == 1
        assert steps[0].step_type == "observation"

    def test_normal_produces_three_steps(self) -> None:
        """Verify normal produces three steps behavior."""
        gen = StructuralStepGenerator()
        steps = gen.generate_steps("test", ThinkingDepth.NORMAL)
        assert len(steps) == 3
        types = [s.step_type for s in steps]
        assert "observation" in types
        assert "hypothesis" in types

    def test_deep_produces_five_steps(self) -> None:
        """Verify deep produces five steps behavior."""
        gen = StructuralStepGenerator()
        steps = gen.generate_steps("test", ThinkingDepth.DEEP)
        assert len(steps) == 5

    def test_context_enrichment(self) -> None:
        """Verify context enrichment behavior."""
        gen = StructuralStepGenerator()
        ctx = {"key": "value"}
        steps = gen.generate_steps("test", ThinkingDepth.SHALLOW, ctx)
        assert len(steps) == 1
        assert len(steps[0].evidence) > 0  # context added as evidence


# ── StructuralConclusionSynthesizer ──────────────────────────────


class TestStructuralConclusionSynthesizer:
    """Test suite for StructuralConclusionSynthesizer."""
    def test_empty_steps(self) -> None:
        """Verify empty steps behavior."""
        synth = StructuralConclusionSynthesizer()
        c = synth.synthesize([], "test")
        assert c.confidence == 0.0
        assert "insufficient" in c.action.lower()

    def test_synthesize_from_steps(self) -> None:
        """Verify synthesize from steps behavior."""
        synth = StructuralConclusionSynthesizer()
        steps = [
            ReasoningStep(thought="First", confidence=0.6),
            ReasoningStep(thought="Second", confidence=0.8),
        ]
        c = synth.synthesize(steps, "refactor module")
        assert c.confidence == pytest.approx(0.7)
        assert "refactor module" in c.action


# ── ChainOfThought pipeline ──────────────────────────────────────


class TestChainOfThought:
    """Test suite for ChainOfThought."""
    def test_basic_think(self) -> None:
        """Verify basic think behavior."""
        cot = ChainOfThought()
        trace = cot.think("How do I optimize this query?")
        assert trace.step_count == 3  # NORMAL depth
        assert trace.is_complete
        assert hasattr(trace.conclusion, 'action')
        assert hasattr(trace.conclusion, 'confidence')
        assert trace.duration_ms > 0

    def test_shallow_think(self) -> None:
        """Verify shallow think behavior."""
        cot = ChainOfThought(depth=ThinkingDepth.SHALLOW)
        trace = cot.think("Quick check")
        assert trace.step_count == 1

    def test_deep_think(self) -> None:
        """Verify deep think behavior."""
        cot = ChainOfThought()
        trace = cot.think("Complex problem", depth=ThinkingDepth.DEEP)
        assert trace.step_count == 5

    def test_trace_stored(self) -> None:
        """Verify trace stored behavior."""
        cot = ChainOfThought()
        cot.think("First")
        cot.think("Second")
        assert len(cot.traces) == 2

    def test_get_last_trace(self) -> None:
        """Verify get last trace behavior."""
        cot = ChainOfThought()
        cot.think("One")
        last = cot.get_last_trace()
        assert hasattr(last, 'prompt')
        assert last.prompt == "One"

    def test_clear_traces(self) -> None:
        """Verify clear traces behavior."""
        cot = ChainOfThought()
        cot.think("Test")
        cot.clear_traces()
        assert cot.get_last_trace() is None

    def test_context_passed_through(self) -> None:
        """Verify context passed through behavior."""
        cot = ChainOfThought()
        trace = cot.think("Test", context={"key": "value"})
        assert trace.step_count > 0
        # Context should appear as evidence in the first step
        assert any(
            "key" in e for step in trace.steps for e in step.evidence
        )

    def test_depth_property(self) -> None:
        """Verify depth property behavior."""
        cot = ChainOfThought()
        assert cot.depth == ThinkingDepth.NORMAL
        cot.depth = ThinkingDepth.DEEP
        assert cot.depth == ThinkingDepth.DEEP
