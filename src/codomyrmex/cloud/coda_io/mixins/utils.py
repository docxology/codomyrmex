"""UtilsMixin functionality."""

from typing import Any

from codomyrmex.cloud.coda_io.models import (
    MutationStatus,
    User,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

class UtilsMixin:
    """UtilsMixin class."""

    def whoami(self) -> User:
        """
        Get info about the current user.

        Returns:
            User info
        """
        data = self._get("/whoami")
        return User.from_dict(data)

    def resolve_browser_link(
        self,
        url: str,
        degrade_gracefully: bool = False,
    ) -> dict[str, Any]:
        """
        Resolve a Coda browser URL to API metadata.

        Args:
            url: The browser URL to resolve
            degrade_gracefully: Return parent if resource deleted

        Returns:
            Resolved resource info with API href
        """
        params = {"url": url}
        if degrade_gracefully:
            params["degradeGracefully"] = True

        return self._get("/resolveBrowserLink", params=params)

    def get_mutation_status(self, request_id: str) -> MutationStatus:
        """
        Get status of an async mutation.

        Args:
            request_id: The mutation request ID

        Returns:
            MutationStatus with completed flag
        """
        path = f"/mutationStatus/{request_id}"
        data = self._get(path)
        return MutationStatus.from_dict(data)

