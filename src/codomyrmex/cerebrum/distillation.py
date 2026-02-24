"""Knowledge distillation from reasoning traces to cases.

Extracts reusable patterns from ``ReasoningTrace`` objects and
converts them into ``Case`` entries for the ``CaseBase``.  This
enables the agent to learn from past reasoning and apply similar
solutions to new problems.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.cerebrum.core.cases import Case, CaseBase
from codomyrmex.llm.models.reasoning import (
    Conclusion,
    ReasoningStep,
    ReasoningTrace,
    ThinkingDepth,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class DistillationConfig:
    """Configuration for the distillation pipeline.

    Attributes:
        min_confidence: Minimum trace confidence to distill.
        min_steps: Minimum reasoning steps for a trace to be distillable.
        dedup_by_prompt: Whether to skip traces with duplicate prompts.
    """

    min_confidence: float = 0.5
    min_steps: int = 2
    dedup_by_prompt: bool = True


class DistillationPipeline:
    """Extracts reusable cases from reasoning traces.

    Usage::

        pipeline = DistillationPipeline()
        cases = pipeline.distill(agent.all_traces)
        for case in cases:
            case_base.add_case(case)
    """

    def __init__(
        self,
        config: DistillationConfig | None = None,
    ) -> None:
        """Execute   Init   operations natively."""
        self._config = config or DistillationConfig()
        self._seen_prompts: set[str] = set()

    def distill(
        self,
        traces: list[ReasoningTrace],
    ) -> list[Case]:
        """Distill a list of reasoning traces into cases.

        Each trace that meets quality thresholds (confidence, step
        count) is converted to a ``Case`` with:
        - features: prompt, depth, step_types
        - context: step thoughts, evidence
        - outcome: conclusion action + justification

        Args:
            traces: List of traces to distill.

        Returns:
            List of distilled ``Case`` objects.
        """
        cases: list[Case] = []

        for trace in traces:
            if not self._should_distill(trace):
                continue

            case = self._trace_to_case(trace)
            cases.append(case)

            if self._config.dedup_by_prompt:
                self._seen_prompts.add(self._prompt_hash(trace.prompt))

        logger.info(
            "Distilled traces to cases",
            extra={
                "traces_in": len(traces),
                "cases_out": len(cases),
            },
        )

        return cases

    def _should_distill(self, trace: ReasoningTrace) -> bool:
        """Check whether a trace meets distillation quality thresholds."""
        if not trace.is_complete:
            return False

        if trace.total_confidence < self._config.min_confidence:
            return False

        if trace.step_count < self._config.min_steps:
            return False

        if self._config.dedup_by_prompt:
            prompt_hash = self._prompt_hash(trace.prompt)
            if prompt_hash in self._seen_prompts:
                return False

        return True

    def _trace_to_case(self, trace: ReasoningTrace) -> Case:
        """Convert a single reasoning trace to a Case."""
        # Features: problem description
        step_types = [s.step_type for s in trace.steps]
        features: dict[str, Any] = {
            "prompt": trace.prompt,
            "depth": trace.depth.value,
            "step_count": trace.step_count,
            "step_types": step_types,
            "confidence": trace.total_confidence,
        }

        # Context: supporting evidence from steps
        context: dict[str, Any] = {
            "thoughts": [s.thought for s in trace.steps],
            "evidence": [e for s in trace.steps for e in s.evidence],
            "duration_ms": trace.duration_ms,
        }

        # Outcome: conclusion
        outcome: dict[str, Any] = {}
        if trace.conclusion:
            outcome = {
                "action": trace.conclusion.action,
                "justification": trace.conclusion.justification,
                "confidence": trace.conclusion.confidence,
                "alternatives": trace.conclusion.alternatives,
                "risks": trace.conclusion.risks,
            }

        case_id = f"distilled-{trace.trace_id[:12]}"

        return Case(
            case_id=case_id,
            features=features,
            context=context,
            outcome=outcome,
            metadata={
                "source": "distillation",
                "trace_id": trace.trace_id,
                "created_at": trace.created_at,
            },
        )

    @staticmethod
    def _prompt_hash(prompt: str) -> str:
        """Generate a hash for deduplication."""
        return hashlib.sha256(prompt.strip().lower().encode()).hexdigest()[:16]


__all__ = [
    "DistillationConfig",
    "DistillationPipeline",
]
