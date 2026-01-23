"""Session Management for Code Execution.

Handles execution session management for persistent environments, allowing
state to be maintained between code executions. Sessions are identified
by validated session IDs.

Attributes:
    ACTIVE_SESSIONS: Dictionary tracking active session containers and
        their associated state.

Example:
    >>> from codomyrmex.coding.execution.session_manager import validate_session_id
    >>> session_id = validate_session_id("user_123_session")
    >>> if session_id:
    ...     print(f"Valid session: {session_id}")
"""

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Session management (if needed)
ACTIVE_SESSIONS = {}  # Dictionary to track active session containers


def validate_session_id(session_id: str | None) -> str | None:
    """Validate and sanitize a session ID string.

    Ensures the session ID meets security requirements: alphanumeric
    characters plus underscores and hyphens only, with a maximum
    length of 64 characters.

    Args:
        session_id: The session ID to validate, or None.

    Returns:
        The validated session ID if valid, or None if the input was
        None or invalid.

    Example:
        >>> validate_session_id("user_123")
        'user_123'
        >>> validate_session_id("session-abc-def")
        'session-abc-def'
        >>> validate_session_id("invalid@session!")
        None
        >>> validate_session_id("a" * 100)  # Too long
        None
        >>> validate_session_id(None)
        None
    """
    if session_id is None:
        return None

    # Basic validation - alphanumeric plus underscores/hyphens, max length
    if not isinstance(session_id, str) or len(session_id) > 64:
        return None

    for char in session_id:
        if not (char.isalnum() or char in "_-"):
            return None

    return session_id

