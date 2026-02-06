"""MIME type and format detection utilities."""

import mimetypes
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def detect_format_from_path(file_path: Path) -> str:
    """
    Detect document format from file extension.

    Args:
        file_path: Path to file

    Returns:
        Format string (e.g., "markdown", "json", "pdf")
    """
    suffix = file_path.suffix.lower().lstrip('.')

    format_mapping = {
        "md": "markdown",
        "markdown": "markdown",
        "json": "json",
        "yaml": "yaml",
        "yml": "yaml",
        "pdf": "pdf",
        "txt": "text",
        "text": "text",
        "html": "html",
        "htm": "html",
        "xml": "xml",
        "csv": "csv",
        "rtf": "rtf",
        "docx": "docx",
        "xlsx": "xlsx",
    }

    return format_mapping.get(suffix, "text")


def detect_mime_type(file_path: Path) -> str | None:
    """
    Detect MIME type of a file.

    Args:
        file_path: Path to file

    Returns:
        MIME type string or None if detection fails
    """
    try:
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type
    except Exception:
        return None
