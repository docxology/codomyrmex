"""Tests for auth MCP tools.

Zero-mock policy: tests use the real auth module classes.
"""

from __future__ import annotations


def test_import_mcp_tools() -> None:
    """All three MCP tools are importable without errors."""
    from codomyrmex.auth.mcp_tools import (
        auth_authenticate,
        auth_list_providers,
        auth_validate_token,
    )

    assert callable(auth_authenticate)
    assert callable(auth_validate_token)
    assert callable(auth_list_providers)


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.auth.mcp_tools import (
        auth_authenticate,
        auth_list_providers,
        auth_validate_token,
    )

    for fn in (auth_authenticate, auth_validate_token, auth_list_providers):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
        assert fn._mcp_tool_meta.get("category") == "auth"


def test_list_providers_returns_list() -> None:
    """auth_list_providers returns a non-empty list of strings."""
    from codomyrmex.auth.mcp_tools import auth_list_providers

    result = auth_list_providers()
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(p, str) for p in result)


def test_list_providers_includes_authenticator() -> None:
    """auth_list_providers includes 'Authenticator'."""
    from codomyrmex.auth.mcp_tools import auth_list_providers

    assert "Authenticator" in auth_list_providers()


def test_validate_token_returns_dict() -> None:
    """auth_validate_token returns a dict with 'valid' and 'reason'."""
    from codomyrmex.auth.mcp_tools import auth_validate_token

    result = auth_validate_token("test_token_12345")
    assert isinstance(result, dict)
    assert "valid" in result
    assert "reason" in result
    assert isinstance(result["valid"], bool)


def test_authenticate_with_empty_credentials() -> None:
    """auth_authenticate with empty dict returns None or a token dict."""
    from codomyrmex.auth.mcp_tools import auth_authenticate

    result = auth_authenticate({})
    # Either None (no match) or a dict (token)
    assert result is None or isinstance(result, dict)


def test_authenticate_success() -> None:
    """auth_authenticate returns a token dict when authentication succeeds."""
    from codomyrmex.auth import get_authenticator
    from codomyrmex.auth.mcp_tools import auth_authenticate

    # Register a user to authenticate against
    auth = get_authenticator()
    auth.register_user("mcp_test_user", "mcp_test_password", roles=["mcp_role"])

    credentials = {"username": "mcp_test_user", "password": "mcp_test_password"}
    result = auth_authenticate(credentials)

    assert isinstance(result, dict)
    assert "user_id" in result
    assert result["user_id"] == "mcp_test_user"


def test_validate_token_valid() -> None:
    """auth_validate_token returns valid=True for a valid token."""
    from codomyrmex.auth import TokenValidator
    from codomyrmex.auth.mcp_tools import auth_validate_token

    # Generate a valid token signed with the key used in auth_validate_token
    validator = TokenValidator(secret="mcp_tool_validation_key")
    token_value = validator.sign_token_data({"user_id": "test_user"})

    result = auth_validate_token(token_value)
    assert isinstance(result, dict)
    assert result.get("valid") is True
    assert result.get("reason") == "ok"


def test_validate_token_invalid_format() -> None:
    """auth_validate_token returns valid=False for completely invalid tokens."""
    from codomyrmex.auth.mcp_tools import auth_validate_token

    result = auth_validate_token("not_a_base64_string")
    assert isinstance(result, dict)
    assert result.get("valid") is False
    assert result.get("reason") == "invalid or expired token"


def test_validate_token_exception_handling() -> None:
    """auth_validate_token catches exceptions and returns valid=False."""
    from codomyrmex.auth.mcp_tools import auth_validate_token

    # Provide a value that causes an exception in TokenValidator.validate_signed_token
    # For example, passing an integer instead of string or something that base64 fails on
    # Though mypy enforces string, let's pass an invalid type to trigger the catch block
    result = auth_validate_token(12345) # type: ignore
    assert isinstance(result, dict)
    assert result.get("valid") is False
    assert "reason" in result
