"""Attack-vector check: check missing metrics."""

from __future__ import annotations

import re
from typing import Any

from codomyrmex.colony_kernel.falsification.models import AttackVector
from codomyrmex.colony_kernel.models import FalsificationFinding, FalsificationSeverity


def check_missing_metrics(plan: dict[str, Any]) -> FalsificationFinding | None:
    """Attack: plan defines no verifiable success metric.

    Returns a MEDIUM finding when ``metrics`` is absent or contains only
    qualitative language with no measurable thresholds.
    """
    metrics = plan.get("metrics")

    if metrics is None:
        return FalsificationFinding(
            claim="The plan specifies at least one verifiable success metric.",
            attack_vector=AttackVector.FALSE_METRIC.value,
            severity=FalsificationSeverity.MEDIUM,
            evidence={"metrics": "<key absent>"},
            remediation=(
                "Add a `metrics` key with at least one measurable criterion, e.g. "
                "'coverage >= 80%', 'p99 latency < 200ms', or 'zero regressions in suite X'."
            ),
        )

    metrics_str = (
        str(metrics).strip()
        if not isinstance(metrics, (list, tuple))
        else " ".join(str(m) for m in metrics)
    )

    if not metrics_str:
        return FalsificationFinding(
            claim="The plan specifies at least one verifiable success metric.",
            attack_vector=AttackVector.FALSE_METRIC.value,
            severity=FalsificationSeverity.MEDIUM,
            evidence={"metrics": "<empty>"},
            remediation=(
                "Provide concrete, measurable metrics so outcomes can be objectively verified."
            ),
        )

    # Detect purely qualitative metrics with no numbers or comparisons
    has_number = bool(re.search(r"\d", metrics_str))
    has_comparison = bool(
        re.search(
            r"[<>=≤≥%]|better|faster|less|more|reduce|increase",
            metrics_str,
            re.IGNORECASE,
        )
    )
    if not has_number and not has_comparison:
        return FalsificationFinding(
            claim="Metrics contain measurable thresholds, not subjective language.",
            attack_vector=AttackVector.FALSE_METRIC.value,
            severity=FalsificationSeverity.LOW,
            evidence={"metrics": metrics_str[:200]},
            remediation=(
                "Add numeric thresholds or comparison operators to the metrics description. "
                "'Improved performance' is not a metric; '< 100ms p95' is."
            ),
        )

    return None
