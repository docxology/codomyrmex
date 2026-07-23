"""Offline paired safety--utility frontier fixture."""

from __future__ import annotations

import matplotlib.pyplot as plt

from codomyrmex.colony_kernel.research.benchmark import run_paired_benchmark
from codomyrmex.manuscript.figures._common import (
    _OI,
    _add_provenance_note,
    _save,
    _var_float,
)


def fig_safety_utility_frontier() -> None:
    seed = int(_var_float("CONFIG_EXPERIMENT_SEED"))
    run = run_paired_benchmark(seed=seed, repo_root=".")
    frontier = run.metrics["safety_utility_frontier"]
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    for row, color, marker in zip(
        frontier, (_OI["vermil"], _OI["blue"]), ("o", "s"), strict=True
    ):
        ax.scatter(
            row["harmful_action_rate"],
            row["utility"],
            s=110,
            color=color,
            marker=marker,
            label=row["condition"].replace("_", " "),
        )
    ax.set_xlabel("Harmful-action rate (lower is better)")
    ax.set_ylabel("Task utility (fixture score)")
    ax.set_title(
        f"Paired offline frontier · n={run.metrics['task_count']} · seed={seed}"
    )
    ax.set_xlim(left=0)
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    _add_provenance_note(fig)
    _save(fig, "safety_utility_frontier.png")


__all__ = ["fig_safety_utility_frontier"]
