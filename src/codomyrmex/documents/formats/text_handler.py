"""Plain text document handler."""

from __future__ import annotations

from pathlib import Path

from codomyrmex.documents.config import get_config
from codomyrmex.documents.exceptions import DocumentReadError, DocumentWriteError
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


def read_text(file_path: str | Path, encoding: str | None = None) -> str:
    """
    Read plain text content from a file.

    Args:
        file_path: Path to text file
        encoding: Optional encoding (auto-detected if not provided)

    Returns:
        Text content as string

    Raises:
        DocumentReadError: If reading fails
    """
    file_path = Path(file_path)

    # Try to detect encoding if not provided
    if encoding is None:
        from codomyrmex.documents.utils.encoding_detector import detect_encoding
        encoding = detect_encoding(file_path) or get_config().default_encoding

    try:
        with open(file_path, encoding=encoding) as f:
            content = f.read()
        return content
    except UnicodeDecodeError as e:
        logger.warning(f"Encoding error reading {file_path}, trying different encodings")
        # Try common encodings
        for enc in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                with open(file_path, encoding=enc) as f:
                    content = f.read()
                logger.info(f"Successfully read {file_path} with encoding {enc}")
                return content
            except UnicodeDecodeError:
                continue
        raise DocumentReadError(
            f"Could not decode file with any encoding: {str(e)}",
            file_path=str(file_path)
        ) from e
    except Exception as e:
        logger.error(f"Error reading text file {file_path}: {e}")
        raise DocumentReadError(
            f"Failed to read text file: {str(e)}",
            file_path=str(file_path)
        ) from e


def write_text(content: str, file_path: str | Path, encoding: str | None = None) -> None:
    """
    Write text content to a file.

    Args:
        content: Text content to write
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
        logger.debug(f"Wrote text to {file_path}")
    except Exception as e:
        logger.error(f"Error writing text file {file_path}: {e}")
        raise DocumentWriteError(
            f"Failed to write text file: {str(e)}",
            file_path=str(file_path)
        ) from e



