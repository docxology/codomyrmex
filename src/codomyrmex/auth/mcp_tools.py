"""MCP tools for the auth module.

Exposes authentication, token validation, and provider listing as
auto-discovered MCP tools. Zero external dependencies beyond the
auth module itself.
"""

from __future__ import annotations

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="auth",
    description=(
        "Authenticate with credential parameters and return a token "
        "dictionary. credentials is a dict (e.g. {'api_key': '...'})."
    ),
)
def auth_authenticate(credentials: dict) -> dict | None:
    """Authenticate and return a token representation.

    Args:
        credentials: Authentication credentials dict.

    Returns:
        Token dict or None if authentication fails.
    """
    from codomyrmex.auth import authenticate

    token = authenticate(credentials)
    if token is None:
        return None
    # Convert Token to dict for JSON transport
    if hasattr(token, "__dict__"):
        return {k: str(v) for k, v in token.__dict__.items()}
    return {"token": str(token)}


@mcp_tool(
    category="auth",
    description=(
        "Validate whether a token string is well-formed and not expired. "
        "Returns a dict with 'valid' (bool) and 'reason' (str)."
    ),
)
def auth_validate_token(token_value: str) -> dict:
    """Validate a token string.

    Args:
        token_value: The raw token string to validate.

    Returns:
        Dictionary with 'valid' bool and 'reason' string.
    """
    from codomyrmex.auth import TokenValidator

    validator = TokenValidator(secret="mcp_tool_validation_key")
    try:
        result = validator.validate_signed_token(token_value)
        if result is None:
            return {"valid": False, "reason": "invalid or expired token"}
        return {"valid": True, "reason": "ok"}
    except Exception as exc:
        return {"valid": False, "reason": str(exc)}


@mcp_tool(
    category="auth",
    description=(
        "list available authentication provider class names "
        "(e.g. Authenticator, APIKeyManager, TokenManager)."
    ),
)
def auth_list_providers() -> list[str]:
    """Return the names of available auth provider classes."""
    return [
        "Authenticator",
        "APIKeyManager",
        "TokenManager",
        "TokenValidator",
        "PermissionRegistry",
    ]
