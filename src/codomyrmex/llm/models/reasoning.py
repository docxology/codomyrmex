"""Reasoning data models for Chain-of-Thought pipelines.

Provides structured types for multi-step reasoning traces, individual
reasoning steps, and conclusions.  All types are JSON-serializable
``dataclass``es designed to integrate with the ``AgentProtocol``
plan-act-observe lifecycle.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class ThinkingDepth(StrEnum):
    """Controls how many reasoning steps the CoT pipeline produces."""

    SHALLOW = "shallow"     # 1 step — quick pattern match
    NORMAL = "normal"       # 3 steps — standard analysis
    DEEP = "deep"           # 5+ steps — exhaustive deliberation
    EXHAUSTIVE = "exhaustive"  # 8+ steps — maximum rigour


DEPTH_TO_STEPS: dict[ThinkingDepth, int] = {
    ThinkingDepth.SHALLOW: 1,
    ThinkingDepth.NORMAL: 3,
    ThinkingDepth.DEEP: 5,
    ThinkingDepth.EXHAUSTIVE: 8,
}


@dataclass
class ReasoningStep:
    """A single step in a chain-of-thought reasoning trace.

    Attributes:
        thought: The reasoning content for this step.
        confidence: Confidence in this step's validity (0.0 – 1.0).
        evidence: Supporting evidence or references.
        step_type: Category of reasoning (e.g. "observation", "hypothesis",
            "deduction", "verification").
        timestamp: When this step was produced.
        step_id: Unique identifier for this step.
    """

    thought: str
    confidence: float = 0.5
    evidence: list[str] = field(default_factory=list)
    step_type: str = "reasoning"
    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    step_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    def __post_init__(self) -> None:
        """Clamp confidence to [0, 1]."""
        self.confidence = max(0.0, min(1.0, self.confidence))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReasoningStep:
        """Deserialize from a plain dictionary."""
        return cls(
            thought=data["thought"],
            confidence=data.get("confidence", 0.5),
            evidence=data.get("evidence", []),
            step_type=data.get("step_type", "reasoning"),
            timestamp=data.get("timestamp", datetime.now(UTC).isoformat()),
            step_id=data.get("step_id", uuid.uuid4().hex[:12]),
        )


@dataclass
class Conclusion:
    """The synthesized outcome of a reasoning trace.

    Attributes:
        action: The recommended action to take.
        justification: Why this action was chosen.
        confidence: Overall confidence in the conclusion (0.0 – 1.0).
        alternatives: Other actions considered but not chosen.
        risks: Identified risks or caveats.
    """

    action: str
    justification: str
    confidence: float = 0.5
    alternatives: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Clamp confidence to [0, 1]."""
        self.confidence = max(0.0, min(1.0, self.confidence))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Conclusion:
        """Deserialize from a plain dictionary."""
        return cls(
            action=data["action"],
            justification=data.get("justification", ""),
            confidence=data.get("confidence", 0.5),
            alternatives=data.get("alternatives", []),
            risks=data.get("risks", []),
        )


@dataclass
class ReasoningTrace:
    """Complete record of a chain-of-thought reasoning session.

    Attributes:
        steps: Ordered list of reasoning steps.
        conclusion: The synthesized conclusion (may be None if incomplete).
        total_confidence: Aggregate confidence across steps.
        duration_ms: Wall-clock time for the reasoning process.
        token_count: Approximate token usage (if tracked).
        prompt: The original prompt that initiated reasoning.
        depth: The thinking depth used.
        trace_id: Unique identifier for this trace.
        created_at: Trace creation timestamp.
    """

    steps: list[ReasoningStep] = field(default_factory=list)
    conclusion: Conclusion | None = None
    total_confidence: float = 0.0
    duration_ms: float = 0.0
    token_count: int = 0
    prompt: str = ""
    depth: ThinkingDepth = ThinkingDepth.NORMAL
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )

    # ── Computed properties ───────────────────────────────────────

    @property
    def step_count(self) -> int:
        """Number of reasoning steps in this trace."""
        return len(self.steps)

    @property
    def is_complete(self) -> bool:
        """Whether the trace has reached a conclusion."""
        return self.conclusion is not None

    @property
    def mean_confidence(self) -> float:
        """Average confidence across all steps."""
        if not self.steps:
            return 0.0
        return sum(s.confidence for s in self.steps) / len(self.steps)

    # ── Mutation ──────────────────────────────────────────────────

    def add_step(self, step: ReasoningStep) -> None:
        """Append a reasoning step and update aggregate confidence."""
        self.steps.append(step)
        self.total_confidence = self.mean_confidence

    def set_conclusion(self, conclusion: Conclusion) -> None:
        """Set the trace conclusion."""
        self.conclusion = conclusion
        self.total_confidence = (
            self.mean_confidence * 0.7 + conclusion.confidence * 0.3
        )

    # ── Serialization ─────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary."""
        d: dict[str, Any] = {
            "trace_id": self.trace_id,
            "prompt": self.prompt,
            "depth": self.depth.value,
            "steps": [s.to_dict() for s in self.steps],
            "total_confidence": round(self.total_confidence, 4),
            "duration_ms": round(self.duration_ms, 2),
            "token_count": self.token_count,
            "step_count": self.step_count,
            "is_complete": self.is_complete,
            "created_at": self.created_at,
        }
        if self.conclusion:
            d["conclusion"] = self.conclusion.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReasoningTrace:
        """Deserialize from a plain dictionary."""
        steps = [ReasoningStep.from_dict(s) for s in data.get("steps", [])]
        conclusion = None
        if "conclusion" in data and data["conclusion"] is not None:
            conclusion = Conclusion.from_dict(data["conclusion"])
        return cls(
            steps=steps,
            conclusion=conclusion,
            total_confidence=data.get("total_confidence", 0.0),
            duration_ms=data.get("duration_ms", 0.0),
            token_count=data.get("token_count", 0),
            prompt=data.get("prompt", ""),
            depth=ThinkingDepth(data.get("depth", "normal")),
            trace_id=data.get("trace_id", uuid.uuid4().hex),
            created_at=data.get("created_at", datetime.now(UTC).isoformat()),
        )

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, s: str) -> ReasoningTrace:
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(s))


__all__ = [
    "Conclusion",
    "DEPTH_TO_STEPS",
    "ReasoningStep",
    "ReasoningTrace",
    "ThinkingDepth",
]
