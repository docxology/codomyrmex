"""Document versioning operations."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..exceptions import MetadataError

logger = get_logger(__name__)


def get_document_version(file_path: str | Path) -> Optional[str]:
    """
    Get version information from a document.
    
    Args:
        file_path: Path to document file
    
    Returns:
        Version string or None if not found
    """
    file_path = Path(file_path)
    
    try:
        from .extractor import extract_metadata
        metadata = extract_metadata(file_path)
        return metadata.get("version")
    except Exception:
        return None


def set_document_version(file_path: str | Path, version: str) -> None:
    """
    Set version information for a document.
    
    Args:
        file_path: Path to document file
        version: Version string to set
    """
    file_path = Path(file_path)
    
    try:
        from .manager import update_metadata
        update_metadata(file_path, {"version": version})
    except Exception as e:
        logger.error(f"Error setting document version: {e}")
        raise MetadataError(f"Failed to set version: {str(e)}") from e



