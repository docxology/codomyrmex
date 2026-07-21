"""Manuscript figure: live falsification-vector taxonomy."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    _OI,
    _add_provenance_note,
    _falsification_severity_map,
    _pub_style,
    _save,
    _var_float,
    mpatches,
    plt,
)


def fig_falsification_vectors() -> None:
    """Plot the highest severity emitted by each live heuristic check."""
    from codomyrmex.colony_kernel.falsification.models import AttackVector

    severity_by_vector = _falsification_severity_map()
    severity_names = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
    severity_colors = {
        "CRITICAL": _OI["black"],
        "HIGH": _OI["vermil"],
        "MEDIUM": _OI["orange"],
        "LOW": _OI["sky"],
    }
    severity_weights = {
        name: int(_var_float(f"CONFIG_SEVERITY_RANK_{name}", fallback))
        for name, fallback in zip(severity_names, (4, 3, 2, 1), strict=False)
    }
    vectors = [
        (
            vector.name,
            severity_by_vector[vector.name],
            severity_colors[severity_by_vector[vector.name]],
        )
        for vector in AttackVector
    ]
    vectors.sort(key=lambda item: (-severity_weights[item[1]], item[0]))
    names = [vector[0] for vector in vectors]
    weights = [severity_weights[vector[1]] for vector in vectors]
    colors = [vector[2] for vector in vectors]
    labels = [vector[1] for vector in vectors]
    max_weight = max(severity_weights.values())

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")
    _pub_style(ax)

    y_pos = list(range(len(names)))

    for severity_name in severity_names:
        rank = severity_weights[severity_name]
        color = severity_colors[severity_name]
        alpha = 0.06 if severity_name == "CRITICAL" else 0.05
        ax.axvspan(rank - 0.5, rank + 0.5, alpha=alpha, color=color, zorder=0)

    for index, (weight, color) in enumerate(zip(weights, colors, strict=False)):
        ax.plot(
            [0, weight],
            [y_pos[index], y_pos[index]],
            color=color,
            lw=2.0,
            alpha=0.55,
            zorder=2,
            solid_capstyle="round",
        )

    ax.scatter(
        weights,
        y_pos,
        c=colors,
        s=220,
        zorder=4,
        edgecolors="white",
        linewidths=2.0,
    )

    for index, (weight, severity, color) in enumerate(
        zip(weights, labels, colors, strict=False)
    ):
        text_color = "white" if color not in (_OI["sky"], _OI["yellow"]) else "#1a1a1a"
        ax.text(
            weight,
            y_pos[index],
            severity[0],
            va="center",
            ha="center",
            fontsize=7.5,
            color=text_color,
            fontweight="bold",
            zorder=5,
        )

    critical_text = (
        "CRITICAL override class\n(no canonical vector currently\nlands here)"
        if "CRITICAL" not in labels
        else "CRITICAL override class\n(hard refusal before scoring)"
    )
    ax.text(
        max_weight - 0.24,
        max(len(names) - 1, 0) * 0.55,
        critical_text,
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
    ax.set_xticks(sorted(severity_weights.values()))
    ax.set_xticklabels(
        [f"{name} ({severity_weights[name]})" for name in reversed(severity_names)],
        fontsize=9.5,
    )
    ax.set_title(
        f"FalsificationWorker — {len(vectors)} canonical adversarial vectors\n"
        "Highest live check severity; CRITICAL remains the unconditional gate override class",
        fontsize=11,
        pad=12,
    )

    legend_items = [
        mpatches.Patch(color=severity_colors[name], label=f"{name} — live severity")
        for name in severity_names
    ]
    ax.legend(
        handles=legend_items,
        fontsize=8.2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.11),
        framealpha=0.92,
        ncol=len(severity_names),
        edgecolor="#CCCCCC",
    )

    ax.invert_yaxis()
    ax.set_xlim(0, max_weight + 0.7)
    _add_provenance_note(fig)
    fig.tight_layout(rect=(0, 0.095, 1, 1))
    _save(fig, "falsification_vectors.png")
