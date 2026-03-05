"""Base class for Google Workspace SDK clients."""

from __future__ import annotations

from typing import TYPE_CHECKING

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from codomyrmex.cloud.google_workspace.auth import GoogleCredentials

logger = get_logger(__name__)


class GoogleWorkspaceBase:
    """Base class for all Google Workspace SDK clients.

    Subclasses set _api_name and _api_version class attributes to specify
    which Google API to use. The service client is built lazily on first use.
    """

    _api_name: str = ""
    _api_version: str = "v3"

    def __init__(self, credentials: GoogleCredentials) -> None:  # type: ignore[name-defined]
        self._credentials = credentials
        self._service = None

    @classmethod
    def from_env(cls) -> GoogleWorkspaceBase:
        """Create client from environment variables.

        Reads GWS_SERVICE_ACCOUNT_FILE or GOOGLE_APPLICATION_CREDENTIALS.

        Returns:
            Instance of the calling class.

        Raises:
            GoogleWorkspaceAuthError: If no credentials are configured.
        """
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials

        creds = GoogleCredentials.from_env()
        return cls(creds)

    def _get_service(self):
        """Lazily build and cache the API service client."""
        if self._service is None:
            self._service = self._credentials.build_service(
                self._api_name, self._api_version
            )
        return self._service

    def _safe_call(self, operation_fn, verb: str, resource: str, *, default=None):
        """Execute an API call with standardized error logging.

        Args:
            operation_fn: Zero-argument callable wrapping the API call.
            verb: Action name for the error message (e.g., 'list', 'create').
            resource: Resource name for the error message (e.g., 'files').
            default: Value to return when the call fails.

        Returns:
            The return value of operation_fn, or default on any exception.
        """
        try:
            return operation_fn()
        except Exception as exc:
            logger.error("Failed to %s %s: %s", verb, resource, exc)
            return default

    def __enter__(self) -> GoogleWorkspaceBase:
        return self

    def __exit__(self, *args) -> bool:
        return False
