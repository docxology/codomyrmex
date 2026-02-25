"""codomyrmex.meme.hyperreality — Simulation & Simulacra."""

from codomyrmex.meme.hyperreality.engine import HyperrealityEngine
from codomyrmex.meme.hyperreality.models import (
    OntologicalStatus,
    RealityTunnel,
    Simulacrum,
    SimulationLevel,
)
from codomyrmex.meme.hyperreality.simulation import (
    assess_reality_level,
    generate_simulacrum,
)

__all__ = [
    "Simulacrum",
    "SimulationLevel",
    "RealityTunnel",
    "OntologicalStatus",
    "HyperrealityEngine",
    "assess_reality_level",
    "generate_simulacrum",
]
