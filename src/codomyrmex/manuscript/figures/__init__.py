"""Publication figure generators for the Codomyrmex manuscript."""

import os

# Load a headless backend before any generator imports pyplot. This keeps local
# macOS rendering and CI deterministic and avoids creating GUI windows.
os.environ["MPLBACKEND"] = "Agg"

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
from codomyrmex.manuscript.figures.orchestrator import main
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

FIGURES: list[tuple[str, object]] = [
    ("cover.png", fig_cover_art),
    ("colony_pressure_loop.png", fig_colony_pressure_loop),
    ("pheromone_decay.png", fig_pheromone_decay),
    ("gate_score_heatmap.png", fig_gate_score_heatmap),
    ("trust_trajectory.png", fig_trust_trajectory),
    ("falsification_vectors.png", fig_falsification_vectors),
    ("subsystem_architecture.png", fig_subsystem_architecture),
    ("gate_score_3d.png", fig_gate_score_3d),
    ("fep_correspondence.png", fig_fep_correspondence),
    ("research_roadmap.png", fig_research_roadmap),
    ("formalism_code_crosswalk.png", fig_formalism_code_crosswalk),
    ("replay_contract.png", fig_replay_contract),
    ("attestation_event_chain.png", fig_attestation_event_chain),
    ("safety_utility_frontier.png", fig_safety_utility_frontier),
    ("calibration_reliability.png", fig_calibration_reliability),
    ("persistence_recovery.png", fig_persistence_recovery),
    ("formalism_coverage.png", fig_formalism_coverage),
    ("research_status_matrix.png", fig_research_status_matrix),
]

__all__ = [
    "FIGURES",
    "fig_attestation_event_chain",
    "fig_calibration_reliability",
    "fig_colony_pressure_loop",
    "fig_cover_art",
    "fig_falsification_vectors",
    "fig_fep_correspondence",
    "fig_formalism_code_crosswalk",
    "fig_formalism_coverage",
    "fig_gate_score_3d",
    "fig_gate_score_heatmap",
    "fig_persistence_recovery",
    "fig_pheromone_decay",
    "fig_replay_contract",
    "fig_research_roadmap",
    "fig_research_status_matrix",
    "fig_safety_utility_frontier",
    "fig_subsystem_architecture",
    "fig_trust_trajectory",
    "main",
]
