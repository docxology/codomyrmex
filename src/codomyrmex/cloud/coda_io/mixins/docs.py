"""DocsMixin functionality."""

from typing import Any

from codomyrmex.cloud.coda_io.models import (
    Doc,
    DocList,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

class DocsMixin:
    """DocsMixin class."""

    def list_docs(
        self,
        is_owner: bool | None = None,
        is_published: bool | None = None,
        query: str | None = None,
        source_doc: str | None = None,
        is_starred: bool | None = None,
        in_gallery: bool | None = None,
        workspace_id: str | None = None,
        folder_id: str | None = None,
        limit: int = 25,
        page_token: str | None = None,
    ) -> DocList:
        """
        List accessible docs.

        Returns docs in reverse chronological order by last relevant event.

        Args:
            is_owner: Show only docs owned by the user
            is_published: Show only published docs
            query: Search term to filter results
            source_doc: Show only docs copied from this doc ID
            is_starred: Filter by starred status
            in_gallery: Show only docs visible in gallery
            workspace_id: Filter by workspace
            folder_id: Filter by folder
            limit: Maximum results (default 25)
            page_token: Pagination token

        Returns:
            DocList with items and pagination info
        """
        params = {
            "isOwner": is_owner,
            "isPublished": is_published,
            "query": query,
            "sourceDoc": source_doc,
            "isStarred": is_starred,
            "inGallery": in_gallery,
            "workspaceId": workspace_id,
            "folderId": folder_id,
            "limit": limit,
            "pageToken": page_token,
        }
        data = self._get("/docs", params=params)
        return DocList.from_dict(data)

    def create_doc(
        self,
        title: str | None = None,
        source_doc: str | None = None,
        timezone: str | None = None,
        folder_id: str | None = None,
        initial_page: dict[str, Any] | None = None,
    ) -> Doc:
        """
        Create a new doc.

        Note: Creating a doc requires Doc Maker role in the workspace.

        Args:
            title: Title of the new doc (defaults to "Untitled")
            source_doc: Doc ID to copy from
            timezone: Timezone for the doc
            folder_id: Folder to create doc in
            initial_page: Initial page content

        Returns:
            The created Doc
        """
        body = {}
        if title:
            body["title"] = title
        if source_doc:
            body["sourceDoc"] = source_doc
        if timezone:
            body["timezone"] = timezone
        if folder_id:
            body["folderId"] = folder_id
        if initial_page:
            body["initialPage"] = initial_page

        data = self._post("/docs", json_data=body)
        return Doc.from_dict(data)

    def get_doc(self, doc_id: str) -> Doc:
        """
        Get metadata for a specific doc.

        Args:
            doc_id: The doc ID

        Returns:
            Doc metadata
        """
        data = self._get(f"/docs/{self._encode_id(doc_id)}")
        return Doc.from_dict(data)

    def delete_doc(self, doc_id: str) -> dict[str, Any]:
        """
        Delete a doc.

        Args:
            doc_id: The doc ID to delete

        Returns:
            Deletion result
        """
        return self._delete(f"/docs/{self._encode_id(doc_id)}")

    def update_doc(
        self,
        doc_id: str,
        title: str | None = None,
        icon_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Update doc metadata.

        Note: Updating title requires Doc Maker role.

        Args:
            doc_id: The doc ID
            title: New title
            icon_name: New icon name

        Returns:
            Update result
        """
        body = {}
        if title:
            body["title"] = title
        if icon_name:
            body["iconName"] = icon_name

        return self._patch(f"/docs/{self._encode_id(doc_id)}", json_data=body)

