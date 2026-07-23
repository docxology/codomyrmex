"""Manuscript figure: formal objects translated into executable evidence."""

from __future__ import annotations

import json
import textwrap

from matplotlib.patches import FancyBboxPatch

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
    "partial": _OI["blue"],
    "next": _OI["orange"],
    "planned": _OI["orange"],
    "research": _OI["pink"],
}


def _crosswalk_entries() -> list[dict[str, object]]:
    raw = _var_str("CONFIG_FORMALISM_CODE_CROSSWALK")
    if not raw:
        configured = _CONFIG.get("formalism_code_crosswalk")
        if isinstance(configured, list):
            raw = json.dumps(configured)
        else:
            raise RuntimeError(
                "Formalism crosswalk figure requires configured crosswalk entries"
            )
    try:
        entries = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Formalism crosswalk variable is not valid JSON") from exc
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("Formalism crosswalk variable must be a non-empty list")
    required = {
        "id",
        "name",
        "status",
        "formalism",
        "formal_object",
        "code_symbols",
        "bridge",
        "evidence",
        "claim_boundary",
    }
    normalized: list[dict[str, object]] = []
    for entry in entries:
        if not isinstance(entry, dict) or not required <= set(entry):
            raise RuntimeError("Formalism crosswalk entry is missing required fields")
        normalized.append(entry)
    return normalized


def _cell_text(value: object, width: int) -> str:
    return "\n".join(textwrap.wrap(str(value), width=width, break_long_words=False))


def fig_formalism_code_crosswalk() -> None:
    """Draw the configured translation chain without implying proof equivalence."""
    entries = _crosswalk_entries()
    columns = [
        "Formal object",
        "Typed code anchor",
        "Translation",
        "Evidence",
        "Claim limit",
    ]
    widths = [0.19, 0.19, 0.21, 0.18, 0.23]
    left = 0.08
    top = 0.84
    row_height = min(0.095, 0.74 / max(len(entries), 1))
    figure_height = max(7.5, 1.0 + len(entries) * 0.86)
    fig, ax = plt.subplots(figsize=(14.0, figure_height))
    background = "#F7F9FC"
    fig.patch.set_facecolor(background)
    ax.set_facecolor(background)
    ax.axis("off")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)

    ax.text(
        left,
        0.965,
        "Formal objects → code anchors → translation → evidence → claim boundary",
        ha="left",
        va="top",
        fontsize=13,
        fontweight="bold",
        color="#172033",
    )
    ax.text(
        left,
        0.925,
        "A correspondence inventory with explicit missing links; not a proof graph or equivalence claim",
        ha="left",
        va="top",
        fontsize=9,
        color="#526176",
    )

    x_positions: list[float] = []
    cursor = left
    for width in widths:
        x_positions.append(cursor)
        cursor += width
    for column, (header, width) in enumerate(zip(columns, widths, strict=True)):
        ax.add_patch(
            FancyBboxPatch(
                (x_positions[column], top),
                width - 0.006,
                0.055,
                boxstyle="round,pad=0.004,rounding_size=0.008",
                facecolor="#172033",
                edgecolor="white",
                linewidth=0.8,
            )
        )
        ax.text(
            x_positions[column] + (width - 0.006) / 2,
            top + 0.027,
            header,
            ha="center",
            va="center",
            fontsize=8.6,
            fontweight="bold",
            color="white",
        )

    for row_index, entry in enumerate(entries):
        y = top - (row_index + 1) * row_height
        background_row = "#EAF0F6" if row_index % 2 == 0 else background
        status = str(entry["status"]).lower()
        color = _STATUS_COLORS.get(status, _OI["grey"])
        row_values = [
            f"{entry['id']}  {entry['name']}\n{entry['formalism']}\n{entry['formal_object']}",
            str(entry["code_symbols"]),
            str(entry["bridge"]),
            str(entry["evidence"]),
            str(entry["claim_boundary"]),
        ]
        for column, (value, width) in enumerate(zip(row_values, widths, strict=True)):
            ax.add_patch(
                FancyBboxPatch(
                    (x_positions[column], y),
                    width - 0.006,
                    row_height - 0.008,
                    boxstyle="round,pad=0.004,rounding_size=0.006",
                    facecolor=background_row,
                    edgecolor="white",
                    linewidth=0.8,
                )
            )
            ax.text(
                x_positions[column] + (width - 0.006) / 2,
                y + (row_height - 0.008) / 2,
                _cell_text(value, 29 if column in {0, 1} else 34),
                ha="center",
                va="center",
                fontsize=7.1 if column else 7.25,
                color="#172033",
                linespacing=1.12,
            )
        ax.add_patch(
            FancyBboxPatch(
                (left - 0.018, y + 0.012),
                0.012,
                row_height - 0.032,
                boxstyle="round,pad=0.002,rounding_size=0.004",
                facecolor=color,
                edgecolor="none",
            )
        )

    bottom = top - (len(entries) + 1) * row_height - 0.01
    ax.text(
        left,
        max(0.035, bottom),
        "Status colours: implemented · partial · planned/next · research",
        ha="left",
        va="bottom",
        fontsize=8.5,
        color="#526176",
        style="italic",
    )
    _add_provenance_note(fig)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    _save(fig, "formalism_code_crosswalk.png")
