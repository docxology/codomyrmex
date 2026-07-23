"""SQLite persistence and restart fixture."""

from __future__ import annotations

import tempfile
from pathlib import Path

import matplotlib.pyplot as plt

from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig
from codomyrmex.colony_kernel.models import (
    ColonySignal,
    DecayRate,
    SignalSource,
    SignalType,
)
from codomyrmex.colony_kernel.research.persistent_store import PersistentPheromoneStore
from codomyrmex.manuscript.figures._common import _OI, _add_provenance_note, _save


def fig_persistence_recovery() -> None:
    with tempfile.TemporaryDirectory(
        prefix="codomyrmex-persistence-figure-"
    ) as directory:
        db_path = Path(directory) / "signals.sqlite"
        store = PersistentPheromoneStore(
            db_path, config=StigmergyConfig(max_strength=10.0)
        )
        store.deposit_signal(
            ColonySignal(
                location="figure.py",
                signal_type=SignalType.FAILURE,
                strength=1.0,
                decay_rate=DecayRate.NORMAL,
                source=SignalSource.TEST,
            )
        )
        before = store.sense("figure.py", SignalType.FAILURE)
        store.close()
        restarted = PersistentPheromoneStore(db_path)
        after_restart = restarted.sense("figure.py", SignalType.FAILURE)
        restarted.evaporate()
        after_decay = restarted.sense("figure.py", SignalType.FAILURE)
        restarted.close()

    labels = ("after deposit", "after restart", "after one decay")
    values = (before, after_restart, after_decay)
    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    bars = ax.bar(labels, values, color=(_OI["blue"], _OI["green"], _OI["orange"]))
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    ax.set_ylabel("Stored failure strength")
    ax.set_title("Persistent signal restart and decay fixture")
    ax.set_ylim(0, max(values) * 1.25 if max(values) else 1)
    ax.grid(axis="y", alpha=0.2)
    _add_provenance_note(fig)
    _save(fig, "persistence_recovery.png")


__all__ = ["fig_persistence_recovery"]
