"""Chain-of-Thought reasoning pipeline.

Provides a composable pipeline for multi-step deliberative reasoning:

1. ``think(prompt)`` — decompose a problem into reasoning steps
2. ``reason(steps)`` — synthesize steps into a conclusion
3. ``conclude(conclusion)`` — convert conclusion to an actionable output

The pipeline works without an LLM for structural reasoning (pattern
decomposition, evidence accumulation) and can optionally be backed by
an LLM provider for richer analysis.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Protocol

from codomyrmex.logging_monitoring import get_logger

from .models.reasoning import (
    Conclusion,
    DEPTH_TO_STEPS,
    ReasoningStep,
    ReasoningTrace,
    ThinkingDepth,
)

logger = get_logger(__name__)


# ── Step generators ───────────────────────────────────────────────

class StepGenerator(Protocol):
    """Protocol for pluggable step generation strategies."""

    def generate_steps(
        self,
        prompt: str,
        depth: ThinkingDepth,
        context: dict[str, Any] | None = None,
    ) -> list[ReasoningStep]:
        """Generate reasoning steps from a prompt."""
        ...


class StructuralStepGenerator:
    """Default step generator using structural decomposition.

    Produces reasoning steps by decomposing the prompt into:
    1. Observation — what is being asked
    2. Hypothesis — possible approaches
    3. Deduction — logical implications
    4. Verification — checking consistency
    5+ Evidence gathering — supporting data (for deeper thinking)
    """

    STEP_TEMPLATES: list[tuple[str, str]] = [
        ("observation", "Observing the problem: {}"),
        ("hypothesis", "Forming hypothesis about the approach"),
        ("analysis", "Analyzing implications and constraints"),
        ("deduction", "Deducing the most viable solution path"),
        ("verification", "Verifying consistency of the reasoning"),
        ("evidence", "Gathering supporting evidence"),
        ("refinement", "Refining the approach based on evidence"),
        ("synthesis", "Synthesizing final assessment"),
    ]

    def generate_steps(
        self,
        prompt: str,
        depth: ThinkingDepth,
        context: dict[str, Any] | None = None,
    ) -> list[ReasoningStep]:
        """Generate reasoning steps via structural decomposition."""
        n_steps = DEPTH_TO_STEPS.get(depth, 3)
        steps: list[ReasoningStep] = []

        for i in range(min(n_steps, len(self.STEP_TEMPLATES))):
            step_type, template = self.STEP_TEMPLATES[i]
            thought = template.format(prompt[:200]) if i == 0 else template

            # Confidence ramps up as we accumulate steps
            base_confidence = 0.4 + (i * 0.1)

            # Context enrichment
            evidence: list[str] = []
            if context:
                for key, val in context.items():
                    if isinstance(val, str) and len(val) < 500:
                        evidence.append(f"{key}: {val}")

            steps.append(
                ReasoningStep(
                    thought=thought,
                    confidence=min(base_confidence, 0.95),
                    evidence=evidence if i == 0 else [],
                    step_type=step_type,
                )
            )

        return steps


# ── Conclusion synthesizer ────────────────────────────────────────

class ConclusionSynthesizer(Protocol):
    """Protocol for pluggable conclusion synthesis."""

    def synthesize(
        self, steps: list[ReasoningStep], prompt: str
    ) -> Conclusion:
        """Synthesize a conclusion from reasoning steps."""
        ...


class StructuralConclusionSynthesizer:
    """Default synthesizer that aggregates step insights."""

    def synthesize(
        self, steps: list[ReasoningStep], prompt: str
    ) -> Conclusion:
        """Synthesize conclusion by aggregating step confidence and evidence."""
        if not steps:
            return Conclusion(
                action="No action — insufficient reasoning",
                justification="No reasoning steps were produced",
                confidence=0.0,
            )

        # Aggregate evidence from all steps
        all_evidence: list[str] = []
        for step in steps:
            all_evidence.extend(step.evidence)

        # Compute aggregate confidence
        mean_conf = sum(s.confidence for s in steps) / len(steps)

        # Build justification from step thoughts
        justification_parts = [
            f"Step {i + 1} ({s.step_type}): {s.thought}"
            for i, s in enumerate(steps)
        ]
        justification = " → ".join(justification_parts[:5])

        return Conclusion(
            action=f"Proceed with analysis of: {prompt[:100]}",
            justification=justification,
            confidence=mean_conf,
            alternatives=[],
            risks=["Reasoning based on structural decomposition only"],
        )


# ── Main pipeline ─────────────────────────────────────────────────

class ChainOfThought:
    """Composable Chain-of-Thought reasoning pipeline.

    Usage::

        cot = ChainOfThought()
        trace = cot.think("How should I refactor this module?")
        print(trace.conclusion.action)
        print(trace.to_json())
    """

    def __init__(
        self,
        step_generator: StepGenerator | None = None,
        synthesizer: ConclusionSynthesizer | None = None,
        depth: ThinkingDepth = ThinkingDepth.NORMAL,
    ) -> None:
        """Execute   Init   operations natively."""
        self._generator = step_generator or StructuralStepGenerator()
        self._synthesizer = synthesizer or StructuralConclusionSynthesizer()
        self._depth = depth
        self._traces: list[ReasoningTrace] = []

    @property
    def depth(self) -> ThinkingDepth:
        """Current thinking depth."""
        return self._depth

    @depth.setter
    def depth(self, value: ThinkingDepth) -> None:
        """Set thinking depth."""
        self._depth = value

    @property
    def traces(self) -> list[ReasoningTrace]:
        """All reasoning traces produced by this pipeline."""
        return list(self._traces)

    def think(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        depth: ThinkingDepth | None = None,
    ) -> ReasoningTrace:
        """Run the full think → reason → conclude pipeline.

        Args:
            prompt: The question or problem to reason about.
            context: Optional context (prior observations, data, etc.).
            depth: Override thinking depth for this call.

        Returns:
            A complete ``ReasoningTrace`` with steps and conclusion.
        """
        effective_depth = depth or self._depth
        t0 = time.monotonic()

        trace = ReasoningTrace(
            prompt=prompt,
            depth=effective_depth,
        )

        logger.info(
            "Starting CoT reasoning",
            extra={"prompt_len": len(prompt), "depth": effective_depth.value},
        )

        # Step 1: Generate reasoning steps
        steps = self._generator.generate_steps(
            prompt, effective_depth, context
        )
        for step in steps:
            trace.add_step(step)

        # Step 2: Synthesize conclusion
        conclusion = self._synthesizer.synthesize(steps, prompt)
        trace.set_conclusion(conclusion)

        # Record timing
        trace.duration_ms = (time.monotonic() - t0) * 1000

        logger.info(
            "CoT reasoning complete",
            extra={
                "steps": trace.step_count,
                "confidence": round(trace.total_confidence, 3),
                "duration_ms": round(trace.duration_ms, 1),
            },
        )

        self._traces.append(trace)
        return trace

    def get_last_trace(self) -> ReasoningTrace | None:
        """Return the most recent reasoning trace, or None."""
        return self._traces[-1] if self._traces else None

    def clear_traces(self) -> None:
        """Clear all stored traces."""
        self._traces.clear()


__all__ = [
    "ChainOfThought",
    "ConclusionSynthesizer",
    "StepGenerator",
    "StructuralConclusionSynthesizer",
    "StructuralStepGenerator",
]
