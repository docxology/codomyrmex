"""Figure generation orchestrator."""

from __future__ import annotations

import hashlib
import json

from codomyrmex.manuscript.figures._common import FIGDIR
from codomyrmex.manuscript.figures.cover import fig_cover_art
from codomyrmex.manuscript.figures.falsification_vectors import (
    fig_falsification_vectors,
)
from codomyrmex.manuscript.figures.fep_correspondence import fig_fep_correspondence
from codomyrmex.manuscript.figures.gate_heatmap import fig_gate_score_heatmap
from codomyrmex.manuscript.figures.gate_score_3d import fig_gate_score_3d
from codomyrmex.manuscript.figures.pheromone_decay import fig_pheromone_decay
from codomyrmex.manuscript.figures.pressure_loop import fig_colony_pressure_loop
from codomyrmex.manuscript.figures.subsystem_architecture import (
    fig_subsystem_architecture,
)
from codomyrmex.manuscript.figures.trust_trajectory import fig_trust_trajectory

_FIGURE_GENERATORS = (
    ("cover.png", fig_cover_art, "schematic"),
    ("colony_pressure_loop.png", fig_colony_pressure_loop, "schematic"),
    ("pheromone_decay.png", fig_pheromone_decay, "analytic"),
    ("gate_score_heatmap.png", fig_gate_score_heatmap, "analytic"),
    ("trust_trajectory.png", fig_trust_trajectory, "deterministic-fixture"),
    ("falsification_vectors.png", fig_falsification_vectors, "code-taxonomy"),
    ("subsystem_architecture.png", fig_subsystem_architecture, "schematic"),
    ("gate_score_3d.png", fig_gate_score_3d, "analytic"),
    ("fep_correspondence.png", fig_fep_correspondence, "conceptual-analogy"),
)


def _write_registry() -> None:
    entries = []
    for filename, _generator, evidence_class in _FIGURE_GENERATORS:
        path = FIGDIR / filename
        payload = path.read_bytes()
        entries.append(
            {
                "filename": filename,
                "evidence_class": evidence_class,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    registry = {"schema_version": 1, "count": len(entries), "figures": entries}
    destination = FIGDIR / "figure_registry.json"
    destination.write_text(
        json.dumps(registry, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"  saved {destination.relative_to(FIGDIR.parent.parent)}")


def main() -> None:
    print("Generating Codomyrmex manuscript figures...")
    for _filename, generator, _evidence_class in _FIGURE_GENERATORS:
        generator()
    _write_registry()
    print(f"Done — 9 figures in {FIGDIR.relative_to(FIGDIR.parent.parent)}/")


if __name__ == "__main__":
    main()
