"""codomyrmex.meme.narrative — Computational Narratology."""

from codomyrmex.meme.narrative.engine import NarrativeEngine
from codomyrmex.meme.narrative.models import (
    Archetype,
    Narrative,
    NarrativeArc,
    NarrativeTemplate,
)
from codomyrmex.meme.narrative.myth import synthesize_myth
from codomyrmex.meme.narrative.structure import (
    fichtean_curve_arc,
    freytag_pyramid_arc,
    heros_journey_arc,
)

__all__ = [
    "Narrative",
    "NarrativeArc",
    "Archetype",
    "NarrativeTemplate",
    "NarrativeEngine",
    "heros_journey_arc",
    "freytag_pyramid_arc",
    "fichtean_curve_arc",
    "synthesize_myth",
]
