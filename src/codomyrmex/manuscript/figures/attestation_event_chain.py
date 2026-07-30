"""Authenticated local execution-evidence fixture."""

from __future__ import annotations

import matplotlib.pyplot as plt

from codomyrmex.colony_kernel.attestation import AttestationLedger, HMACSigner
from codomyrmex.manuscript.figures._common import _OI, _add_provenance_note, _save


def fig_attestation_event_chain() -> None:
    """Render the signed event lifecycle without implying action safety."""
    ledger = AttestationLedger(
        signer=HMACSigner(b"manuscript-attestation-fixture-key", key_id="fixture")
    )
    run_id = "figure-attestation"
    proposal = ledger.record_proposal(
        run_id, "fixture", {"proposal_id": "proposal-1", "target": "fixture.py"}
    )
    verdict = ledger.record_gate_verdict(
        run_id, "fixture", proposal, "execute", {"decision": "execute"}
    )
    authorization = ledger.authorize_execution(run_id, "fixture", verdict)
    receipt = ledger.record_execution(
        run_id, "fixture", authorization, {"execution_id": "execution-1"}
    )
    ledger.record_outcome(run_id, "fixture", receipt, {"tests_passed": True})
    events = ledger.events(run_id)
    validation = ledger.validate(run_id)
    ledger.close()

    fig, ax = plt.subplots(figsize=(8.5, 7.6))
    background = "#F7F9FC"
    fig.patch.set_facecolor(background)
    ax.set_facecolor(background)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, len(events) + 1.25)
    ax.axis("off")
    colors = [_OI["blue"], _OI["green"], _OI["orange"], _OI["vermil"], _OI["pink"]]
    labels = {
        "proposal": "Proposal",
        "gate_verdict": "Gate verdict",
        "execution_authorization": "Execution authorization",
        "execution_receipt": "Caller-supplied execution receipt",
        "outcome": "Caller-supplied outcome",
    }
    for index, event in enumerate(events):
        y = len(events) - index - 0.05
        if index < len(events) - 1:
            ax.annotate(
                "",
                xy=(0.12, y - 0.76),
                xytext=(0.12, y - 0.28),
                arrowprops={
                    "arrowstyle": "-|>",
                    "color": _OI["grey"],
                    "lw": 1.7,
                    "mutation_scale": 14,
                },
            )
        color = colors[index % len(colors)]
        ax.scatter(
            0.12,
            y,
            s=850,
            color=color,
            edgecolors="white",
            linewidths=2.0,
            zorder=3,
        )
        ax.text(
            0.12,
            y,
            str(event.sequence),
            ha="center",
            va="center",
            color="white",
            weight="bold",
            fontsize=10,
        )
        ax.text(
            0.21,
            y + 0.15,
            labels.get(event.event_type.value, event.event_type.value),
            ha="left",
            va="center",
            fontsize=10.2,
            fontweight="bold",
            color="#172033",
        )
        ax.text(
            0.21,
            y - 0.15,
            f"actor={event.actor_id}  ·  hash={event.event_hash[:14]}…  ·  signed",
            ha="left",
            va="center",
            fontsize=8.6,
            family="monospace",
            color="#4B5563",
        )
    ax.text(
        0.0,
        len(events) + 1.08,
        "Authenticated local lifecycle fixture",
        ha="left",
        va="top",
        fontsize=12.2,
        fontweight="bold",
        color="#172033",
    )
    ax.text(
        0.0,
        len(events) + 0.78,
        "Each event binds its predecessor; printed labels and sequence numbers carry the order.",
        ha="left",
        va="top",
        fontsize=9.0,
        color="#526176",
    )
    ax.text(
        1.0,
        0.07,
        f"Chain validation: {validation.status.value} · "
        f"{len(events)} signed events · HMAC-SHA256 fixture",
        ha="right",
        va="bottom",
        fontsize=8.0,
        color="#4B5563",
    )
    ax.text(
        0.0,
        0.28,
        "Local integrity only — no independent observation\n"
        "of external actuation or safety",
        ha="left",
        va="bottom",
        fontsize=8.1,
        color="#7F1D1D",
        fontweight="bold",
        linespacing=1.15,
    )
    _add_provenance_note(fig)
    fig.tight_layout(rect=(0.02, 0.06, 0.98, 0.99))
    _save(fig, "attestation_event_chain.png")


__all__ = ["fig_attestation_event_chain"]
