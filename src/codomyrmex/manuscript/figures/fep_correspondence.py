"""Manuscript figure: fep correspondence."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import (
    _OI,
    _add_provenance_note,
    _save,
    np,
    plt,
)


def fig_fep_correspondence() -> None:
    """Visual mapping of Free Energy Principle components to Colony Kernel
    subsystems. Used by 08_active_inference.md.

    A tiled table with color-coded rows showing the correspondence.
    """
    rows = [
        ("Generative model\np(o, s)", "PheromoneStore +\nConsequenceMemory",
         "Field stores accumulated\nconsequence history",
         _OI["blue"]),
        ("Observations o", "Pheromone field:\nTraceField.sense()",
         "Signal strengths at\n(tick, location, type)",
         _OI["sky"]),
        ("Hidden states s", "AgentTrustProfile:\ntrust_score, role",
         "Latent competence\ninferred from outcomes",
         _OI["orange"]),
        ("Variational posterior\nq(s)", "RoleAdapter.infer_role()",
         "Deterministic mapping\nfrom trust→role",
         _OI["pink"]),
        ("Expected Free Energy\nG(π)", "ActuationGate.evaluate()\ngate_score",
         "Cost of acting with\ncurrent belief state",
         _OI["vermil"]),
        ("Policy π", "ActionProposal\n(action_type, target)",
         "Proposed course of\naction for gate",
         _OI["green"]),
        ("Active inference\n(action selection)", "GateResult:\nEXECUTE/HOLD/REFUSE",
         "Score-thresholded\nternary decision",
         "#555555"),
        ("Learning\n(parameter update)", "ConsequenceMemory.record()\ntrust_delta",
         "Trust deltas as\nparameter updates",
         _OI["pink"]),
    ]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")
    ax.axis("off")

    col_widths = [0.22, 0.28, 0.32, 0.18]
    n_rows = len(rows)
    row_h = 0.65
    table_w = sum(col_widths)
    table_h = n_rows * row_h + 0.3

    # Headers
    headers = ["FEP component", "Colony Kernel\nsubsystem", "Formal\ncorrespondence", "Decay\nclass"]
    x_positions = [sum(col_widths[:i]) for i in range(len(col_widths))]
    start_x = (1 - table_w) / 2
    start_y = 0.92

    for i, (header, x_pos) in enumerate(zip(headers, x_positions, strict=False)):
        ax.text(
            start_x + x_pos + col_widths[i] / 2, start_y,
            header, ha="center", va="center", fontsize=8.5,
            fontweight="bold", color="#1a1a1a",
        )

    # Rows
    for r, (fep, kernel, formal, color) in enumerate(rows):
        y = start_y - 0.08 - (r + 1) * row_h
        # Row background
        bg_color = "#EBF0F5" if r % 2 == 0 else "#F7F9FC"
        ax.add_patch(plt.Rectangle(
            (start_x, y), table_w, row_h,
            facecolor=bg_color, edgecolor="none", alpha=0.6, zorder=0,
        ))
        # Color stripe
        ax.add_patch(plt.Rectangle(
            (start_x, y), 0.04, row_h,
            facecolor=color, edgecolor="none", alpha=0.9, zorder=1,
        ))
        # Cells
        texts = [fep, kernel, formal, ""]
        for j, (txt, x_pos, cw) in enumerate(zip(texts, x_positions, col_widths, strict=False)):
            ax.text(
                start_x + x_pos + cw / 2, y + row_h / 2,
                txt, ha="center", va="center",
                fontsize=7.0 if j < 3 else 6.5,
                color="#1a1a1a",
                linespacing=1.2,
            )

    ax.set_title(
        "Free Energy Principle — Colony Kernel correspondence\n"
        "Each FEP component maps to a deterministic colony subsystem",
        fontsize=11, pad=6, color="#1a1a1a",
    )
    _add_provenance_note(fig)
    fig.tight_layout(pad=0.4, rect=(0, 0.035, 1, 1))
    _save(fig, "fep_correspondence.png")
