"""Manuscript figure: bounded Active Inference comparison."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    _OI,
    _add_provenance_note,
    _save,
    plt,
)


def fig_fep_correspondence() -> None:
    """Render conceptual analogies and the implementation divergence for each."""

    rows = [
        (
            "Observation",
            "Sensed RISK / FAILURE traces",
            "Aggregated stored values; no likelihood model",
            _OI["sky"],
        ),
        (
            "Latent state / belief",
            "Trust score and role label",
            "Deterministic accounting state; no posterior q(s)",
            _OI["orange"],
        ),
        (
            "Preferences / costs",
            "Budget, weights, thresholds",
            "Fixed engineering policy; no learned prior preferences",
            _OI["pink"],
        ),
        (
            "Policy evaluation",
            "ActuationGate score",
            "Weighted rule; no expected-free-energy calculation",
            _OI["vermil"],
        ),
        (
            "Action selection",
            "EXECUTE / HOLD / REFUSE",
            "Threshold routing; no variational policy inference",
            _OI["green"],
        ),
        (
            "Learning",
            "Trust deltas and signal deposits",
            "Additive updates; no Bayesian parameter learning",
            _OI["blue"],
        ),
    ]

    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")
    ax.axis("off")

    headers = [
        "Active Inference concept",
        "Loose software analogue",
        "Why equivalence fails",
    ]
    widths = [0.23, 0.31, 0.46]
    x0 = 0.02
    y_top = 0.88
    row_h = 0.115

    for index, (header, width) in enumerate(zip(headers, widths, strict=True)):
        left = x0 + sum(widths[:index])
        ax.add_patch(
            plt.Rectangle(
                (left, y_top),
                width,
                0.075,
                facecolor="#172033",
                edgecolor="white",
                linewidth=1,
            )
        )
        ax.text(
            left + width / 2,
            y_top + 0.0375,
            header,
            ha="center",
            va="center",
            color="white",
            fontsize=9,
            fontweight="bold",
        )

    for row_index, (concept, analogue, divergence, color) in enumerate(rows):
        y = y_top - (row_index + 1) * row_h
        background = "#EAF0F6" if row_index % 2 == 0 else "#F7F9FC"
        ax.add_patch(
            plt.Rectangle(
                (x0, y),
                sum(widths),
                row_h,
                facecolor=background,
                edgecolor="white",
                linewidth=1,
            )
        )
        ax.add_patch(
            plt.Rectangle(
                (x0, y),
                0.012,
                row_h,
                facecolor=color,
                edgecolor="none",
            )
        )
        values = [concept, analogue, divergence]
        for column, (value, width) in enumerate(zip(values, widths, strict=True)):
            left = x0 + sum(widths[:column])
            ax.text(
                left + width / 2,
                y + row_h / 2,
                value,
                ha="center",
                va="center",
                fontsize=8.2,
                color="#1A1A1A",
                wrap=True,
            )

    ax.set_title(
        "Active Inference comparison: structural analogy, not implementation identity",
        fontsize=12,
        color="#1A1A1A",
        pad=12,
        fontweight="bold",
    )
    ax.text(
        0.5,
        0.055,
        "Codomyrmex implements no generative model, posterior update, or expected-free-energy optimizer.",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=8.5,
        color=_OI["vermil"],
        fontweight="bold",
    )
    _add_provenance_note(fig)
    fig.tight_layout(pad=0.5, rect=(0, 0.04, 1, 1))
    _save(fig, "fep_correspondence.png")
