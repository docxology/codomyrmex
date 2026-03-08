"""Mixin for Gemini file management operations."""

from typing import Any

from google.genai import types

from codomyrmex.agents.core.exceptions import GeminiError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GeminiFilesMixin:
    """File upload, listing, retrieval, and deletion.

    Requires ``client`` from the host class.
    """

    def upload_file(
        self, file_path: str, mime_type: str | None = None
    ) -> dict[str, Any]:
        """Upload a file for use in Gemini prompts."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            config = types.UploadFileConfig(mime_type=mime_type) if mime_type else None
            file_ref = self.client.files.upload(file=file_path, config=config)
            return file_ref.model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to upload file: %s", e)
            raise GeminiError(f"Failed to upload file: {e}") from e

    def list_files(self) -> list[dict[str, Any]]:
        """List all uploaded files."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return [f.model_dump() for f in self.client.files.list()]
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to list files: %s", e)
            raise GeminiError(f"Failed to list files: {e}") from e

    def get_file(self, file_name: str) -> dict[str, Any]:
        """Get metadata for an uploaded file."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return self.client.files.get(name=file_name).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to get file %s: %s", file_name, e)
            raise GeminiError(f"Failed to get file {file_name}: {e}") from e

    def delete_file(self, file_name: str) -> bool:
        """Delete an uploaded file."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            self.client.files.delete(name=file_name)
            return True
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to delete file %s: %s", file_name, e)
            raise GeminiError(f"Failed to delete file {file_name}: {e}") from e
