"""Google Drive SDK client."""

from __future__ import annotations

from typing import Any

from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GoogleDriveClient(GoogleWorkspaceBase):
    """Client for Google Drive API v3."""

    _api_name = "drive"
    _api_version = "v3"

    def list_files(
        self,
        query: str = "",
        page_size: int = 20,
        fields: str = "files(id,name,mimeType,modifiedTime,size)",
    ) -> list[dict[str, Any]]:
        """List files in Drive matching an optional query.

        Args:
            query: Drive search query string (e.g., "name contains 'report'").
            page_size: Maximum number of files to return.
            fields: Fields to include in the response.

        Returns:
            List of file metadata dicts.
        """
        params: dict[str, Any] = {"pageSize": page_size, "fields": fields}
        if query:
            params["q"] = query

        def _call():
            return self._get_service().files().list(**params).execute()

        result = self._safe_call(_call, "list", "files", default={})
        return result.get("files", []) if isinstance(result, dict) else []

    def get_file(self, file_id: str) -> dict[str, Any]:
        """Get metadata for a specific file.

        Args:
            file_id: The Drive file ID.

        Returns:
            File metadata dict, or empty dict on error.
        """

        def _call():
            return self._get_service().files().get(fileId=file_id).execute()

        return self._safe_call(_call, "get", f"file/{file_id}", default={}) or {}

    def upload_file(
        self,
        local_path: str,
        name: str,
        mime_type: str = "application/octet-stream",
        parent_id: str = "",
    ) -> dict[str, Any]:
        """Upload a local file to Google Drive.

        Args:
            local_path: Path to the local file.
            name: Name for the file in Drive.
            mime_type: MIME type of the file.
            parent_id: Optional parent folder ID.

        Returns:
            Uploaded file metadata dict, or empty dict on error.
        """
        try:
            from googleapiclient.http import MediaFileUpload
        except ImportError as exc:
            raise ImportError(
                "google-api-python-client is required: uv sync --extra google_workspace"
            ) from exc

        file_metadata: dict[str, Any] = {"name": name}
        if parent_id:
            file_metadata["parents"] = [parent_id]
        media = MediaFileUpload(local_path, mimetype=mime_type)

        def _call():
            return (
                self._get_service()
                .files()
                .create(body=file_metadata, media_body=media, fields="id,name")
                .execute()
            )

        return self._safe_call(_call, "upload", "file", default={}) or {}

    def share_file(
        self, file_id: str, email: str, role: str = "reader"
    ) -> dict[str, Any]:
        """Share a file with a specific user.

        Args:
            file_id: The Drive file ID.
            email: Email address of the user to share with.
            role: Permission role ('reader', 'writer', 'commenter', 'owner').

        Returns:
            Permission metadata dict, or empty dict on error.
        """
        permission = {"type": "user", "role": role, "emailAddress": email}

        def _call():
            return (
                self._get_service()
                .permissions()
                .create(fileId=file_id, body=permission)
                .execute()
            )

        return self._safe_call(_call, "share", f"file/{file_id}", default={}) or {}

    def delete_file(self, file_id: str) -> bool:
        """Delete a file from Drive.

        Args:
            file_id: The Drive file ID.

        Returns:
            True on success, False on error.
        """

        def _call():
            self._get_service().files().delete(fileId=file_id).execute()
            return True

        result = self._safe_call(_call, "delete", f"file/{file_id}", default=False)
        return bool(result)
