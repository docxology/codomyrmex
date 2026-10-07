"""Charts for governance data recorded by the policy engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart

if TYPE_CHECKING:
    from matplotlib.figure import Figure

    from .policy import PolicyEngine


def plot_policy_compliance(
    engine: PolicyEngine,
    policy_name: str | None = None,
    output_path: str | None = None,
) -> Figure:
    """Render a pie chart of the engine's recorded pass/fail evaluations.

    The counts come from :meth:`PolicyEngine.compliance_stats`, i.e. from the
    policy evaluations the engine has actually performed. Categories with no
    evaluations are omitted from the chart.

    Args:
        engine: Policy engine whose evaluation history is plotted.
        policy_name: Plot a single policy; ``None`` plots all policies.
        output_path: Optional file path to save the chart to.

    Returns:
        The matplotlib figure.

    Raises:
        ValueError: If no evaluations have been recorded.
        PolicyError: If ``policy_name`` does not exist.
    """
    stats = engine.compliance_stats(policy_name)
    if stats["evaluations"] == 0:
        scope = f"policy '{policy_name}'" if policy_name else "any policy"
        raise ValueError(
            f"No evaluations recorded for {scope}; evaluate policies before "
            "plotting compliance."
        )

    slices = [
        (label, count)
        for label, count in (("Pass", stats["passed"]), ("Fail", stats["failed"]))
        if count > 0
    ]
    title = "Policy Compliance Rate"
    if policy_name:
        title = f"{title}: {policy_name}"
    return create_pie_chart(
        labels=[label for label, _ in slices],
        sizes=[count for _, count in slices],
        title=f"{title} (n={stats['evaluations']})",
        output_path=output_path,
    )
