"""File validation utilities."""

from pathlib import Path

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..config import get_config
from ..exceptions import DocumentReadError

logger = get_logger(__name__)


def validate_file_path(file_path: Path, must_exist: bool = True) -> None:
    """
    Validate file path.
    
    Args:
        file_path: Path to validate
        must_exist: Whether file must exist
    
    Raises:
        DocumentReadError: If validation fails
    """
    if must_exist and not file_path.exists():
        raise DocumentReadError(f"File does not exist: {file_path}", file_path=str(file_path))
    
    if file_path.exists() and not file_path.is_file():
        raise DocumentReadError(f"Path is not a file: {file_path}", file_path=str(file_path))


def check_file_size(file_path: Path) -> bool:
    """
    Check if file size is within limits.
    
    Args:
        file_path: Path to file
    
    Returns:
        True if file size is acceptable
    """
    if not file_path.exists():
        return False
    
    file_size = file_path.stat().st_size
    max_size = get_config().max_file_size
    
    if file_size > max_size:
        logger.warning(f"File {file_path} exceeds size limit: {file_size} > {max_size}")
        return False
    
    return True



