"""Tests for the auth module."""


import pytest

from codomyrmex.auth.google import AUTH_AVAILABLE, GoogleAuthenticator

# Require auth module dependencies
pytestmark = pytest.mark.skipif(
    not AUTH_AVAILABLE,
    reason="Google Auth dependencies not installed. Run `uv sync --extra calendar --extra email`"
)

def test_google_authenticator_init():
    """Test that GoogleAuthenticator initializes correctly with custom paths."""
    auth = GoogleAuthenticator(
        client_secrets_file="/tmp/dummy_client_secrets.json",
        token_cache_file="/tmp/dummy_token.json",
        scopes=["https://www.googleapis.com/auth/calendar.readonly"]
    )

    assert auth.client_secrets_file == "/tmp/dummy_client_secrets.json"
    assert auth.token_file == "/tmp/dummy_token.json"
    assert len(auth.scopes) == 1
    assert "calendar.readonly" in auth.scopes[0]

def test_google_authenticator_missing_secrets():
    """Test that GoogleAuthenticator fails fast if secrets file is missing and it has to run flow."""
    auth = GoogleAuthenticator(
        client_secrets_file="/tmp/this_file_does_not_exist.json",
        token_cache_file="/tmp/no_token_here.json",
    )

    # We expect a FileNotFoundError because the interactive flow falls back to reading the client_secrets
    with pytest.raises(FileNotFoundError):
        # Prevent actual browser pop-ups just in case something acts unexpected during Zero-Mock tests
        auth.get_credentials()
