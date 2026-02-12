"""codomyrmex.meme.narrative — Computational Narratology."""

from codomyrmex.meme.narrative.models import (
    Narrative,
    NarrativeArc,
    Archetype,
    NarrativeTemplate,
)
from codomyrmex.meme.narrative.engine import NarrativeEngine
from codomyrmex.meme.narrative.structure import (
    heros_journey_arc,
    freytag_pyramid_arc,
    fichtean_curve_arc,
)
from codomyrmex.meme.narrative.myth import synthesize_myth

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
