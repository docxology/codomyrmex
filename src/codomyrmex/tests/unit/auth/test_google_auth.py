"""Zero-mock tests for GoogleAuthenticator.

Covers basic initialization and path handling. Skips interactive
flow tests since they require user input and external dependencies.

Zero-mock policy: no unittest.mock, no MagicMock, no monkeypatch.
"""

import os
import tempfile

import pytest

from codomyrmex.auth.google.authenticator import AUTH_AVAILABLE, GoogleAuthenticator


@pytest.mark.skipif(not AUTH_AVAILABLE, reason="Google Auth dependencies not installed")
class TestGoogleAuthenticator:
    """Tests for GoogleAuthenticator class."""

    def test_initialization(self):
        """Test initialization with custom paths."""
        with tempfile.NamedTemporaryFile() as tmp:
            client_secrets = tmp.name
            token_cache = tempfile.NamedTemporaryFile().name

            auth = GoogleAuthenticator(
                client_secrets_file=client_secrets,
                token_cache_file=token_cache,
                scopes=["https://www.googleapis.com/auth/calendar"]
            )

            assert auth.client_secrets_file == client_secrets
            assert auth.token_file == token_cache
            assert auth.scopes == ["https://www.googleapis.com/auth/calendar"]
            assert os.path.exists(os.path.dirname(token_cache))

    def test_default_token_path(self):
        """Test default token path expansion."""
        with tempfile.NamedTemporaryFile() as tmp:
            auth = GoogleAuthenticator(client_secrets_file=tmp.name)
            expected = os.path.expanduser("~/.codomyrmex/auth/google/token.json")
            assert auth.token_file == expected

    def test_get_credentials_no_secrets_raises_error(self):
        """get_credentials raises FileNotFoundError if secrets file is missing."""
        auth = GoogleAuthenticator(client_secrets_file="nonexistent.json")
        with pytest.raises(FileNotFoundError, match="Client secrets file not found"):
            auth.get_credentials()

    def test_run_interactive_flow_no_secrets_raises_error(self):
        """_run_interactive_flow raises FileNotFoundError if secrets file is missing."""
        auth = GoogleAuthenticator(client_secrets_file="nonexistent.json")
        with pytest.raises(FileNotFoundError, match="Client secrets file not found"):
            auth._run_interactive_flow()
