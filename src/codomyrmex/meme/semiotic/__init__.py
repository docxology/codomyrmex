"""codomyrmex.meme.semiotic — Computational Semiotics."""

from codomyrmex.meme.semiotic.analyzer import SemioticAnalyzer
from codomyrmex.meme.semiotic.encoding import SemioticEncoder
from codomyrmex.meme.semiotic.mnemonics import MnemonicDevice
from codomyrmex.meme.semiotic.models import (
    DriftReport,
    SemanticTerritory,
    Sign,
    SignType,
)

__all__ = [
    "Sign",
    "SignType",
    "DriftReport",
    "SemanticTerritory",
    "SemioticAnalyzer",
    "SemioticEncoder",
    "MnemonicDevice",
]
