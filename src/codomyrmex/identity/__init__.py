"""Identity Module.

Provides Persona management and Bio-Cognitive Verification.
"""

from .biocognitive import BioCognitiveVerifier
from .manager import IdentityManager
from .mcp_tools import (
    identity_create_persona,
    identity_enroll_metric,
    identity_export_persona,
    identity_get_confidence,
    identity_list_personas,
    identity_promote_persona,
    identity_record_metric,
    identity_revoke_persona,
    identity_set_active_persona,
    identity_verify_metric,
)
from .persona import Persona, VerificationLevel

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
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
    "identity_create_persona",
    "identity_set_active_persona",
    "identity_revoke_persona",
    "identity_list_personas",
    "identity_promote_persona",
    "identity_export_persona",
    "identity_record_metric",
    "identity_verify_metric",
    "identity_enroll_metric",
    "identity_get_confidence",
]
