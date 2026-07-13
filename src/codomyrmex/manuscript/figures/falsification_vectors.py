"""Manuscript figure: falsification vectors."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    _OI,
    _add_provenance_note,
    _pub_style,
    _save,
    mpatches,
    plt,
)


def fig_falsification_vectors() -> None:
    vectors = [
        ("SECURITY_RISK", "HIGH", _OI["vermil"]),
        ("NO_ROLLBACK", "HIGH", _OI["vermil"]),
        ("NO_TEST_VALUE", "HIGH", _OI["vermil"]),
        ("SCOPE_CREEP", "HIGH", _OI["vermil"]),
        ("CIRCULAR_ARCHITECTURE", "HIGH", _OI["vermil"]),
        ("FALSE_METRIC", "MEDIUM", _OI["orange"]),
        ("HIDDEN_MAINTENANCE_COST", "MEDIUM", _OI["orange"]),
        ("DEPENDENCY_RISK", "MEDIUM", _OI["orange"]),
        ("OVER_BROAD_MODULE", "MEDIUM", _OI["orange"]),
        ("PREMATURE_ABSTRACTION", "LOW", _OI["sky"]),
    ]
    sev_weight = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    names = [v[0] for v in vectors]
    weights = [sev_weight[v[1]] for v in vectors]
    colors = [v[2] for v in vectors]
    labels = [v[1] for v in vectors]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")
    _pub_style(ax)

    y_pos = list(range(len(names)))

    # Severity band backgrounds
    for x0, x1, bcolor, balpha in [
        (3.5, 4.55, _OI["black"], 0.06),
        (2.5, 3.5, _OI["vermil"], 0.05),
        (1.5, 2.5, _OI["orange"], 0.04),
        (0.5, 1.5, _OI["sky"], 0.04),
    ]:
        ax.axvspan(x0, x1, alpha=balpha, color=bcolor, zorder=0)

    # Lollipop stems
    for i, (w, color) in enumerate(zip(weights, colors, strict=False)):
        ax.plot(
            [0, w],
            [y_pos[i], y_pos[i]],
            color=color,
            lw=2.0,
            alpha=0.55,
            zorder=2,
            solid_capstyle="round",
        )

    # Lollipop heads
    ax.scatter(
        weights, y_pos, c=colors, s=220, zorder=4, edgecolors="white", linewidths=2.0
    )

    # Severity letter inside head
    for i, (w, sev, color) in enumerate(zip(weights, labels, colors, strict=False)):
        txt_color = "white" if color not in (_OI["sky"], _OI["yellow"]) else "#1a1a1a"
        ax.text(
            w,
            y_pos[i],
            sev[0],  # C / H / M / L
            va="center",
            ha="center",
            fontsize=7.5,
            color=txt_color,
            fontweight="bold",
            zorder=5,
        )

    ax.text(
        3.76,
        5.45,
        "CRITICAL override class\n(no canonical vector currently\nlands here)",
        fontsize=8.2,
        color="#333333",
        ha="center",
        va="center",
        bbox={
            "boxstyle": "round,pad=0.35",
            "facecolor": "#FFF0EE",
            "edgecolor": _OI["vermil"],
            "alpha": 0.95,
            "linewidth": 1.5,
        },
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9, fontfamily="monospace")
    ax.set_xlabel("Severity weight", fontsize=11.5, color="#333333")
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(
        ["LOW (1)", "MEDIUM (2)", "HIGH (3)", "CRITICAL (4)"], fontsize=9.5
    )
    ax.set_title(
        f"FalsificationWorker — {len(vectors)} canonical adversarial vectors\n"
        "Current checks top out at HIGH; CRITICAL remains the unconditional gate override class",
        fontsize=11,
        pad=12,
    )

    legend_items = [
        mpatches.Patch(color=_OI["black"], label="CRITICAL override class"),
        mpatches.Patch(color=_OI["vermil"], label="HIGH — FAILURE deposit"),
        mpatches.Patch(color=_OI["orange"], label="MEDIUM — RISK deposit"),
        mpatches.Patch(color=_OI["sky"], label="LOW — finding only"),
    ]
    ax.legend(
        handles=legend_items,
        fontsize=8.2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.11),
        framealpha=0.92,
        ncol=4,
        edgecolor="#CCCCCC",
    )

    ax.invert_yaxis()
    ax.set_xlim(0, 4.7)
    _add_provenance_note(fig)
    fig.tight_layout(rect=(0, 0.095, 1, 1))
    _save(fig, "falsification_vectors.png")
