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

    fig, ax = plt.subplots(figsize=(14, 3.8))
    ax.set_xlim(-0.6, len(events) - 0.4)
    ax.set_ylim(-0.9, 1.1)
    ax.axis("off")
    colors = [_OI["blue"], _OI["green"], _OI["orange"], _OI["vermil"], _OI["pink"]]
    for index, event in enumerate(events):
        if index < len(events) - 1:
            ax.annotate(
                "",
                xy=(index + 0.82, 0),
                xytext=(index + 0.18, 0),
                arrowprops={"arrowstyle": "->", "color": _OI["grey"], "lw": 1.4},
            )
        ax.scatter(index, 0, s=1250, color=colors[index % len(colors)], zorder=3)
        ax.text(
            index,
            0,
            str(event.sequence),
            ha="center",
            va="center",
            color="white",
            weight="bold",
        )
        ax.text(
            index,
            0.42,
            event.event_type.value.replace("_", "\n"),
            ha="center",
            va="bottom",
            fontsize=8,
        )
        ax.text(
            index,
            -0.42,
            f"hash {event.event_hash[:10]}…",
            ha="center",
            va="top",
            fontsize=7,
            family="monospace",
        )
    ax.text(
        len(events) - 0.05,
        -0.78,
        f"validation={validation.status.value} · {len(events)} events · HMAC-SHA256 fixture",
        ha="right",
        va="top",
        fontsize=8,
        color="#4B5563",
    )
    _add_provenance_note(fig)
    _save(fig, "attestation_event_chain.png")


__all__ = ["fig_attestation_event_chain"]
