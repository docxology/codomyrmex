"""Figure generation orchestrator."""

from __future__ import annotations

import hashlib
import json

from codomyrmex.manuscript.figures._common import FIGDIR, _figure_metadata, _var_str
from codomyrmex.manuscript.figures.attestation_event_chain import (
    fig_attestation_event_chain,
)
from codomyrmex.manuscript.figures.calibration_reliability import (
    fig_calibration_reliability,
)
from codomyrmex.manuscript.figures.cover import fig_cover_art
from codomyrmex.manuscript.figures.falsification_vectors import (
    fig_falsification_vectors,
)
from codomyrmex.manuscript.figures.fep_correspondence import fig_fep_correspondence
from codomyrmex.manuscript.figures.formalism_code_crosswalk import (
    fig_formalism_code_crosswalk,
)
from codomyrmex.manuscript.figures.formalism_coverage import fig_formalism_coverage
from codomyrmex.manuscript.figures.gate_heatmap import fig_gate_score_heatmap
from codomyrmex.manuscript.figures.gate_score_3d import fig_gate_score_3d
from codomyrmex.manuscript.figures.persistence_recovery import fig_persistence_recovery
from codomyrmex.manuscript.figures.pheromone_decay import fig_pheromone_decay
from codomyrmex.manuscript.figures.pressure_loop import fig_colony_pressure_loop
from codomyrmex.manuscript.figures.replay_contract import fig_replay_contract
from codomyrmex.manuscript.figures.research_roadmap import fig_research_roadmap
from codomyrmex.manuscript.figures.research_status_matrix import (
    fig_research_status_matrix,
)
from codomyrmex.manuscript.figures.safety_utility_frontier import (
    fig_safety_utility_frontier,
)
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
    ("research_roadmap.png", fig_research_roadmap, "research-plan"),
    ("formalism_code_crosswalk.png", fig_formalism_code_crosswalk, "formal-crosswalk"),
    ("replay_contract.png", fig_replay_contract, "deterministic-fixture"),
    (
        "attestation_event_chain.png",
        fig_attestation_event_chain,
        "authenticated-fixture",
    ),
    ("safety_utility_frontier.png", fig_safety_utility_frontier, "offline-synthetic"),
    ("calibration_reliability.png", fig_calibration_reliability, "calibration-status"),
    ("persistence_recovery.png", fig_persistence_recovery, "restart-fixture"),
    ("formalism_coverage.png", fig_formalism_coverage, "formalism-inventory"),
    ("research_status_matrix.png", fig_research_status_matrix, "research-status"),
)


def _write_registry() -> None:
    entries = []
    for filename, _generator, evidence_class in _FIGURE_GENERATORS:
        path = FIGDIR / filename
        payload = path.read_bytes()
        metadata = _figure_metadata(filename)
        entries.append(
            {
                "filename": filename,
                "label": metadata.get("label", ""),
                "width": metadata.get("width", ""),
                "evidence_class": metadata.get("evidence_class", evidence_class),
                "caption": metadata.get("caption", ""),
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    registry = {
        "schema_version": 2,
        "config_hash": _var_str("CONFIG_HASH"),
        "count": len(entries),
        "figures": entries,
    }
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
    print(
        f"Done — {len(_FIGURE_GENERATORS)} figures in "
        f"{FIGDIR.relative_to(FIGDIR.parent.parent)}/"
    )


if __name__ == "__main__":
    main()
