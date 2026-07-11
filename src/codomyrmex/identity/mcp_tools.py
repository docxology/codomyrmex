"""MCP tool definitions for the identity module.

Exposes persona management and identity operations as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_manager():
    """Lazy import of IdentityManager."""
    from codomyrmex.identity.manager import IdentityManager

    return IdentityManager


def _get_persona_models():
    """Lazy import of Persona and VerificationLevel."""
    from codomyrmex.identity.persona import Persona, VerificationLevel

    return Persona, VerificationLevel


@mcp_tool(
    category="identity",
    description="list available verification levels for identity personas.",
)
def identity_list_levels() -> dict[str, Any]:
    """list all supported identity verification levels.

    Returns:
        dict with keys: status, levels
    """
    try:
        _, verification_level = _get_persona_models()
        return {
            "status": "success",
            "levels": [
                {"name": vl.name, "value": vl.value} for vl in verification_level
            ],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="identity",
    description=(
        "Create a persona with a given name and verification level, "
        "returning its full metadata."
    ),
)
def identity_create_persona(
    persona_id: str,
    name: str,
    level: str = "unverified",
    capabilities: list[str] | None = None,
) -> dict[str, Any]:
    """Create a new identity persona.

    Args:
        persona_id: Unique identifier for the persona.
        name: Human-readable display name.
        level: Verification level - one of: unverified, anonymous_verified,
               verified_anon, kyc_verified.
        capabilities: Optional list of capability strings.

    Returns:
        dict with keys: status, persona (serialized persona data)
    """
    try:
        manager_cls = _get_manager()
        _, verification_level = _get_persona_models()

        manager = manager_cls()
        vl = verification_level(level)
        persona = manager.create_persona(
            id=persona_id,
            name=name,
            level=vl,
            capabilities=capabilities,
        )
        return {
            "status": "success",
            "persona": persona.to_dict(),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="identity",
    description=(
        "Validate whether a persona's capabilities include a specific permission. "
        "Creates a temporary persona for the check."
    ),
)
def identity_check_capability(
    capabilities: list[str],
    required_capability: str,
) -> dict[str, Any]:
    """Check if a set of capabilities includes a required permission.

    Args:
        capabilities: list of capability strings the persona holds.
        required_capability: The capability to check for.

    Returns:
        dict with keys: status, has_capability, required, provided
    """
    try:
        persona_cls, verification_level = _get_persona_models()
        persona = persona_cls(
            id="_check",
            name="_capability_check",
            level=verification_level.UNVERIFIED,
            capabilities=capabilities,
        )
        has_it = persona.has_capability(required_capability)
        return {
            "status": "success",
            "has_capability": has_it,
            "required": required_capability,
            "provided": capabilities,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def _get_biocognitive():
    """Lazy import of bio-cognitive verification functions."""
    from codomyrmex.identity.biocognitive import verify_biocognitive

    return verify_biocognitive


def _get_persona_rotator():
    """Lazy import of PersonaRotator and IdentityManager."""
    from codomyrmex.identity.manager import IdentityManager, PersonaRotator

    return PersonaRotator, IdentityManager


@mcp_tool(
    category="identity",
    description=(
        "Verify identity using bio-cognitive signals: keystroke dynamics, "
        "heartbeat intervals (HRV), and/or EEG frequency-band analysis. "
        "Supports multi-modal verification when multiple signal types are provided."
    ),
)
def identity_verify_biocognitive(
    user_id: str,
    keystroke_values: list[float] | None = None,
    current_keystroke: float | None = None,
    heartbeat_intervals: list[float] | None = None,
    heartbeat_baseline: list[float] | None = None,
    eeg_samples: list[float] | None = None,
    eeg_baseline: list[float] | None = None,
    eeg_sampling_rate: float = 256.0,
) -> dict[str, Any]:
    """Perform bio-cognitive verification of a user identity.

    Pass whichever signal modalities are available; all provided modalities
    must pass for overall verification to succeed.

    Args:
        user_id: Unique identifier for the user being verified.
        keystroke_values: Baseline keystroke flight-time values for enrolment.
        current_keystroke: Current keystroke flight-time to verify.
        heartbeat_intervals: Current RR-interval samples (ms) to verify.
        heartbeat_baseline: Baseline RR-intervals (ms) for enrolment.
        eeg_samples: Current EEG amplitude samples to verify.
        eeg_baseline: Baseline EEG samples for enrolment.
        eeg_sampling_rate: EEG sampling rate in Hz (default 256).

    Returns:
        dict with keys: status, verified, modalities, confidence
    """
    try:
        verify_fn = _get_biocognitive()
        return verify_fn(
            user_id=user_id,
            keystroke_values=keystroke_values,
            current_keystroke=current_keystroke,
            heartbeat_intervals=heartbeat_intervals,
            heartbeat_baseline=heartbeat_baseline,
            eeg_samples=eeg_samples,
            eeg_baseline=eeg_baseline,
            eeg_sampling_rate=eeg_sampling_rate,
        )
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="identity",
    description=(
        "Rotate the active identity persona to a different registered persona. "
        "Supports direct rotation to a persona ID, round-robin next, and "
        "preferred/sticky persona rotation. Can optionally register personas "
        "inline before rotating. Returns the new active persona and rotation history."
    ),
)
def identity_rotate_persona(
    persona_id: str | None = None,
    mode: str = "direct",
    reason: str = "",
    set_preferred: bool = False,
    clear_preferred: bool = False,
    register_personas: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Rotate the active identity persona.

    Modes:
        - ``direct``: rotate to the persona specified by *persona_id*.
        - ``next``: round-robin to the next registered persona.
        - ``preferred``: rotate to the previously set preferred persona.

    Args:
        persona_id: Target persona ID (required for ``mode='direct'``).
        mode: Rotation mode - one of: direct, next, preferred.
        reason: Optional reason for the rotation (recorded in history).
        set_preferred: If True, set *persona_id* as the preferred persona
                       before rotating (only valid with ``mode='direct'``).
        clear_preferred: If True, clear the preferred persona after rotation.
        register_personas: Optional list of persona specs to register before
                           rotating. Each spec is a dict with keys: id, name,
                           level (optional, default 'unverified'), capabilities
                           (optional list of str).

    Returns:
        dict with keys: status, active_persona, rotation_history,
                        rotation_count, registered_count
    """
    try:
        rotator_cls, manager_cls = _get_persona_rotator()
        manager = manager_cls()
        rotator = rotator_cls(manager)

        # Optionally register personas inline
        registered_count = 0
        if register_personas:
            persona_cls, verification_level = _get_persona_models()
            for spec in register_personas:
                pid = spec.get("id", "")
                pname = spec.get("name", pid)
                plevel_str = spec.get("level", "unverified")
                pcap = spec.get("capabilities")
                try:
                    plevel = verification_level(plevel_str)
                except ValueError:
                    plevel = verification_level.UNVERIFIED
                if manager.get_persona(pid) is None:
                    manager.create_persona(
                        id=pid,
                        name=pname,
                        level=plevel,
                        capabilities=pcap,
                    )
                    registered_count += 1

        if mode == "direct":
            if persona_id is None:
                return {
                    "status": "error",
                    "message": "persona_id required for mode='direct'",
                }
            if set_preferred:
                rotator.set_preferred(persona_id)
            rotator.rotate_to(persona_id, reason=reason)
        elif mode == "next":
            rotator.rotate_next(reason=reason)
        elif mode == "preferred":
            result = rotator.rotate_to_preferred(reason=reason)
            if result is None:
                return {
                    "status": "error",
                    "message": "No preferred persona set",
                }
        else:
            return {
                "status": "error",
                "message": f"Unknown rotation mode: {mode}. Use direct, next, or preferred.",
            }

        if clear_preferred:
            rotator.clear_preferred()

        active = rotator.current_persona
        return {
            "status": "success",
            "active_persona": active.to_dict() if active else None,
            "rotation_history": rotator.get_history_dicts(),
            "rotation_count": rotator.rotation_count(),
            "registered_count": registered_count,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
