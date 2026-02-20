"""Tests for cerebrum/distillation.py."""

from __future__ import annotations

import pytest

from codomyrmex.cerebrum.distillation import (
    DistillationConfig,
    DistillationPipeline,
)
from codomyrmex.llm.models.reasoning import (
    Conclusion,
    ReasoningStep,
    ReasoningTrace,
    ThinkingDepth,
)


def _make_complete_trace(
    prompt: str = "test prompt",
    confidence: float = 0.7,
    steps: int = 3,
) -> ReasoningTrace:
    """Create a complete reasoning trace for testing."""
    trace = ReasoningTrace(prompt=prompt, depth=ThinkingDepth.NORMAL)
    for i in range(steps):
        trace.add_step(ReasoningStep(
            thought=f"Step {i+1} reasoning",
            confidence=confidence,
            step_type="analysis",
        ))
    trace.set_conclusion(Conclusion(
        action=f"Proceed with: {prompt}",
        justification="All steps converge",
        confidence=confidence,
    ))
    return trace


class TestDistillationConfig:
    def test_defaults(self) -> None:
        cfg = DistillationConfig()
        assert cfg.min_confidence == 0.5
        assert cfg.min_steps == 2
        assert cfg.dedup_by_prompt is True


class TestDistillationPipeline:
    def test_distill_single_trace(self) -> None:
        pipeline = DistillationPipeline()
        traces = [_make_complete_trace()]
        cases = pipeline.distill(traces)
        assert len(cases) == 1
        assert cases[0].case_id.startswith("distilled-")

    def test_distill_features(self) -> None:
        pipeline = DistillationPipeline()
        traces = [_make_complete_trace(prompt="analyze module")]
        cases = pipeline.distill(traces)
        case = cases[0]
        assert case.features["prompt"] == "analyze module"
        assert case.features["step_count"] == 3
        assert "step_types" in case.features

    def test_distill_outcome(self) -> None:
        pipeline = DistillationPipeline()
        traces = [_make_complete_trace()]
        cases = pipeline.distill(traces)
        assert "action" in cases[0].outcome
        assert "justification" in cases[0].outcome

    def test_distill_context(self) -> None:
        pipeline = DistillationPipeline()
        traces = [_make_complete_trace()]
        cases = pipeline.distill(traces)
        assert "thoughts" in cases[0].context
        assert len(cases[0].context["thoughts"]) == 3

    def test_distill_skips_incomplete(self) -> None:
        pipeline = DistillationPipeline()
        trace = ReasoningTrace(prompt="incomplete")
        trace.add_step(ReasoningStep(thought="A", confidence=0.5))
        # No conclusion set
        cases = pipeline.distill([trace])
        assert len(cases) == 0

    def test_distill_skips_low_confidence(self) -> None:
        pipeline = DistillationPipeline(
            config=DistillationConfig(min_confidence=0.8)
        )
        traces = [_make_complete_trace(confidence=0.3)]
        cases = pipeline.distill(traces)
        assert len(cases) == 0

    def test_distill_skips_few_steps(self) -> None:
        pipeline = DistillationPipeline(
            config=DistillationConfig(min_steps=5)
        )
        traces = [_make_complete_trace(steps=3)]
        cases = pipeline.distill(traces)
        assert len(cases) == 0

    def test_deduplication(self) -> None:
        pipeline = DistillationPipeline()
        t1 = _make_complete_trace(prompt="same prompt")
        t2 = _make_complete_trace(prompt="same prompt")
        cases = pipeline.distill([t1, t2])
        assert len(cases) == 1  # Second deduplicated

    def test_dedup_disabled(self) -> None:
        pipeline = DistillationPipeline(
            config=DistillationConfig(dedup_by_prompt=False)
        )
        t1 = _make_complete_trace(prompt="same")
        t2 = _make_complete_trace(prompt="same")
        cases = pipeline.distill([t1, t2])
        assert len(cases) == 2

    def test_metadata_source(self) -> None:
        pipeline = DistillationPipeline()
        traces = [_make_complete_trace()]
        cases = pipeline.distill(traces)
        assert cases[0].metadata["source"] == "distillation"
        assert "trace_id" in cases[0].metadata
