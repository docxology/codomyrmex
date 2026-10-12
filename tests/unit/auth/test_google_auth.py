"""Real Google OAuth object/path tests with exclusively temporary credential files.

Interactive and refresh flows are never initiated by these local tests. No mocks
or operator token caches are used.
"""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from codomyrmex.auth.google.authenticator import (
    AUTH_AVAILABLE,
    DEFAULT_SCOPES,
    GoogleAuthenticator,
)


@pytest.mark.skipif(not AUTH_AVAILABLE, reason="Google Auth dependencies not installed")
class TestGoogleAuthenticator:
    """Local path creation, negative flow checks, and actual cached token parsing."""

    def test_initialization(self, tmp_path: Path):
        client_secrets = tmp_path / "client.json"
        client_secrets.write_text("{}", encoding="utf-8")
        token_cache = tmp_path / "tokens" / "token.json"
        auth = GoogleAuthenticator(
            client_secrets_file=str(client_secrets),
            token_cache_file=str(token_cache),
            scopes=["https://www.googleapis.com/auth/calendar"],
        )
        assert auth.client_secrets_file == str(client_secrets)
        assert auth.token_file == str(token_cache)
        assert auth.scopes == ["https://www.googleapis.com/auth/calendar"]
        assert token_cache.parent.is_dir()
        assert not token_cache.exists()

    def test_default_scopes_with_explicit_token_path(self, tmp_path: Path):
        """Defaults can be checked without constructing an operator cache path."""
        auth = GoogleAuthenticator(
            client_secrets_file=str(tmp_path / "client.json"),
            token_cache_file=str(tmp_path / "tokens" / "token.json"),
        )
        assert auth.scopes == DEFAULT_SCOPES
        assert Path(auth.token_file).parent.is_dir()

    def test_get_credentials_no_secrets_raises_error(self, tmp_path: Path):
        token = tmp_path / "token.json"
        auth = GoogleAuthenticator(
            client_secrets_file=str(tmp_path / "missing-client.json"),
            token_cache_file=str(token),
        )
        with pytest.raises(FileNotFoundError, match="Client secrets file not found"):
            auth.get_credentials()
        assert not token.exists()

    def test_run_interactive_flow_no_secrets_raises_error(self, tmp_path: Path):
        auth = GoogleAuthenticator(
            client_secrets_file=str(tmp_path / "missing-client.json"),
            token_cache_file=str(tmp_path / "tokens" / "token.json"),
        )
        with pytest.raises(FileNotFoundError, match="Client secrets file not found"):
            auth._run_interactive_flow()

    def test_valid_local_cache_returns_without_refresh_or_interactive_flow(
        self, tmp_path: Path
    ):
        """Actual SDK credential parsing returns a valid synthetic cached token."""
        token = tmp_path / "token.json"
        expiry = (datetime.now(UTC) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        token.write_text(
            json.dumps(
                {
                    "token": "unit-only-access-token",
                    "refresh_token": "unit-only-refresh-token",
                    "client_id": "unit-only-client-id",
                    "client_secret": "unit-only-client-secret",  # pragma: allowlist secret
                    "expiry": expiry,
                }
            ),
            encoding="utf-8",
        )
        before = token.read_bytes()
        auth = GoogleAuthenticator(
            client_secrets_file=str(tmp_path / "missing-client.json"),
            token_cache_file=str(token),
        )
        credentials = auth.get_credentials()
        assert credentials.valid
        assert credentials.token == "unit-only-access-token"
        assert token.read_bytes() == before
