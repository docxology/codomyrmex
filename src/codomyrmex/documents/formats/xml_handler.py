"""XML document handler."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..config import get_config
from ..exceptions import DocumentReadError, DocumentWriteError

logger = get_logger(__name__)


def read_xml(file_path: str | Path, encoding: Optional[str] = None) -> str:
    """
    Read XML content from a file.

    Args:
        file_path: Path to XML file
        encoding: Optional encoding (defaults to utf-8)

    Returns:
        XML content as string

    Raises:
        DocumentReadError: If reading fails
    """
    file_path = Path(file_path)
    encoding = encoding or get_config().default_encoding

    try:
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        # Validate it parses as XML
        ET.fromstring(content)
        return content
    except ET.ParseError as e:
        logger.error(f"Invalid XML in file {file_path}: {e}")
        raise DocumentReadError(
            f"Invalid XML: {str(e)}",
            file_path=str(file_path)
        ) from e
    except Exception as e:
        logger.error(f"Error reading XML file {file_path}: {e}")
        raise DocumentReadError(
            f"Failed to read XML file: {str(e)}",
            file_path=str(file_path)
        ) from e


def write_xml(content: str, file_path: str | Path, encoding: Optional[str] = None) -> None:
    """
    Write XML content to a file.

    Args:
        content: XML content string to write
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
        logger.debug(f"Wrote XML to {file_path}")
    except Exception as e:
        logger.error(f"Error writing XML file {file_path}: {e}")
        raise DocumentWriteError(
            f"Failed to write XML file: {str(e)}",
            file_path=str(file_path)
        ) from e
