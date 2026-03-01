"""Google Authenticator for Codomyrmex.

Handles OAuth2 device flow and local server flow to acquire and cache tokens.
Requires `google-auth-oauthlib`, `google-auth-httplib2`, and `google-api-python-client`.
"""

import logging
import os

logger = logging.getLogger(__name__)

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    Request = None
    Credentials = None
    InstalledAppFlow = None

# Default scopes required for full bidirectional Email and Calendar functionality.
DEFAULT_SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GoogleAuthenticator:
    """Handles Google OAuth2 authentication and token management."""

    def __init__(self, client_secrets_file: str, token_cache_file: str | None = None, scopes: list | None = None):
        """
        Initialize the authenticator.

        Args:
            client_secrets_file: Path to the downloaded client_secret_<client_id>.json from Google Cloud Console.
            token_cache_file: Path to cache the acquired refresh/access tokens. Defaults to `~/.codomyrmex/auth/google/token.json`.
            scopes: List of OAuth2 scopes. Defaults to Calendar and Gmail modify scopes.
        """
        if not AUTH_AVAILABLE:
            raise ImportError(
                "Google Auth dependencies are not installed. "
                "Please run: uv sync --extra calendar --extra email"
            )

        self.client_secrets_file = client_secrets_file
        self.scopes = scopes or DEFAULT_SCOPES

        if token_cache_file:
            self.token_file = os.path.expanduser(token_cache_file)
        else:
            self.token_file = os.path.expanduser("~/.codomyrmex/auth/google/token.json")

        os.makedirs(os.path.dirname(self.token_file), exist_ok=True)

    def get_credentials(self) -> "Credentials": # type: ignore
        """
        Acquire valid credentials. Retrieves from cache if found and valid.
        Refreshes if expired. Otherwise, initiates an interactive browser flow.

        Returns:
            google.oauth2.credentials.Credentials: The valid credentials object.
        """
        creds = None

        # Load existing token if available
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            except Exception as e:
                # If the cache file is malformed, simply ignore it and re-auth
                logger.warning("Malformed token cache file %s, will re-auth: %s", self.token_file, e)
                pass

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning("OAuth token refresh failed: %s — running interactive flow", e)
                    creds = self._run_interactive_flow()
            else:
                creds = self._run_interactive_flow()

            # Save the credentials for the next run (owner-readable only)
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
            os.chmod(self.token_file, 0o600)

        return creds

    def _run_interactive_flow(self) -> "Credentials": # type: ignore
        """Run the local server flow to get user authorization."""
        if not os.path.exists(self.client_secrets_file):
            raise FileNotFoundError(f"Client secrets file not found at {self.client_secrets_file}")

        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, self.scopes
        )
        return flow.run_local_server(port=0)
