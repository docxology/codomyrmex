"""Evidence-bounded statistics for paired binary benchmark outcomes.

The analysis layer is deliberately independent of the runner and provider adapters. It
records denominators and partitions explicitly, keeps the historical normal-approximation
fields for compatibility, and adds an exact conditional interval for paired binary
differences together with an exact McNemar test.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

ANALYSIS_SCHEMA_VERSION = "paired-binary-v1"


def _beta_continued_fraction(a: float, b: float, x: float) -> float:
    """Evaluate the continued fraction used by the regularized beta function."""

    maximum_iterations = 200
    epsilon = 3.0e-14
    tiny = 1.0e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    d = max(abs(d), tiny) if d == 0.0 else d
    d = 1.0 / d
    result = d
    for iteration in range(1, maximum_iterations + 1):
        step = 2.0 * iteration
        numerator = iteration * (b - iteration) * x
        denominator = (qam + step) * (a + step)
        delta = numerator / denominator
        d = 1.0 + delta * d
        d = tiny if d == 0.0 else d
        c = 1.0 + delta / c
        c = tiny if c == 0.0 else c
        d = 1.0 / d
        result *= d * c
        numerator = -(a + iteration) * (qab + iteration) * x
        denominator = (a + step) * (qap + step)
        delta = numerator / denominator
        d = 1.0 + delta * d
        d = tiny if d == 0.0 else d
        c = 1.0 + delta / c
        c = tiny if c == 0.0 else c
        d = 1.0 / d
        correction = d * c
        result *= correction
        if abs(correction - 1.0) < epsilon:
            break
    return result


def _regularized_beta(x: float, a: float, b: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    log_factor = (
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log1p(-x)
    )
    factor = math.exp(log_factor)
    if x < (a + 1.0) / (a + b + 2.0):
        return factor * _beta_continued_fraction(a, b, x) / a
    return 1.0 - factor * _beta_continued_fraction(b, a, 1.0 - x) / b


def _beta_quantile(probability: float, a: float, b: float) -> float:
    """Compute a beta quantile by monotone bisection without SciPy."""

    if probability <= 0.0:
        return 0.0
    if probability >= 1.0:
        return 1.0
    lower, upper = 0.0, 1.0
    for _ in range(80):
        midpoint = (lower + upper) / 2.0
        if _regularized_beta(midpoint, a, b) < probability:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2.0


def _clopper_pearson(successes: int, trials: int, alpha: float = 0.05) -> tuple[float, float]:
    if trials < 1 or not 0 <= successes <= trials:
        raise ValueError("successes must be between zero and trials")
    lower = 0.0 if successes == 0 else _beta_quantile(alpha / 2.0, successes, trials - successes + 1)
    upper = (
        1.0
        if successes == trials
        else _beta_quantile(1.0 - alpha / 2.0, successes + 1, trials - successes)
    )
    return lower, upper


def _exact_two_sided_binomial_pvalue(successes: int, trials: int) -> float:
    if trials == 0:
        return 1.0
    tail = sum(math.comb(trials, index) for index in range(min(successes, trials - successes) + 1))
    return min(1.0, 2.0 * tail / (2**trials))


def _normal_interval(values: list[float]) -> tuple[float, float, float | None]:
    if not values:
        return (float("nan"), float("nan"), None)
    mean = sum(values) / len(values)
    if len(values) == 1:
        return mean, mean, mean
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    standard_error = math.sqrt(variance / len(values))
    margin = 1.959963984540054 * standard_error
    return mean, max(-1.0, mean - margin), min(1.0, mean + margin)


def paired_binary_effects(
    rows: list[dict[str, Any]],
    *,
    baseline: str = "always_execute",
    treatment: str = "enforced_authorization",
) -> dict[str, Any]:
    """Summarize a paired binary treatment effect with exact conditional inference."""

    grouped: dict[str, dict[str, int]] = defaultdict(dict)
    for row in rows:
        task_id = str(row["task_id"])
        condition = str(row["condition"])
        if condition in grouped[task_id]:
            raise ValueError(f"duplicate paired observation for {task_id}/{condition}")
        grouped[task_id][condition] = int(bool(row.get("task_success", False)))
    pairs = [
        (values[baseline], values[treatment])
        for values in grouped.values()
        if baseline in values and treatment in values
    ]
    if not pairs:
        return {
            "statistics_version": ANALYSIS_SCHEMA_VERSION,
            "baseline": baseline,
            "treatment": treatment,
            "n": 0,
            "mean_difference": None,
            "standard_error": None,
            "ci95": [None, None],
            "ci95_method": "normal_approximation",
            "ci95_exact": [None, None],
            "ci95_exact_method": "conditional_mcnemar",
            "mcnemar": {
                "baseline_success_treatment_failure": 0,
                "baseline_failure_treatment_success": 0,
                "discordant_pairs": 0,
                "exact_two_sided_pvalue": 1.0,
                "method": "exact_binomial_conditional",
            },
        }

    differences = [treatment_value - baseline_value for baseline_value, treatment_value in pairs]
    mean, normal_lower, normal_upper = _normal_interval([float(value) for value in differences])
    standard_error = (
        0.0
        if len(differences) == 1
        else math.sqrt(
            sum((value - mean) ** 2 for value in differences)
            / (len(differences) - 1)
            / len(differences)
        )
    )
    baseline_success_treatment_failure = sum(
        baseline_value == 1 and treatment_value == 0 for baseline_value, treatment_value in pairs
    )
    baseline_failure_treatment_success = sum(
        baseline_value == 0 and treatment_value == 1 for baseline_value, treatment_value in pairs
    )
    discordant = baseline_success_treatment_failure + baseline_failure_treatment_success
    if discordant:
        exact_lower, exact_upper = _clopper_pearson(
            baseline_failure_treatment_success, discordant
        )
        scale = discordant / len(pairs)
        exact_ci = [scale * (2.0 * exact_lower - 1.0), scale * (2.0 * exact_upper - 1.0)]
    else:
        exact_ci = [0.0, 0.0]
    return {
        "statistics_version": ANALYSIS_SCHEMA_VERSION,
        "baseline": baseline,
        "treatment": treatment,
        "n": len(pairs),
        "mean_difference": mean,
        "standard_error": standard_error,
        "ci95": [normal_lower, normal_upper],
        "ci95_method": "normal_approximation",
        "ci95_exact": exact_ci,
        "ci95_exact_method": "conditional_mcnemar",
        "mcnemar": {
            "baseline_success_treatment_failure": baseline_success_treatment_failure,
            "baseline_failure_treatment_success": baseline_failure_treatment_success,
            "discordant_pairs": discordant,
            "exact_two_sided_pvalue": _exact_two_sided_binomial_pvalue(
                baseline_failure_treatment_success, discordant
            ),
            "method": "exact_binomial_conditional",
        },
    }


def condition_summaries(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Return explicit denominators and rates for each condition and partition."""

    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[str(row.get("partition", "controlled"))][str(row["condition"])].append(row)

    by_partition: dict[str, dict[str, dict[str, Any]]] = {}
    for partition, conditions in sorted(grouped.items()):
        by_partition[partition] = {}
        for condition, condition_rows in sorted(conditions.items()):
            denominator = len(condition_rows)
            by_partition[partition][condition] = {
                "denominator": denominator,
                "task_success_count": sum(bool(row.get("task_success")) for row in condition_rows),
                "task_success_rate": sum(bool(row.get("task_success")) for row in condition_rows) / denominator,
                "verified_failure_count": sum(bool(row.get("verified_failure")) for row in condition_rows),
                "harmful_attempt_count": sum(bool(row.get("harmful_attempt")) for row in condition_rows),
            }
    return {
        "statistics_version": ANALYSIS_SCHEMA_VERSION,
        "row_denominator": len(rows),
        "partition_denominators": {
            partition: sum(group["denominator"] for group in conditions.values())
            for partition, conditions in by_partition.items()
        },
        "by_partition": by_partition,
    }


def analyze_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the machine-readable, partition-aware analysis payload."""

    return {
        "statistics_version": ANALYSIS_SCHEMA_VERSION,
        "denominators": condition_summaries(rows),
        "paired_effects": paired_binary_effects(rows),
    }


__all__ = [
    "ANALYSIS_SCHEMA_VERSION",
    "analyze_rows",
    "condition_summaries",
    "paired_binary_effects",
]
