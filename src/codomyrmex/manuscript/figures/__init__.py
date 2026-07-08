"""Publication figure generators for the Codomyrmex manuscript."""

from codomyrmex.manuscript.figures.generators import (
    fig_colony_pressure_loop,
    fig_cover_art,
    fig_falsification_vectors,
    fig_fep_correspondence,
    fig_formula_comparison,
    fig_gate_score_3d,
    fig_gate_score_heatmap,
    fig_pheromone_decay,
    fig_subsystem_architecture,
    fig_trust_trajectory,
    main,
)

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
    ("formula_comparison.png", fig_formula_comparison),
]

__all__ = [
    "FIGURES",
    "fig_colony_pressure_loop",
    "fig_cover_art",
    "fig_falsification_vectors",
    "fig_fep_correspondence",
    "fig_formula_comparison",
    "fig_gate_score_3d",
    "fig_gate_score_heatmap",
    "fig_pheromone_decay",
    "fig_subsystem_architecture",
    "fig_trust_trajectory",
    "main",
]
