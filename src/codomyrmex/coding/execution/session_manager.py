
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)
"""
Session Management

Handles execution session management for persistent environments.
"""

# Session management (if needed)
ACTIVE_SESSIONS = {}  # Dictionary to track active session containers


def validate_session_id(session_id: str | None) -> str | None:
    """Validate session ID format if provided."""
    if session_id is None:
        return None

    # Basic validation - alphanumeric plus underscores/hyphens, max length
    if not isinstance(session_id, str) or len(session_id) > 64:
        return None

    for char in session_id:
        if not (char.isalnum() or char in "_-"):
            return None

    return session_id

