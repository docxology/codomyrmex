"""Encoding detection utilities."""

from pathlib import Path

from codomyrmex.documents.config import get_config
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


def detect_encoding(file_path: Path, sample_size: int = 8192) -> str | None:
    """
    Detect file encoding.

    Args:
        file_path: Path to file
        sample_size: Number of bytes to sample for detection

    Returns:
        Detected encoding or None if detection fails
    """
    try:
        import chardet

        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)

        result = chardet.detect(sample)
        encoding = result.get('encoding')
        confidence = result.get('confidence', 0)

        if encoding and confidence > 0.7:
            logger.debug(f"Detected encoding {encoding} with confidence {confidence:.2f}")
            return encoding
        else:
            logger.warning(f"Low confidence encoding detection: {encoding} ({confidence:.2f})")
            return get_config().default_encoding

    except ImportError:
        logger.warning("chardet not available, using default encoding")
        return get_config().default_encoding
    except Exception as e:
        logger.warning(f"Encoding detection failed: {e}, using default")
        return get_config().default_encoding



