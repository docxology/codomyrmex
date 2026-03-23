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
