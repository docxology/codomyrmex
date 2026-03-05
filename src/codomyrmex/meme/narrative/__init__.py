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
    "Archetype",
    "Narrative",
    "NarrativeArc",
    "NarrativeEngine",
    "NarrativeTemplate",
    "fichtean_curve_arc",
    "freytag_pyramid_arc",
    "heros_journey_arc",
    "synthesize_myth",
]
