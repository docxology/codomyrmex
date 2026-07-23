"""Manuscript figure: fixed-input paired-locality replay evidence."""

from __future__ import annotations

from matplotlib.patches import FancyBboxPatch

from codomyrmex.manuscript.figures._common import (
    _OI,
    _add_provenance_note,
    _save,
    _var_float,
    _var_str,
    plt,
)


def _decision_color(decision: str) -> str:
    return {
        "EXECUTE": _OI["green"],
        "HOLD": _OI["orange"],
        "REFUSE": _OI["vermil"],
    }.get(decision.upper(), _OI["grey"])


def fig_replay_contract() -> None:
    """Draw the executed replay as a semantic transition, not a causal chart."""
    stages = [
        (
            "Before failure",
            _var_float("RESULT_PAIRED_CLEAR_SCORE"),
            "EXECUTE",
            "hazard " + _var_str("RESULT_PAIRED_CLEAR_PRESSURE"),
        ),
        (
            "Same target after report",
            _var_float("RESULT_PAIRED_FAILURE_SCORE"),
            _var_str("RESULT_REPLAY_SAME_TARGET_DECISION"),
            "failure pressure " + _var_str("RESULT_PAIRED_FAILURE_PRESSURE"),
        ),
        (
            "Unrelated target",
            _var_float("RESULT_PAIRED_UNRELATED_SCORE"),
            _var_str("RESULT_REPLAY_UNRELATED_DECISION"),
            "hazard " + _var_str("RESULT_PAIRED_UNRELATED_PRESSURE"),
        ),
        (
            "Same target after recovery",
            _var_float("RESULT_PAIRED_RECOVERED_SCORE"),
            _var_str("RESULT_REPLAY_RECOVERY_DECISION"),
            "passive decay restored",
        ),
    ]
    fig, ax = plt.subplots(figsize=(14.0, 5.0))
    background = "#F7F9FC"
    fig.patch.set_facecolor(background)
    ax.set_facecolor(background)
    ax.axis("off")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)

    ax.text(
        0.04,
        0.94,
        "Executed paired-locality replay",
        ha="left",
        va="top",
        fontsize=14,
        fontweight="bold",
        color="#172033",
    )
    ax.text(
        0.04,
        0.875,
        "Fixed proposal identities · two semantic runs · caller-reported failure · no random draws",
        ha="left",
        va="top",
        fontsize=9,
        color="#526176",
    )

    left = 0.04
    gap = 0.018
    card_width = (0.92 - gap * (len(stages) - 1)) / len(stages)
    y = 0.39
    height = 0.34
    for index, (label, score, decision, note) in enumerate(stages):
        x = left + index * (card_width + gap)
        color = _decision_color(decision)
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                card_width,
                height,
                boxstyle="round,pad=0.012,rounding_size=0.018",
                facecolor="white",
                edgecolor=color,
                linewidth=2.0,
            )
        )
        ax.text(
            x + card_width / 2,
            y + height - 0.075,
            label,
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold",
            color="#172033",
            wrap=True,
        )
        ax.text(
            x + card_width / 2,
            y + 0.19,
            f"{score:.3f}",
            ha="center",
            va="center",
            fontsize=22,
            fontweight="bold",
            color="#172033",
        )
        ax.text(
            x + card_width / 2,
            y + 0.105,
            decision.upper(),
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color=color,
        )
        ax.text(
            x + card_width / 2,
            y + 0.035,
            note,
            ha="center",
            va="center",
            fontsize=7.5,
            color="#526176",
        )
        if index < len(stages) - 1:
            ax.annotate(
                "",
                xy=(x + card_width + gap * 0.82, y + height / 2),
                xytext=(x + card_width + gap * 0.18, y + height / 2),
                arrowprops={
                    "arrowstyle": "-|>",
                    "color": "#8CA0B8",
                    "linewidth": 1.4,
                },
            )

    repeatable = _var_str("RESULT_REPLAY_REPEATABLE").lower() == "true"
    badge_color = _OI["green"] if repeatable else _OI["vermil"]
    ax.add_patch(
        FancyBboxPatch(
            (0.04, 0.16),
            0.92,
            0.09,
            boxstyle="round,pad=0.012,rounding_size=0.012",
            facecolor="#EAF0F6",
            edgecolor="white",
            linewidth=1.0,
        )
    )
    ax.text(
        0.055,
        0.205,
        "REPEATABLE SEMANTICS" if repeatable else "REPLAY ASSERTION FAILED",
        ha="left",
        va="center",
        fontsize=8.5,
        fontweight="bold",
        color=badge_color,
    )
    ax.text(
        0.28,
        0.205,
        "same-target friction increases · unrelated target is unchanged · passive decay recovers the decision",
        ha="left",
        va="center",
        fontsize=8.2,
        color="#526176",
    )
    ax.text(
        0.04,
        0.10,
        "Evidence boundary: this is an executable contract replay, not an attestation, causal estimate, or external-workload result.",
        ha="left",
        va="center",
        fontsize=8.2,
        color="#526176",
        style="italic",
    )
    _add_provenance_note(fig)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _save(fig, "replay_contract.png")
