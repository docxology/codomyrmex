"""Identity Module.

Provides Persona management, Bio-Cognitive Verification (heartbeat, EEG),
and Persona rotation.
"""

import contextlib

from .biocognitive import (
    BioCognitiveVerifier,
    EEGFrequencyAnalyzer,
    HeartbeatValidator,
    analyze_eeg_bands,
    verify_biocognitive,
    verify_heartbeat_intervals,
)
from .manager import IdentityManager, PersonaRotator, RotationRecord
from .persona import Persona, VerificationLevel

# Shared schemas for cross-module interop
with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus


def cli_commands():
    """Return CLI commands for the identity module."""
    return {
        "providers": {
            "help": "list identity providers and verification methods",
            "handler": lambda **kwargs: print(
                "Identity Providers:\n"
                f"  - Identity Manager: {IdentityManager.__name__}\n"
                f"  - Bio-Cognitive Verifier: {BioCognitiveVerifier.__name__}\n"
                f"  - Heartbeat Validator: {HeartbeatValidator.__name__}\n"
                f"  - EEG Frequency Analyzer: {EEGFrequencyAnalyzer.__name__}\n"
                f"  - Persona Rotator: {PersonaRotator.__name__}\n"
                f"  - Persona: {Persona.__name__}\n"
                f"  Verification levels: {[v.name for v in VerificationLevel] if hasattr(VerificationLevel, '__iter__') else 'available'}"
            ),
        },
        "whoami": {
            "help": "Show current identity information",
            "handler": lambda **kwargs: print(
                "Current Identity:\n"
                "  Manager: IdentityManager (available)\n"
                "  Bio-Cognitive Verifier: available\n"
                "  Heartbeat Validator: available\n"
                "  EEG Frequency Analyzer: available\n"
                "  Persona Rotator: available"
            ),
        },
    }


__all__ = [
    "BioCognitiveVerifier",
    "EEGFrequencyAnalyzer",
    "HeartbeatValidator",
    "IdentityManager",
    "Persona",
    "PersonaRotator",
    "RotationRecord",
    "VerificationLevel",
    "analyze_eeg_bands",
    "cli_commands",
    "verify_biocognitive",
    "verify_heartbeat_intervals",
]
