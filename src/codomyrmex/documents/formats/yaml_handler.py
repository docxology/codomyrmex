"""YAML document handler."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..config import get_config
from ..exceptions import DocumentReadError, DocumentWriteError

logger = get_logger(__name__)


def read_yaml(
    file_path: str | Path,
    encoding: str | None = None,
) -> dict[str, Any]:
    """
    Read YAML content from a file.

    Args:
        file_path: Path to YAML file
        encoding: Optional encoding (defaults to utf-8)

    Returns:
        Parsed YAML data as dictionary

    Raises:
        DocumentReadError: If reading fails
    """
    file_path = Path(file_path)
    encoding = encoding or get_config().default_encoding

    try:
        import yaml

        with open(file_path, encoding=encoding) as f:
            data = yaml.safe_load(f)

        if data is None:
            data = {}

        return data

    except ImportError:
        logger.error("PyYAML not installed. Install with: uv pip install pyyaml")
        raise DocumentReadError(
            "PyYAML library not available",
            file_path=str(file_path)
        )
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in file {file_path}: {e}")
        raise DocumentReadError(
            f"Invalid YAML: {str(e)}",
            file_path=str(file_path)
        ) from e
    except Exception as e:
        logger.error(f"Error reading YAML file {file_path}: {e}")
        raise DocumentReadError(
            f"Failed to read YAML file: {str(e)}",
            file_path=str(file_path)
        ) from e


def write_yaml(
    data: dict[str, Any],
    file_path: str | Path,
    encoding: str | None = None,
    default_flow_style: bool = False,
) -> None:
    """
    Write YAML data to a file.

    Args:
        data: Data dictionary to write
        file_path: Path where file should be written
        encoding: Optional encoding (defaults to utf-8)
        default_flow_style: Whether to use flow style (compact) formatting

    Raises:
        DocumentWriteError: If writing fails
    """
    file_path = Path(file_path)
    encoding = encoding or get_config().default_encoding

    try:
        import yaml

        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding=encoding) as f:
            yaml.dump(data, f, default_flow_style=default_flow_style, allow_unicode=True)
        logger.debug(f"Wrote YAML to {file_path}")

    except ImportError:
        logger.error("PyYAML not installed. Install with: uv pip install pyyaml")
        raise DocumentWriteError(
            "PyYAML library not available",
            file_path=str(file_path)
        )
    except Exception as e:
        logger.error(f"Error writing YAML file {file_path}: {e}")
        raise DocumentWriteError(
            f"Failed to write YAML file: {str(e)}",
            file_path=str(file_path)
        ) from e



