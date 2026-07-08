"""Manuscript figure: formula comparison."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    _OI,
    _add_provenance_note,
    _pub_style,
    _save,
    np,
    plt,
)


def fig_formula_comparison() -> None:
    """Comparison of four gate formula approaches across 6 criteria.

    Used by 90_appendix_design_rationale.md §dr-gate-formula.
    Creates a grouped bar chart for visual comparison.
    """
    approaches = ["Weighted\nadditive", "Multiplicative", "Learned\nclassifier", "Rule\nsystem"]
    criteria = ["Auditability", "Zero-shot\nvalidity", "Recovery\nsupport",
                "Calibration\ncost", "Interpretability", "Safety\nguarantees"]
    # Scores: 5 = best, 1 = worst
    scores = np.array([
        [5, 5, 4, 5, 5, 4],   # Weighted additive
        [3, 3, 2, 5, 3, 3],   # Multiplicative
        [1, 1, 3, 1, 1, 2],   # Learned classifier
        [4, 4, 1, 5, 4, 3],   # Rule system
    ])

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")
    _pub_style(ax)

    n_criteria = len(criteria)
    n_approaches = len(approaches)
    bar_width = 0.18
    x = np.arange(n_criteria)
    colors = [_OI["green"], _OI["blue"], _OI["grey"], _OI["yellow"]]

    for i, (approach, color) in enumerate(zip(approaches, colors, strict=False)):
        offset = (i - n_approaches / 2 + 0.5) * bar_width
        bars = ax.bar(
            x + offset, scores[i], bar_width,
            label=approach.replace("\n", " "),
            color=color, alpha=0.85, edgecolor="white", linewidth=1.2,
            zorder=3,
        )
        # Annotate bars
        for bar, score in zip(bars, scores[i], strict=False):
            ax.text(bar.get_x() + bar.get_width() / 2, score + 0.08,
                    str(score), ha="center", va="bottom", fontsize=8,
                    fontweight="bold", color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(criteria, fontsize=8)
    ax.set_ylabel("Score (1–5)", fontsize=9)
    ax.set_ylim(0, 6.2)
    ax.legend(fontsize=8, loc="upper right", framealpha=0.88, ncol=2)
    ax.set_title(
        "Gate formula approach comparison across 6 criteria\n"
        "Weighted additive achieves the best combination of auditability, safety, and flexibility",
        fontsize=11, pad=10, color="#1a1a1a",
    )

    # Highlight additive column
    for i in range(n_criteria):
        max_score = scores[:, i].max()
        if scores[0, i] == max_score:
            ax.text(x[i], 5.85, "← best", ha="center", va="bottom",
                    fontsize=7.5, color=_OI["vermil"], fontweight="bold",
                    style="italic")

    _add_provenance_note(fig)
    fig.tight_layout(pad=0.4, rect=(0, 0.035, 1, 1))
    _save(fig, "formula_comparison.png")
