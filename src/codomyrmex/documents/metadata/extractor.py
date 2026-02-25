"""Metadata extraction from documents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from ..exceptions import MetadataError

logger = get_logger(__name__)


def extract_metadata(file_path: str | Path) -> dict[str, Any]:
    """
    Extract metadata from a document file.

    Args:
        file_path: Path to document file

    Returns:
        Dictionary of metadata

    Raises:
        MetadataError: If extraction fails
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise MetadataError(f"File not found: {file_path}")

    try:
        metadata = {}

        # File system metadata
        stat = file_path.stat()
        metadata["file_size"] = stat.st_size
        metadata["created_at"] = stat.st_ctime
        metadata["modified_at"] = stat.st_mtime

        # Format-specific metadata
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            metadata.update(_extract_pdf_metadata(file_path))
        elif suffix in [".md", ".markdown"]:
            metadata.update(_extract_markdown_metadata(file_path))
        elif suffix == ".json":
            metadata.update(_extract_json_metadata(file_path))
        elif suffix in [".yaml", ".yml"]:
            metadata.update(_extract_yaml_metadata(file_path))

        return metadata

    except Exception as e:
        logger.error(f"Error extracting metadata from {file_path}: {e}")
        raise MetadataError(f"Failed to extract metadata: {str(e)}") from e


def _extract_pdf_metadata(file_path: Path) -> dict[str, Any]:
    """Extract PDF-specific metadata."""
    try:
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            pdf_metadata = reader.metadata or {}
        except ImportError:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                pdf_metadata = reader.metadata or {}

        return {
            "title": pdf_metadata.get("/Title", ""),
            "author": pdf_metadata.get("/Author", ""),
            "subject": pdf_metadata.get("/Subject", ""),
            "creator": pdf_metadata.get("/Creator", ""),
            "producer": pdf_metadata.get("/Producer", ""),
        }
    except Exception:
        return {}


def _extract_markdown_metadata(file_path: Path) -> dict[str, Any]:
    """Extract markdown frontmatter metadata."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        # Check for YAML frontmatter
        if content.startswith('---'):
            import yaml
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                if frontmatter:
                    return frontmatter

        return {}
    except Exception:
        return {}


def _extract_json_metadata(file_path: Path) -> dict[str, Any]:
    """Extract metadata from JSON files."""
    try:
        import json
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                # Return standard metadata fields if present at top level
                return {
                    k: v for k, v in data.items()
                    if k in ["title", "author", "description", "version", "metadata", "created_at", "updated_at"]
                }
        return {}
    except Exception:
        return {}


def _extract_yaml_metadata(file_path: Path) -> dict[str, Any]:
    """Extract metadata from YAML files."""
    try:
        import yaml
        with open(file_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                # Return standard metadata fields
                return {
                    k: v for k, v in data.items()
                    if k in ["title", "author", "description", "version", "metadata", "created_at", "updated_at"]
                }
        return {}
    except Exception:
        return {}



