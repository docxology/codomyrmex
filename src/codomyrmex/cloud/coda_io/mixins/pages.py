"""PagesMixin functionality."""

from typing import Any

from codomyrmex.cloud.coda_io.models import (
    Page,
    PageList,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

class PagesMixin:
    """PagesMixin class."""

    def list_pages(
        self,
        doc_id: str,
        limit: int = 25,
        page_token: str | None = None,
    ) -> PageList:
        """
        List pages in a doc.

        Args:
            doc_id: The doc ID
            limit: Maximum results
            page_token: Pagination token

        Returns:
            PageList with items and pagination info
        """
        params = {"limit": limit, "pageToken": page_token}
        data = self._get(f"/docs/{self._encode_id(doc_id)}/pages", params=params)
        return PageList.from_dict(data)

    def create_page(
        self,
        doc_id: str,
        name: str | None = None,
        subtitle: str | None = None,
        icon_name: str | None = None,
        image_url: str | None = None,
        parent_page_id: str | None = None,
        page_content: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a new page in a doc.

        Note: Requires Doc Maker role.

        Args:
            doc_id: The doc ID
            name: Page name
            subtitle: Page subtitle
            icon_name: Icon name
            image_url: Cover image URL
            parent_page_id: Parent page ID for subpages
            page_content: Initial page content

        Returns:
            Creation result with request_id and page id
        """
        body = {}
        if name:
            body["name"] = name
        if subtitle:
            body["subtitle"] = subtitle
        if icon_name:
            body["iconName"] = icon_name
        if image_url:
            body["imageUrl"] = image_url
        if parent_page_id:
            body["parentPageId"] = parent_page_id
        if page_content:
            body["pageContent"] = page_content

        return self._post(f"/docs/{self._encode_id(doc_id)}/pages", json_data=body)

    def get_page(self, doc_id: str, page_id_or_name: str) -> Page:
        """
        Get details about a page.

        Args:
            doc_id: The doc ID
            page_id_or_name: Page ID or name (names are discouraged)

        Returns:
            Page details
        """
        path = f"/docs/{self._encode_id(doc_id)}/pages/{self._encode_id(page_id_or_name)}"
        data = self._get(path)
        return Page.from_dict(data)

    def update_page(
        self,
        doc_id: str,
        page_id_or_name: str,
        name: str | None = None,
        subtitle: str | None = None,
        icon_name: str | None = None,
        image_url: str | None = None,
        is_hidden: bool | None = None,
        content_update: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Update a page.

        Args:
            doc_id: The doc ID
            page_id_or_name: Page ID or name
            name: New name
            subtitle: New subtitle
            icon_name: New icon
            image_url: New cover image URL
            is_hidden: Whether to hide the page
            content_update: Content to update

        Returns:
            Update result
        """
        body = {}
        if name is not None:
            body["name"] = name
        if subtitle is not None:
            body["subtitle"] = subtitle
        if icon_name is not None:
            body["iconName"] = icon_name
        if image_url is not None:
            body["imageUrl"] = image_url
        if is_hidden is not None:
            body["isHidden"] = is_hidden
        if content_update is not None:
            body["contentUpdate"] = content_update

        path = f"/docs/{self._encode_id(doc_id)}/pages/{self._encode_id(page_id_or_name)}"
        return self._put(path, json_data=body)

    def delete_page(self, doc_id: str, page_id_or_name: str) -> dict[str, Any]:
        """
        Delete a page.

        Args:
            doc_id: The doc ID
            page_id_or_name: Page ID or name

        Returns:
            Deletion result
        """
        path = f"/docs/{self._encode_id(doc_id)}/pages/{self._encode_id(page_id_or_name)}"
        return self._delete(path)

    def list_page_content(
        self,
        doc_id: str,
        page_id_or_name: str,
        limit: int = 50,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """
        List content elements in a page.

        Args:
            doc_id: The doc ID
            page_id_or_name: Page ID or name
            limit: Maximum results (1-500, default 50)
            page_token: Pagination token

        Returns:
            Page content with items
        """
        params = {"limit": limit, "pageToken": page_token}
        path = f"/docs/{self._encode_id(doc_id)}/pages/{self._encode_id(page_id_or_name)}/content"
        return self._get(path, params=params)

    def export_page(
        self,
        doc_id: str,
        page_id_or_name: str,
        output_format: str = "html",
    ) -> dict[str, Any]:
        """
        Begin exporting page content.

        Args:
            doc_id: The doc ID
            page_id_or_name: Page ID or name
            output_format: "html" or "markdown"

        Returns:
            Export status with request ID and href to poll
        """
        path = f"/docs/{self._encode_id(doc_id)}/pages/{self._encode_id(page_id_or_name)}/export"
        return self._post(path, json_data={"outputFormat": output_format})

    def get_page_export_status(
        self,
        doc_id: str,
        page_id_or_name: str,
        request_id: str,
    ) -> dict[str, Any]:
        """
        Check page export status.

        Args:
            doc_id: The doc ID
            page_id_or_name: Page ID or name
            request_id: Export request ID

        Returns:
            Export status with download link when complete
        """
        path = f"/docs/{self._encode_id(doc_id)}/pages/{self._encode_id(page_id_or_name)}/export/{request_id}"
        return self._get(path)

