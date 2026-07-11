"""Figure generation orchestrator."""

from __future__ import annotations

from codomyrmex.manuscript.figures._common import FIGDIR
from codomyrmex.manuscript.figures.cover import fig_cover_art
from codomyrmex.manuscript.figures.falsification_vectors import (
    fig_falsification_vectors,
)
from codomyrmex.manuscript.figures.fep_correspondence import fig_fep_correspondence
from codomyrmex.manuscript.figures.formula_comparison import fig_formula_comparison
from codomyrmex.manuscript.figures.gate_heatmap import fig_gate_score_heatmap
from codomyrmex.manuscript.figures.gate_score_3d import fig_gate_score_3d
from codomyrmex.manuscript.figures.pheromone_decay import fig_pheromone_decay
from codomyrmex.manuscript.figures.pressure_loop import fig_colony_pressure_loop
from codomyrmex.manuscript.figures.subsystem_architecture import (
    fig_subsystem_architecture,
)
from codomyrmex.manuscript.figures.trust_trajectory import fig_trust_trajectory


def main() -> None:
    print("Generating Codomyrmex manuscript figures...")
    fig_cover_art()
    fig_colony_pressure_loop()
    fig_pheromone_decay()
    fig_gate_score_heatmap()
    fig_trust_trajectory()
    fig_falsification_vectors()
    fig_subsystem_architecture()
    fig_gate_score_3d()
    fig_fep_correspondence()
    fig_formula_comparison()
    print(f"Done — 10 figures in {FIGDIR.relative_to(FIGDIR.parent.parent)}/")


if __name__ == "__main__":
    main()
