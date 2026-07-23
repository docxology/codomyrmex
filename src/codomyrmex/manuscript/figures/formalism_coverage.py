"""Formalism-to-code bridge status inventory."""

from __future__ import annotations

import matplotlib.pyplot as plt

from codomyrmex.manuscript.figures._common import (
    _CONFIG,
    _OI,
    _add_provenance_note,
    _save,
)


def fig_formalism_coverage() -> None:
    entries = _CONFIG.get("formalism_code_crosswalk", [])
    counts: dict[str, int] = {}
    for entry in entries if isinstance(entries, list) else []:
        if isinstance(entry, dict):
            status = str(entry.get("status", "unclassified"))
            counts[status] = counts.get(status, 0) + 1
    statuses = sorted(counts)
    values = [counts[status] for status in statuses]
    palette = [_OI["green"], _OI["blue"], _OI["orange"], _OI["pink"], _OI["grey"]]
    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    bars = ax.bar(statuses, values, color=palette[: len(statuses)])
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value,
            str(value),
            ha="center",
            va="bottom",
        )
    ax.set_ylabel("Mappings")
    ax.set_title("Formalism-to-code bridge status")
    ax.grid(axis="y", alpha=0.2)
    _add_provenance_note(fig)
    _save(fig, "formalism_coverage.png")


__all__ = ["fig_formalism_coverage"]
