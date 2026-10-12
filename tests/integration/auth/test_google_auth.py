"""Tests for the auth module."""

import pytest

from codomyrmex.auth.google import AUTH_AVAILABLE, GoogleAuthenticator

pytestmark = pytest.mark.integration

# Require auth module dependencies
pytestmark = pytest.mark.skipif(
    not AUTH_AVAILABLE,
    reason="Google Auth dependencies not installed. Run `uv sync --extra calendar --extra email`",
)


def test_google_authenticator_init(tmp_path):
    """Test that GoogleAuthenticator initializes correctly with custom paths."""
    auth = GoogleAuthenticator(
        client_secrets_file=str(tmp_path / "dummy_client_secrets.json"),
        token_cache_file=str(tmp_path / "dummy_token.json"),
        scopes=["https://www.googleapis.com/auth/calendar.readonly"],
    )

    assert auth.client_secrets_file == str(tmp_path / "dummy_client_secrets.json")
    assert auth.token_file == str(tmp_path / "dummy_token.json")
    assert len(auth.scopes) == 1
    assert "calendar.readonly" in auth.scopes[0]


def test_google_authenticator_missing_secrets(tmp_path):
    """Test that GoogleAuthenticator fails fast if secrets file is missing and it has to run flow."""
    auth = GoogleAuthenticator(
        client_secrets_file=str(tmp_path / "this_file_does_not_exist.json"),
        token_cache_file=str(tmp_path / "no_token_here.json"),
    )

    # We expect a FileNotFoundError because the interactive flow falls back to reading the client_secrets
    with pytest.raises(FileNotFoundError):
        # Both selected credential files are absent from this isolated directory.
        auth.get_credentials()
