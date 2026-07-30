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


def _cell_text(value: object, width: int, *, limit: int) -> str:
    """Wrap a source-backed, deliberately abbreviated cell for print legibility."""

    compact = textwrap.shorten(
        " ".join(str(value).split()),
        width=limit,
        placeholder="…",
    )
    return "\n".join(
        textwrap.wrap(
            compact,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def fig_formalism_code_crosswalk() -> None:
    """Draw an abbreviated, redundantly encoded translation inventory."""
    entries = _crosswalk_entries()
    columns = [
        "Formalism and status",
        "Code anchor and translation",
        "Evidence and claim limit",
    ]
    widths = [0.28, 0.31, 0.35]
    left = 0.035
    header_y = 0.825
    rows_top = 0.785
    rows_bottom = 0.105
    fig, ax = plt.subplots(figsize=(8.0, 9.0))
    background = "#F7F9FC"
    fig.patch.set_facecolor(background)
    ax.set_facecolor(background)
    ax.axis("off")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)

    ax.text(
        left,
        0.965,
        "Formalism → code translation → evidence and claim boundary",
        ha="left",
        va="top",
        fontsize=13.2,
        fontweight="bold",
        color="#172033",
    )
    ax.text(
        left,
        0.925,
        "Abbreviated navigation view; full searchable text follows in the manuscript tables",
        ha="left",
        va="top",
        fontsize=9.2,
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
                (x_positions[column], header_y),
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
            header_y + 0.027,
            header,
            ha="center",
            va="center",
            fontsize=9.0,
            fontweight="bold",
            color="white",
        )

    row_texts: list[list[str]] = []
    row_weights: list[int] = []
    for entry in entries:
        status = str(entry["status"]).replace("_", " ").upper()
        code_symbols = "; ".join(
            part.strip()
            for part in str(entry["code_symbols"]).split(";")[:2]
            if part.strip()
        )
        if str(entry["code_symbols"]).count(";") >= 2:
            code_symbols += "; …"
        name_label = f"{entry['id']} · {entry['name']}"
        anchor_label = f"Anchor: {code_symbols}"
        bridge_label = f"Bridge: {entry['bridge']}"
        evidence_label = f"Evidence: {entry['evidence']}"
        limit_label = f"Limit: {entry['claim_boundary']}"
        values = [
            (
                f"{_cell_text(name_label, 27, limit=52)}\n"
                f"STATUS: {status}\n"
                f"{_cell_text(entry['formalism'], 27, limit=48)}"
            ),
            (
                f"{_cell_text(anchor_label, 30, limit=62)}\n"
                f"{_cell_text(bridge_label, 30, limit=64)}"
            ),
            (
                f"{_cell_text(evidence_label, 34, limit=68)}\n"
                f"{_cell_text(limit_label, 34, limit=76)}"
            ),
        ]
        row_texts.append(values)
        row_weights.append(max(value.count("\n") + 1 for value in values) + 1)

    available_height = rows_top - rows_bottom
    weight_unit = available_height / sum(row_weights)
    cursor_y = rows_top
    for row_index, (entry, row_values, weight) in enumerate(
        zip(entries, row_texts, row_weights, strict=True)
    ):
        row_height = weight * weight_unit
        y = cursor_y - row_height
        cursor_y = y
        background_row = "#EAF0F6" if row_index % 2 == 0 else background
        status = str(entry["status"]).lower()
        color = _STATUS_COLORS.get(status, _OI["grey"])
        for column, (value, width) in enumerate(zip(row_values, widths, strict=True)):
            ax.add_patch(
                FancyBboxPatch(
                    (x_positions[column], y + 0.004),
                    width - 0.006,
                    row_height - 0.006,
                    boxstyle="round,pad=0.004,rounding_size=0.006",
                    facecolor=background_row,
                    edgecolor="white",
                    linewidth=0.8,
                )
            )
            ax.text(
                x_positions[column] + 0.012,
                y + row_height / 2,
                value,
                ha="left",
                va="center",
                fontsize=8.7,
                color="#172033",
                linespacing=1.08,
            )
        ax.add_patch(
            FancyBboxPatch(
                (left - 0.018, y + 0.014),
                0.011,
                max(0.018, row_height - 0.028),
                boxstyle="round,pad=0.002,rounding_size=0.004",
                facecolor=color,
                edgecolor="none",
            )
        )

    ax.text(
        left,
        0.075,
        "Every row prints its status; colour is a redundant navigation cue.",
        ha="left",
        va="bottom",
        fontsize=8.8,
        color="#526176",
        style="italic",
    )
    _add_provenance_note(fig)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    _save(fig, "formalism_code_crosswalk.png")
