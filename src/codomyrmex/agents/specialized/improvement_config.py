"""Configuration for the code improvement pipeline.

Safety limits and behavioral configuration for autonomous code
improvement, including change limits, confidence thresholds,
and scope constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ImprovementConfig:
    """Configuration for the ImprovementPipeline.

    Attributes:
        max_changes_per_run: Maximum number of changes to propose.
        max_retries: Maximum fix-generation retries per anti-pattern.
        min_confidence: Minimum confidence to apply a change.
        scope_constraints: File patterns to include (empty = all).
        exclude_patterns: File patterns to exclude.
        auto_apply: If True, apply fixes without human review.
        max_file_size_kb: Skip files larger than this.
        severity_threshold: Minimum anti-pattern severity to address.
    """

    max_changes_per_run: int = 10
    max_retries: int = 2
    min_confidence: float = 0.7
    scope_constraints: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=lambda: ["test_*", "*_test.py"])
    auto_apply: bool = False
    max_file_size_kb: int = 500
    severity_threshold: float = 0.3


__all__ = ["ImprovementConfig"]
