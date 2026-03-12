"""Helper functions for Coda.io data models."""

from datetime import datetime

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse ISO 8601 datetime string."""
    if not value:
        return None
    try:
        # Handle various ISO 8601 formats
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except (ValueError, TypeError) as e:
        logger.debug("Failed to parse datetime %r: %s", value, e)
        return None
