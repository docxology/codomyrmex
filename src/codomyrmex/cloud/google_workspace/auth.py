"""Authentication helpers for the Google Workspace SDK module."""

from __future__ import annotations

import os

from codomyrmex.cloud.google_workspace.exceptions import GoogleWorkspaceAuthError

_DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/chat.messages",
]


class GoogleCredentials:
    """Manages Google service account credentials for Workspace API access."""

    def __init__(
        self,
        credentials_file: str | None = None,
        scopes: list[str] | None = None,
    ) -> None:
        self._credentials_file = credentials_file
        self._scopes = scopes or _DEFAULT_SCOPES
        self._creds = None

    @classmethod
    def from_env(cls, scopes: list[str] | None = None) -> GoogleCredentials:
        """Create credentials from environment variables.

        Checks GWS_SERVICE_ACCOUNT_FILE first, then GOOGLE_APPLICATION_CREDENTIALS.

        Args:
            scopes: OAuth2 scopes to request (defaults to _DEFAULT_SCOPES).

        Raises:
            GoogleWorkspaceAuthError: If neither env var is set.
        """
        creds_file = os.getenv("GWS_SERVICE_ACCOUNT_FILE") or os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )
        if not creds_file:
            raise GoogleWorkspaceAuthError(
                "No Google credentials configured. set GWS_SERVICE_ACCOUNT_FILE "
                "or GOOGLE_APPLICATION_CREDENTIALS environment variable."
            )
        return cls(credentials_file=creds_file, scopes=scopes)

    @classmethod
    def from_service_account_file(
        cls,
        file_path: str,
        scopes: list[str] | None = None,
    ) -> GoogleCredentials:
        """Create credentials from an explicit service account file path.

        Args:
            file_path: Path to the service account JSON key file.
            scopes: OAuth2 scopes to request.
        """
        return cls(credentials_file=file_path, scopes=scopes)

    def get_credentials(self):
        """Return google.oauth2 credentials object (lazy-loaded).

        Returns:
            google.oauth2.service_account.Credentials instance.

        Raises:
            ImportError: If google-auth is not installed.
        """
        if self._creds is None:
            try:
                from google.oauth2 import service_account
            except ImportError as exc:
                raise ImportError(
                    "google-auth is required: uv sync --extra google_workspace"
                ) from exc
            self._creds = service_account.Credentials.from_service_account_file(
                self._credentials_file,
                scopes=self._scopes,
            )
        return self._creds

    def build_service(self, service_name: str, version: str):
        """Build a Google API service client.

        Args:
            service_name: API name (e.g., 'drive', 'gmail').
            version: API version (e.g., 'v3', 'v1').

        Returns:
            googleapiclient.discovery.Resource instance.
        """
        try:
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise ImportError(
                "google-api-python-client is required: uv sync --extra google_workspace"
            ) from exc
        return build(service_name, version, credentials=self.get_credentials())
