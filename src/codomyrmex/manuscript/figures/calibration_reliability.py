"""Calibration-status visual that refuses to relabel gate scores as probabilities."""

from __future__ import annotations

import matplotlib.pyplot as plt

from codomyrmex.manuscript.figures._common import (
    _OI,
    _add_provenance_note,
    _save,
    _var_str,
)


def fig_calibration_reliability() -> None:
    status = _var_str("RESULT_CALIBRATION_STATUS")
    metric = _var_str("RESULT_CALIBRATION_ECE")
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    ax.plot((0, 1), (0, 1), linestyle="--", color=_OI["grey"], label="ideal reference")
    ax.text(
        0.5,
        0.52,
        "No primary reliability estimate\n\n"
        f"status: {status}\nmetric: {metric}\n\n"
        "Gate scores are not probabilities",
        ha="center",
        va="center",
        color=_OI["blue"],
        bbox={
            "boxstyle": "round,pad=0.8",
            "facecolor": "#EAF2F8",
            "edgecolor": _OI["blue"],
        },
    )
    ax.set_xlabel("Declared confidence")
    ax.set_ylabel("Observed frequency")
    ax.set_title("Calibration gate: held-out confidence required")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, loc="lower right")
    _add_provenance_note(fig)
    _save(fig, "calibration_reliability.png")


__all__ = ["fig_calibration_reliability"]
