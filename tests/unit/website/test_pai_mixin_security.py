"""Security contract tests for the PAI WebSocket push listener."""

import inspect

import pytest

from codomyrmex.website.pai_mixin import PAIProviderMixin


def test_websocket_push_defaults_to_loopback():
    signature = inspect.signature(PAIProviderMixin.start_websocket_push)
    assert signature.parameters["host"].default == "127.0.0.1"
    assert signature.parameters["auth_token"].default is None


def test_remote_websocket_bind_requires_auth_and_origin_allowlist():
    with pytest.raises(ValueError, match="auth_token and allowed_origins"):
        PAIProviderMixin._validate_websocket_bind("0.0.0.0", None, None)

    with pytest.raises(ValueError, match="auth_token and allowed_origins"):
        PAIProviderMixin._validate_websocket_bind(
            "0.0.0.0", None, ["https://trusted.example"]
        )


def test_remote_websocket_bind_rejects_wildcard_origin():
    with pytest.raises(ValueError, match="explicit origins"):
        PAIProviderMixin._validate_websocket_bind("0.0.0.0", "secret", ["*"])


def test_remote_websocket_bind_accepts_explicit_security_options():
    host, origins = PAIProviderMixin._validate_websocket_bind(
        "0.0.0.0", "secret", ["https://trusted.example/"]
    )
    assert host == "0.0.0.0"
    assert origins == ["https://trusted.example"]
