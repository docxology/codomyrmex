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
    "adapter_ready": _OI["blue"],
    "harness_ready": _OI["blue"],
    "planned": _OI["orange"],
    "prototype_ready": _OI["pink"],
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
    fig, ax = plt.subplots(figsize=(8.5, 10.2))
    background = "#F7F9FC"
    fig.patch.set_facecolor(background)
    ax.set_facecolor(background)
    ax.axis("off")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, len(stages) + 1.2)

    for index, stage in enumerate(stages):
        status = stage["status"].lower()
        color = _STATUS_COLORS.get(status, _OI["grey"])
        y = len(stages) - index - 0.05
        if index < len(stages) - 1:
            ax.annotate(
                "",
                xy=(0.075, y - 0.78),
                xytext=(0.075, y - 0.28),
                arrowprops={
                    "arrowstyle": "-|>",
                    "color": "#8CA0B8",
                    "linewidth": 1.8,
                    "mutation_scale": 14,
                },
                zorder=1,
            )
        ax.scatter(
            [0.075],
            [y],
            s=520,
            color=color,
            edgecolors="white",
            linewidths=2.0,
            zorder=4,
        )
        ax.text(
            0.075,
            y,
            stage["id"],
            ha="center",
            va="center",
            color="white",
            fontsize=9.5,
            fontweight="bold",
            zorder=5,
        )
        ax.text(
            0.14,
            y + 0.19,
            stage["name"],
            ha="left",
            va="center",
            fontsize=10.2,
            fontweight="bold",
            color="#172033",
        )
        ax.text(
            0.14,
            y - 0.08,
            status.upper(),
            ha="left",
            va="center",
            fontsize=7.2,
            color="white",
            fontweight="bold",
            bbox={
                "boxstyle": "round,pad=0.25",
                "facecolor": color,
                "edgecolor": color,
            },
        )
        artifact = "Required evidence: " + stage["artifact"]
        ax.text(
            0.36,
            y - 0.08,
            textwrap.fill(artifact, width=56),
            ha="left",
            va="center",
            fontsize=7.5,
            color="#374151",
            linespacing=1.08,
            bbox={
                "boxstyle": "round,pad=0.28",
                "facecolor": "white",
                "edgecolor": "#D8E0EA",
                "linewidth": 0.9,
            },
        )

    ax.text(
        0.0,
        len(stages) + 1.02,
        "Evidence-bound research sequence (dependency order, not a delivery timeline)",
        ha="left",
        va="top",
        fontsize=12.2,
        fontweight="bold",
        color="#172033",
    )
    ax.text(
        0.0,
        len(stages) + 0.72,
        "Printed status and required-evidence text are authoritative; colour is redundant.",
        ha="left",
        va="top",
        fontsize=9.0,
        color="#526176",
    )
    ax.text(
        1.0,
        0.12,
        "Each stage also has a metric, falsifier, and exit criterion in the searchable roadmap table.",
        ha="right",
        va="bottom",
        fontsize=8.1,
        color="#526176",
        style="italic",
    )
    _add_provenance_note(fig)
    fig.tight_layout(rect=(0.02, 0.05, 0.98, 0.99))
    _save(fig, "research_roadmap.png")
