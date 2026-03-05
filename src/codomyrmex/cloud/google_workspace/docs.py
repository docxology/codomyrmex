"""Google Docs SDK client."""

from __future__ import annotations

from typing import Any

from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GoogleDocsClient(GoogleWorkspaceBase):
    """Client for Google Docs API v1."""

    _api_name = "docs"
    _api_version = "v1"

    def get_document(self, document_id: str) -> dict[str, Any]:
        """Fetch a Google Doc by its ID.

        Args:
            document_id: The document ID.

        Returns:
            Document dict with content, or empty dict on error.
        """
        def _call():
            return (
                self._get_service()
                .documents()
                .get(documentId=document_id)
                .execute()
            )

        return (
            self._safe_call(_call, "get", f"document/{document_id}", default={}) or {}
        )

    def append_text(self, document_id: str, text: str) -> dict[str, Any]:
        """Append text to the end of a Google Doc.

        Args:
            document_id: The document ID.
            text: Text to append.

        Returns:
            Batch update response dict, or empty dict on error.
        """
        requests = [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": text,
                }
            }
        ]

        def _call():
            return (
                self._get_service()
                .documents()
                .batchUpdate(
                    documentId=document_id,
                    body={"requests": requests},
                )
                .execute()
            )

        return self._safe_call(_call, "append", "text", default={}) or {}
