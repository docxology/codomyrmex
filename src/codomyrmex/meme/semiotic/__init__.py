"""codomyrmex.meme.semiotic — Computational Semiotics."""

from codomyrmex.meme.semiotic.models import (
    Sign,
    SignType,
    DriftReport,
    SemanticTerritory,
)
from codomyrmex.meme.semiotic.analyzer import SemioticAnalyzer
from codomyrmex.meme.semiotic.encoding import SemioticEncoder
from codomyrmex.meme.semiotic.mnemonics import MnemonicDevice

__all__ = [
    "Sign",
    "SignType",
    "DriftReport",
    "SemanticTerritory",
    "SemioticAnalyzer",
    "SemioticEncoder",
    "MnemonicDevice",
]
