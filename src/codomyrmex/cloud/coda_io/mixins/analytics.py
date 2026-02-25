"""AnalyticsMixin functionality."""

from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

class AnalyticsMixin:
    """AnalyticsMixin class."""

    def list_doc_analytics(
        self,
        doc_ids: list[str] | None = None,
        workspace_id: str | None = None,
        query: str | None = None,
        is_published: bool | None = None,
        since_date: str | None = None,
        until_date: str | None = None,
        scale: str = "daily",
        limit: int = 1000,
        page_token: str | None = None,
        order_by: str | None = None,
        direction: str | None = None,
    ) -> dict[str, Any]:
        """
        Get doc analytics data.

        Args:
            doc_ids: Filter by doc IDs
            workspace_id: Filter by workspace
            query: Search query
            is_published: Filter by published status
            since_date: Start date (YYYY-MM-DD)
            until_date: End date (YYYY-MM-DD)
            scale: "daily" or "cumulative"
            limit: Maximum results (1-5000)
            page_token: Pagination token
            order_by: Sort field
            direction: "ascending" or "descending"

        Returns:
            Analytics data with items
        """
        params = {
            "workspaceId": workspace_id,
            "query": query,
            "isPublished": is_published,
            "sinceDate": since_date,
            "untilDate": until_date,
            "scale": scale,
            "limit": limit,
            "pageToken": page_token,
            "orderBy": order_by,
            "direction": direction,
        }
        if doc_ids:
            params["docIds"] = ",".join(doc_ids)

        return self._get("/analytics/docs", params=params)

    def get_doc_analytics_summary(
        self,
        is_published: bool | None = None,
        since_date: str | None = None,
        until_date: str | None = None,
        workspace_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get summarized doc analytics.

        Args:
            is_published: Filter by published status
            since_date: Start date (YYYY-MM-DD)
            until_date: End date (YYYY-MM-DD)
            workspace_id: Filter by workspace

        Returns:
            Summary with totalSessions
        """
        params = {
            "isPublished": is_published,
            "sinceDate": since_date,
            "untilDate": until_date,
            "workspaceId": workspace_id,
        }
        return self._get("/analytics/docs/summary", params=params)

    def list_page_analytics(
        self,
        doc_id: str,
        since_date: str | None = None,
        until_date: str | None = None,
        limit: int = 1000,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """
        Get page analytics for a doc (Enterprise workspaces only).

        Args:
            doc_id: The doc ID
            since_date: Start date (YYYY-MM-DD)
            until_date: End date (YYYY-MM-DD)
            limit: Maximum results (1-5000)
            page_token: Pagination token

        Returns:
            Page analytics data
        """
        params = {
            "sinceDate": since_date,
            "untilDate": until_date,
            "limit": limit,
            "pageToken": page_token,
        }
        path = f"/analytics/docs/{self._encode_id(doc_id)}/pages"
        return self._get(path, params=params)

