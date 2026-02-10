"""Identity Module.

Provides Persona management and Bio-Cognitive Verification.
"""

from .biocognitive import BioCognitiveVerifier
from .manager import IdentityManager
from .persona import Persona, VerificationLevel

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the identity module."""
    return {
        "providers": {
            "help": "List identity providers and verification methods",
            "handler": lambda **kwargs: print(
                "Identity Providers:\n"
                f"  - Identity Manager: {IdentityManager.__name__}\n"
                f"  - Bio-Cognitive Verifier: {BioCognitiveVerifier.__name__}\n"
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
                "  Persona system: available"
            ),
        },
    }


__all__ = [
    "Persona",
    "VerificationLevel",
    "IdentityManager",
    "BioCognitiveVerifier",
    "cli_commands",
]
