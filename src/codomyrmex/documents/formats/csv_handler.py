"""CSV document handler."""

from __future__ import annotations

import csv
from pathlib import Path

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from ..config import get_config
from ..exceptions import DocumentReadError, DocumentWriteError

logger = get_logger(__name__)


def read_csv(file_path: str | Path, encoding: str | None = None) -> list[dict]:
    """
    Read CSV content from a file.

    Args:
        file_path: Path to CSV file
        encoding: Optional encoding (defaults to utf-8)

    Returns:
        List of dictionaries, one per row, keyed by header names

    Raises:
        DocumentReadError: If reading fails
    """
    file_path = Path(file_path)
    encoding = encoding or get_config().default_encoding

    try:
        with open(file_path, encoding=encoding, newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        return rows
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {e}")
        raise DocumentReadError(
            f"Failed to read CSV file: {str(e)}",
            file_path=str(file_path)
        ) from e


def write_csv(
    data: list[dict],
    file_path: str | Path,
    encoding: str | None = None,
    fieldnames: list[str] | None = None,
) -> None:
    """
    Write CSV data to a file.

    Args:
        data: List of dictionaries to write as CSV rows
        file_path: Path where file should be written
        encoding: Optional encoding (defaults to utf-8)
        fieldnames: Optional list of field names for header. Auto-detected from first row if None.

    Raises:
        DocumentWriteError: If writing fails
    """
    file_path = Path(file_path)
    encoding = encoding or get_config().default_encoding

    if not data:
        # Write empty file
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("", encoding=encoding)
            return
        except Exception as e:
            raise DocumentWriteError(
                f"Failed to write CSV file: {str(e)}",
                file_path=str(file_path)
            ) from e

    if fieldnames is None:
        fieldnames = list(data[0].keys())

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding=encoding, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logger.debug(f"Wrote CSV to {file_path}")
    except Exception as e:
        logger.error(f"Error writing CSV file {file_path}: {e}")
        raise DocumentWriteError(
            f"Failed to write CSV file: {str(e)}",
            file_path=str(file_path)
        ) from e
