"""Configuration for the feedback loop.

Dataclass-based configuration for the planning-execution-feedback
cycle, controlling iteration limits, convergence thresholds,
retry behavior, and memory TTL.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FeedbackConfig:
    """Configuration for the FeedbackLoop.

    Attributes:
        max_iterations: Maximum re-plan cycles before bailing.
        convergence_threshold: Minimum score improvement between
            iterations to consider the loop converging (absolute).
        quality_floor: Minimum PlanScore to accept without re-planning.
            Scores below this trigger another iteration.
        retry_on_partial_failure: If True, re-plan when some (but not
            all) workflow steps fail.
        memory_ttl: TTL in seconds for feedback memory entries.
            Set to 0 for no expiration.
        memory_tag_prefix: Prefix for memory tags to namespace
            feedback entries.
        weight_success_rate: Weight for success rate in plan scoring.
        weight_time_efficiency: Weight for time efficiency.
        weight_retry_ratio: Weight for retry ratio (lower is better).
        weight_memory_hits: Weight for memory relevance.
    """

    max_iterations: int = 3
    convergence_threshold: float = 0.05
    quality_floor: float = 0.6
    retry_on_partial_failure: bool = True
    memory_ttl: float = 86400.0  # 24 hours
    memory_tag_prefix: str = "feedback"
    weight_success_rate: float = 0.4
    weight_time_efficiency: float = 0.3
    weight_retry_ratio: float = 0.2
    weight_memory_hits: float = 0.1


__all__ = ["FeedbackConfig"]
