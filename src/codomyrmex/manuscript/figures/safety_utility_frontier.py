"""Offline paired safety--utility frontier fixture."""

from __future__ import annotations

import matplotlib.pyplot as plt

from codomyrmex.colony_kernel.research.benchmark import run_paired_benchmark
from codomyrmex.manuscript.figures._common import (
    _OI,
    _add_provenance_note,
    _save,
    _var_float,
    _var_str,
)


def fig_safety_utility_frontier() -> None:
    seed = int(_var_float("CONFIG_EXPERIMENT_SEED"))
    run = run_paired_benchmark(seed=seed, repo_root=".")
    frontier = run.metrics["safety_utility_frontier"]
    fig, ax = plt.subplots(figsize=(8.6, 5.8))
    for row, color, marker in zip(
        frontier, (_OI["vermil"], _OI["blue"]), ("o", "s"), strict=True
    ):
        ax.scatter(
            row["harmful_action_rate"],
            row["utility"],
            s=110,
            color=color,
            marker=marker,
            label=(
                "baseline always execute"
                if row["condition"] == "baseline_always_execute"
                else "reference-gate mediated"
            ),
        )
        label = (
            "always execute"
            if row["condition"] == "baseline_always_execute"
            else "reference-gate mediated"
        )
        ax.annotate(
            f"{label}\nh={row['harmful_action_rate']:.3f}, u={row['utility']:.3f}",
            xy=(row["harmful_action_rate"], row["utility"]),
            xytext=(8, 10 if row["condition"] == "baseline_always_execute" else -30),
            textcoords="offset points",
            fontsize=8.2,
            ha="left",
            va="bottom" if row["condition"] == "baseline_always_execute" else "top",
            color="#172033",
        )
    baseline = next(
        row for row in frontier if row["condition"] == "baseline_always_execute"
    )
    mediated = next(row for row in frontier if row["condition"] == "gate_mediated")
    arrow_y = max(baseline["utility"], mediated["utility"]) + 0.06
    ax.annotate(
        "",
        xy=(mediated["harmful_action_rate"], arrow_y),
        xytext=(baseline["harmful_action_rate"], arrow_y),
        arrowprops={
            "arrowstyle": "-|>",
            "color": _OI["green"],
            "linewidth": 1.5,
        },
    )
    harm_delta = run.metrics["harm_delta_ci"]
    ax.text(
        0.5,
        arrow_y + 0.035,
        f"paired Δ harm = {harm_delta['estimate']:+.3f} · "
        f"descriptive interval [{harm_delta['ci_low']:+.3f}, {harm_delta['ci_high']:+.3f}]",
        transform=ax.transData,
        ha="center",
        va="bottom",
        fontsize=8.1,
        color="#172033",
    )
    ax.set_xlabel("Harmful-action rate (lower is better)")
    ax.set_ylabel("Mean utility per task case (fixture score; 0–1)")
    ax.set_title(
        f"Deterministic paired safety–utility fixture · N={run.metrics['paired_case_count']} cases · seed={seed}"
    )
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, loc="lower right", title="Condition")
    ax.text(
        0.01,
        -0.20,
        "Mediator: "
        + _var_str("RESULT_BENCHMARK_MEDIATOR_PROVENANCE")
        + "; production-gate parity: "
        + _var_str("RESULT_BENCHMARK_PRODUCTION_GATE_PARITY")
        + ".",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=7.4,
        color="#526176",
        wrap=True,
    )
    _add_provenance_note(fig)
    _save(fig, "safety_utility_frontier.png")


__all__ = ["fig_safety_utility_frontier"]
