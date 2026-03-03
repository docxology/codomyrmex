"""MCP Tools for the identity module."""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .biocognitive import BioCognitiveVerifier
from .manager import IdentityManager
from .persona import VerificationLevel

# Create global instances for the MCP tools to interact with
_identity_manager = IdentityManager()
_biocognitive_verifier = BioCognitiveVerifier()


@mcp_tool(
    name="identity_create_persona",
    description="Create and register a new persona.",
    category="identity",
)
def identity_create_persona(
    id: str, name: str, level: str = "unverified", capabilities: list[str] | None = None
) -> dict[str, Any]:
    """Create and register a new persona.

    Args:
        id: Unique identifier for the persona.
        name: Human-readable name for the persona.
        level: The verification level (unverified, anonymous_verified, verified_anon, kyc_verified).
        capabilities: Optional list of permissions/actions this persona can perform.

    Returns:
        dict: Status and details of the newly created persona.
    """
    try:
        v_level = VerificationLevel(level)
    except ValueError:
        return {"error": f"Invalid verification level: {level}"}

    try:
        persona = _identity_manager.create_persona(id, name, v_level, capabilities)
        return {"status": "success", "persona": persona.to_dict()}
    except ValueError as e:
        return {"error": str(e)}


@mcp_tool(
    name="identity_set_active_persona",
    description="Switch the active persona context.",
    category="identity",
)
def identity_set_active_persona(id: str) -> dict[str, Any]:
    """Switch the active persona context.

    Args:
        id: The ID of the persona to set as active.

    Returns:
        dict: Status of the operation.
    """
    try:
        _identity_manager.set_active_persona(id)
        return {"status": "success", "message": f"Switched active persona to {id}"}
    except ValueError as e:
        return {"error": str(e)}


@mcp_tool(
    name="identity_revoke_persona",
    description="Revoke a persona, making it inactive.",
    category="identity",
)
def identity_revoke_persona(id: str) -> dict[str, Any]:
    """Revoke a persona, making it inactive.

    Args:
        id: The ID of the persona to revoke.

    Returns:
        dict: Status of the operation.
    """
    success = _identity_manager.revoke_persona(id)
    if success:
        return {"status": "success", "message": f"Revoked persona {id}"}
    return {"error": f"Persona {id} not found"}


@mcp_tool(
    name="identity_list_personas",
    description="List all personas, optionally filtered by level.",
    category="identity",
)
def identity_list_personas(level: str | None = None) -> dict[str, Any]:
    """List all personas, optionally filtered by verification level.

    Args:
        level: Optional VerificationLevel string to filter results.

    Returns:
        dict: List of personas.
    """
    v_level = None
    if level:
        try:
            v_level = VerificationLevel(level)
        except ValueError:
            return {"error": f"Invalid verification level: {level}"}

    personas = _identity_manager.list_personas(v_level)
    return {"status": "success", "personas": [p.to_dict() for p in personas]}


@mcp_tool(
    name="identity_promote_persona",
    description="Update the trust level of a persona.",
    category="identity",
)
def identity_promote_persona(id: str, new_level: str) -> dict[str, Any]:
    """Update the trust level of a persona.

    Args:
        id: The ID of the persona to promote.
        new_level: The new verification level string.

    Returns:
        dict: Status of the promotion.
    """
    try:
        v_level = VerificationLevel(new_level)
    except ValueError:
        return {"error": f"Invalid verification level: {new_level}"}

    success = _identity_manager.promote_persona(id, v_level)
    if success:
        return {"status": "success", "message": f"Promoted persona {id} to {new_level}"}
    return {"error": f"Persona {id} not found"}


@mcp_tool(
    name="identity_export_persona",
    description="Export non-sensitive persona data.",
    category="identity",
)
def identity_export_persona(id: str) -> dict[str, Any]:
    """Export non-sensitive persona data.

    Args:
        id: The ID of the persona to export.

    Returns:
        dict: Persona data or error.
    """
    data = _identity_manager.export_persona(id)
    if data:
        return {"status": "success", "persona": data}
    return {"error": f"Persona {id} not found"}


@mcp_tool(
    name="identity_record_metric",
    description="Record a new behavioral metric sample.",
    category="identity",
)
def identity_record_metric(user_id: str, metric: str, value: float) -> dict[str, Any]:
    """Record a new behavioral metric sample.

    Args:
        user_id: Unique identifier for the user or persona.
        metric: The name of the metric being recorded.
        value: The observed value of the metric.

    Returns:
        dict: Status of the recording.
    """
    _biocognitive_verifier.record_metric(user_id, metric, value)
    return {"status": "success", "message": f"Recorded {metric} for {user_id}"}


@mcp_tool(
    name="identity_verify_metric",
    description="Verify if current value matches user's baseline.",
    category="identity",
)
def identity_verify_metric(
    user_id: str, metric: str, current_value: float
) -> dict[str, Any]:
    """Verify if current value matches user's baseline using statistical analysis.

    Args:
        user_id: Unique identifier for the user to verify.
        metric: The name of the metric to check.
        current_value: The current observed value to be verified.

    Returns:
        dict: Verification result (True/False).
    """
    result = _biocognitive_verifier.verify(user_id, metric, current_value)
    return {"status": "success", "verified": result}


@mcp_tool(
    name="identity_enroll_metric",
    description="Enroll a user with a full baseline for a specific metric.",
    category="identity",
)
def identity_enroll_metric(
    user_id: str, metric_type: str, baseline: list[float]
) -> dict[str, Any]:
    """Enroll a user with a full baseline for a specific metric.

    Args:
        user_id: The ID of the user to enroll.
        metric_type: The name of the metric being enrolled.
        baseline: A list of baseline values for that metric.

    Returns:
        dict: Status of the enrollment.
    """
    _biocognitive_verifier.enroll(user_id, metric_type, baseline)
    return {"status": "success", "message": f"Enrolled {metric_type} for {user_id}"}


@mcp_tool(
    name="identity_get_confidence",
    description="Calculate aggregate confidence score for a user's identity.",
    category="identity",
)
def identity_get_confidence(user_id: str) -> dict[str, Any]:
    """Calculate aggregate confidence score for a user's identity based on data volume.

    Args:
        user_id: The ID of the user to check confidence for.

    Returns:
        dict: Confidence score (0.0 to 1.0).
    """
    score = _biocognitive_verifier.get_confidence(user_id)
    return {"status": "success", "confidence": score}
