
# Utility functions for exception handling
def format_exception_chain(exception: Exception) -> str:
    """Format an exception chain for display.

    Args:
        exception: The exception to format

    Returns:
        A formatted string representation of the exception chain
    """
    lines = []
    current: Optional[BaseException] = exception

    while current:
        if isinstance(current, CodomyrmexError):
            lines.append(str(current))
        else:
            lines.append(f"[{current.__class__.__name__}] {str(current)}")
        current = current.__cause__ or current.__context__

    return "\n".join(lines)


def create_error_context(**kwargs: Any) -> dict[str, Any]:
    """Create a context dictionary for exception handling.

    Args:
        **kwargs: Context key-value pairs

    Returns:
        A dictionary suitable for use as exception context
    """
    return {k: v for k, v in kwargs.items() if v is not None}
