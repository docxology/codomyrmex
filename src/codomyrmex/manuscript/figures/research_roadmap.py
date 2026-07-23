"""Manuscript figure: evidence-bound research roadmap."""

from __future__ import annotations

import json
import textwrap

from codomyrmex.manuscript.figures._common import (
    _CONFIG,
    _OI,
    _add_provenance_note,
    _save,
    _var_str,
    plt,
)

_STATUS_COLORS = {
    "implemented": _OI["green"],
    "next": _OI["blue"],
    "planned": _OI["orange"],
    "research": _OI["pink"],
}


def _roadmap_stages() -> list[dict[str, str]]:
    raw = _var_str("CONFIG_RESEARCH_ROADMAP_STAGES")
    if not raw:
        configured = _CONFIG.get("research_roadmap")
        if isinstance(configured, list):
            raw = json.dumps(configured)
        else:
            raise RuntimeError(
                "Research roadmap figure requires configured research_roadmap entries"
            )
    try:
        stages = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Research roadmap variable is not valid JSON") from exc
    if not isinstance(stages, list) or not stages:
        raise RuntimeError("Research roadmap variable must contain a non-empty list")
    required = {
        "id",
        "name",
        "status",
        "artifact",
        "metric",
        "falsifier",
        "exit_criteria",
    }
    normalized: list[dict[str, str]] = []
    for stage in stages:
        if not isinstance(stage, dict) or not required <= set(stage):
            raise RuntimeError("Research roadmap stage is missing required fields")
        normalized.append({key: str(stage[key]) for key in required})
    return normalized


def fig_research_roadmap() -> None:
    """Draw the configured milestone sequence without implying completed evidence."""
    stages = _roadmap_stages()
    figure_width = max(12.0, 2.15 * len(stages))
    fig, ax = plt.subplots(figsize=(figure_width, 5.3))
    background = "#F7F9FC"
    fig.patch.set_facecolor(background)
    ax.set_facecolor(background)
    ax.axis("off")
    ax.set_xlim(-0.55, len(stages) - 0.45)
    ax.set_ylim(-0.2, 1.25)

    # The connecting line communicates dependency order; it is not a timeline.
    ax.annotate(
        "",
        xy=(len(stages) - 0.72, 0.55),
        xytext=(-0.28, 0.55),
        arrowprops={
            "arrowstyle": "-|>",
            "color": "#8CA0B8",
            "linewidth": 2.0,
            "mutation_scale": 16,
        },
    )

    for index, stage in enumerate(stages):
        status = stage["status"].lower()
        color = _STATUS_COLORS.get(status, _OI["grey"])
        ax.scatter(
            [index],
            [0.55],
            s=360,
            color=color,
            edgecolors="white",
            linewidths=2.2,
            zorder=4,
        )
        ax.text(
            index,
            0.55,
            stage["id"],
            ha="center",
            va="center",
            color="white",
            fontsize=9,
            fontweight="bold",
            zorder=5,
        )
        ax.text(
            index,
            0.80,
            textwrap.fill(stage["name"], width=22),
            ha="center",
            va="bottom",
            fontsize=8.2,
            fontweight="bold",
            color="#172033",
            wrap=True,
        )
        ax.text(
            index,
            0.12,
            status.capitalize(),
            ha="center",
            va="top",
            fontsize=8.2,
            color=color,
            fontweight="bold",
        )

    ax.text(
        -0.48,
        1.17,
        "Evidence-bound research sequence (dependency order, not a delivery timeline)",
        ha="left",
        va="top",
        fontsize=12,
        fontweight="bold",
        color="#172033",
    )
    ax.text(
        -0.48,
        1.05,
        "Every milestone requires a retained artifact, decisive metric, falsifier, and exit criterion.",
        ha="left",
        va="top",
        fontsize=8.8,
        color="#526176",
    )
    ax.text(
        len(stages) - 0.48,
        -0.11,
        "Planning artifact — future statuses are not results",
        ha="right",
        va="top",
        fontsize=8.0,
        color="#526176",
        style="italic",
    )
    _add_provenance_note(fig)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _save(fig, "research_roadmap.png")
