"""codomyrmex.meme.contagion — Information Cascade & Contagion Dynamics."""

from codomyrmex.meme.contagion.cascade import CascadeDetector, detect_cascades
from codomyrmex.meme.contagion.epidemic import SEIRModel, SIRModel, SISModel
from codomyrmex.meme.contagion.models import (
    Cascade,
    CascadeType,
    ContagionModel,
    PropagationTrace,
    ResonanceMap,
)
from codomyrmex.meme.contagion.simulation import run_simulation

__all__ = [
    "ContagionModel",
    "CascadeDetector",
    "PropagationTrace",
    "Cascade",
    "CascadeType",
    "ResonanceMap",
    "SIRModel",
    "SISModel",
    "SEIRModel",
    "detect_cascades",
    "run_simulation",
]
