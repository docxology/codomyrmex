"""JSON document handler."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..config import get_config
from ..exceptions import DocumentReadError, DocumentValidationError, DocumentWriteError

logger = get_logger(__name__)


def read_json(
    file_path: str | Path,
    encoding: str | None = None,
    schema: dict | None = None,
) -> dict[str, Any]:
    """
    Read JSON content from a file.

    Args:
        file_path: Path to JSON file
        encoding: Optional encoding (defaults to utf-8)
        schema: Optional JSON schema for validation

    Returns:
        Parsed JSON data as dictionary

    Raises:
        DocumentReadError: If reading fails
        DocumentValidationError: If schema validation fails
    """
    file_path = Path(file_path)
    encoding = encoding or get_config().default_encoding

    try:
        with open(file_path, encoding=encoding) as f:
            data = json.load(f)

        # Validate against schema if provided
        if schema:
            try:
                import jsonschema
                jsonschema.validate(instance=data, schema=schema)
            except jsonschema.ValidationError as e:
                raise DocumentValidationError(
                    f"JSON schema validation failed: {str(e)}",
                    validation_errors=[str(e)]
                ) from e
            except ImportError:
                logger.warning("jsonschema not available, skipping validation")

        return data

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        raise DocumentReadError(
            f"Invalid JSON: {str(e)}",
            file_path=str(file_path)
        ) from e
    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {e}")
        raise DocumentReadError(
            f"Failed to read JSON file: {str(e)}",
            file_path=str(file_path)
        ) from e


def write_json(
    data: dict[str, Any],
    file_path: str | Path,
    encoding: str | None = None,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    """
    Write JSON data to a file.

    Args:
        data: Data dictionary to write
        file_path: Path where file should be written
        encoding: Optional encoding (defaults to utf-8)
        indent: Indentation level for pretty printing
        ensure_ascii: Whether to escape non-ASCII characters

    Raises:
        DocumentWriteError: If writing fails
    """
    file_path = Path(file_path)
    encoding = encoding or get_config().default_encoding

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
        logger.debug(f"Wrote JSON to {file_path}")
    except Exception as e:
        logger.error(f"Error writing JSON file {file_path}: {e}")
        raise DocumentWriteError(
            f"Failed to write JSON file: {str(e)}",
            file_path=str(file_path)
        ) from e



