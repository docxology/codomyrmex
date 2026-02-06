"""HTML document handler."""

from __future__ import annotations

import re
from pathlib import Path

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..config import get_config
from ..exceptions import DocumentReadError, DocumentWriteError

logger = get_logger(__name__)


def read_html(file_path: str | Path, encoding: str | None = None) -> str:
    """
    Read HTML content from a file.

    Args:
        file_path: Path to HTML file
        encoding: Optional encoding (defaults to utf-8)

    Returns:
        HTML content as string

    Raises:
        DocumentReadError: If reading fails
    """
    file_path = Path(file_path)
    encoding = encoding or get_config().default_encoding

    try:
        with open(file_path, encoding=encoding) as f:
            content = f.read()
        return content
    except Exception as e:
        logger.error(f"Error reading HTML file {file_path}: {e}")
        raise DocumentReadError(
            f"Failed to read HTML file: {str(e)}",
            file_path=str(file_path)
        ) from e


def write_html(content: str, file_path: str | Path, encoding: str | None = None) -> None:
    """
    Write HTML content to a file.

    Args:
        content: HTML content to write
        file_path: Path where file should be written
        encoding: Optional encoding (defaults to utf-8)

    Raises:
        DocumentWriteError: If writing fails
    """
    file_path = Path(file_path)
    encoding = encoding or get_config().default_encoding

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        logger.debug(f"Wrote HTML to {file_path}")
    except Exception as e:
        logger.error(f"Error writing HTML file {file_path}: {e}")
        raise DocumentWriteError(
            f"Failed to write HTML file: {str(e)}",
            file_path=str(file_path)
        ) from e


def strip_html_tags(html_content: str) -> str:
    """
    Strip HTML tags and return plain text.

    Args:
        html_content: HTML content string

    Returns:
        Plain text with HTML tags removed
    """
    clean = re.sub(r'<[^>]+>', '', html_content)
    # Collapse whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean
