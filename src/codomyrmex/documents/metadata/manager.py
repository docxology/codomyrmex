"""Metadata management operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..exceptions import MetadataError

logger = get_logger(__name__)


def update_metadata(file_path: str | Path, metadata: dict[str, Any]) -> None:
    """
    Update metadata for a document file.

    Args:
        file_path: Path to document file
        metadata: Metadata dictionary to update

    Raises:
        MetadataError: If update fails
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise MetadataError(f"File not found: {file_path}")

    try:
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            _update_pdf_metadata(file_path, metadata)
        elif suffix in [".md", ".markdown"]:
            _update_markdown_metadata(file_path, metadata)
        else:
            logger.warning(f"Metadata update not supported for format: {suffix}")

    except Exception as e:
        logger.error(f"Error updating metadata for {file_path}: {e}")
        raise MetadataError(f"Failed to update metadata: {str(e)}") from e


def get_metadata(file_path: str | Path) -> dict[str, Any]:
    """
    Get metadata for a document file.

    Args:
        file_path: Path to document file

    Returns:
        Metadata dictionary
    """
    from .extractor import extract_metadata
    return extract_metadata(file_path)


def _update_pdf_metadata(file_path: Path, metadata: dict[str, Any]) -> None:
    """Update PDF metadata."""
    # PDF metadata updates require creating a new PDF
    # This is a placeholder - full implementation would need PDF manipulation
    logger.warning("PDF metadata update requires full PDF rewrite - not yet implemented")


def _update_markdown_metadata(file_path: Path, metadata: dict[str, Any]) -> None:
    """Update markdown frontmatter metadata."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        import yaml

        # Check for existing frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                existing_metadata = yaml.safe_load(parts[1]) or {}
                existing_metadata.update(metadata)
                frontmatter = yaml.dump(existing_metadata, default_flow_style=False)
                new_content = f"---\n{frontmatter}---{parts[2]}"
            else:
                frontmatter = yaml.dump(metadata, default_flow_style=False)
                new_content = f"---\n{frontmatter}---\n{content}"
        else:
            frontmatter = yaml.dump(metadata, default_flow_style=False)
            new_content = f"---\n{frontmatter}---\n{content}"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    except Exception as e:
        logger.error(f"Error updating markdown metadata: {e}")
        raise



