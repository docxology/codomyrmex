"""Standardized MCP tool response factory functions.

All MCP tool responses follow a consistent schema::

    # Success
    {"status": "success", "message": str, "data": Any, ...}

    # Error
    {"status": "error", "message": str}

Usage::

    from codomyrmex.model_context_protocol.response_helpers import ok_response, error_response

    @mcp_tool(category="my_module")
    def my_tool(arg: str) -> dict:
        try:
            result = do_work(arg)
            return ok_response({"result": result})
        except Exception as exc:
            return error_response(str(exc))
"""

from __future__ import annotations

from typing import Any


def ok_response(data: dict[str, Any] | None = None, message: str = "OK") -> dict[str, Any]:
    """Return a standardized MCP success response.

    Args:
        data: Additional key-value pairs to merge into the response.
        message: Human-readable success message.

    Returns:
        dict with ``status="success"`` and any extra ``data`` fields merged in.
    """
    response: dict[str, Any] = {"status": "success", "message": message}
    if data:
        response.update(data)
    return response


def error_response(message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a standardized MCP error response.

    Args:
        message: Human-readable error description.
        data: Optional additional key-value pairs to merge into the response.

    Returns:
        dict with ``status="error"`` and ``message``.
    """
    response: dict[str, Any] = {"status": "error", "message": message}
    if data:
        response.update(data)
    return response
