"""Roadmap and formalism status matrix."""

from __future__ import annotations

import matplotlib.pyplot as plt

from codomyrmex.manuscript.figures._common import (
    _CONFIG,
    _OI,
    _add_provenance_note,
    _save,
)


def fig_research_status_matrix() -> None:
    roadmap = _CONFIG.get("research_roadmap", [])
    crosswalk = _CONFIG.get("formalism_code_crosswalk", [])
    rows: list[tuple[str, str, str]] = []
    for entry in roadmap if isinstance(roadmap, list) else []:
        if isinstance(entry, dict):
            rows.append(
                ("roadmap", str(entry.get("id", "?")), str(entry.get("status", "?")))
            )
    for entry in crosswalk if isinstance(crosswalk, list) else []:
        if isinstance(entry, dict):
            rows.append(
                ("formalism", str(entry.get("id", "?")), str(entry.get("status", "?")))
            )
    status_names = sorted({status for _, _, status in rows})
    status_index = {status: index for index, status in enumerate(status_names)}
    fig, ax = plt.subplots(figsize=(10.5, max(4.5, len(rows) * 0.28)))
    colors = [
        _OI["green"],
        _OI["blue"],
        _OI["orange"],
        _OI["pink"],
        _OI["grey"],
    ]
    for index, (family, identifier, status) in enumerate(rows):
        ax.scatter(
            status_index[status],
            index,
            s=100,
            color=colors[status_index[status] % len(colors)],
        )
        ax.text(
            -0.18, index, f"{family}:{identifier}", ha="right", va="center", fontsize=7
        )
    ax.set_xticks(range(len(status_names)), status_names)
    ax.set_yticks([])
    ax.set_xlim(-0.5, max(0.5, len(status_names) - 0.5))
    ax.set_title("Evidence status across roadmap and formalism surfaces")
    ax.grid(axis="x", alpha=0.2)
    _add_provenance_note(fig)
    _save(fig, "research_status_matrix.png")


__all__ = ["fig_research_status_matrix"]
