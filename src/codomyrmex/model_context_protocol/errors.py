"""
MCP Structured Error Types

Provides typed error envelopes for MCP tool invocations so that clients
receive machine-readable failure information instead of raw exception strings.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MCPErrorCode(str, Enum):
    """Canonical error codes for MCP tool invocations."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    EXECUTION_ERROR = "EXECUTION_ERROR"
    TIMEOUT = "TIMEOUT"
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMITED = "RATE_LIMITED"
    CIRCUIT_OPEN = "CIRCUIT_OPEN"
    DEPENDENCY_MISSING = "DEPENDENCY_MISSING"
    INTERNAL = "INTERNAL"


@dataclass(frozen=True, slots=True)
class FieldError:
    """Describes a single field-level validation failure."""

    field: str
    constraint: str
    value: Any = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"field": self.field, "constraint": self.constraint}
        if self.value is not None:
            d["value"] = self.value
        return d


@dataclass(slots=True)
class MCPToolError:
    """Structured error envelope for MCP tool invocations.

    Carries enough context for programmatic error handling on the client side
    while remaining serialisable to the standard MCP ``isError: true`` response.
    """

    code: MCPErrorCode
    message: str
    tool_name: str = ""
    module: str = ""
    field_errors: list[FieldError] = field(default_factory=list)
    suggestion: str | None = None
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""
        d: dict[str, Any] = {
            "code": self.code.value,
            "message": self.message,
            "correlation_id": self.correlation_id,
        }
        if self.tool_name:
            d["tool_name"] = self.tool_name
        if self.module:
            d["module"] = self.module
        if self.field_errors:
            d["field_errors"] = [fe.to_dict() for fe in self.field_errors]
        if self.suggestion:
            d["suggestion"] = self.suggestion
        return d

    def to_json(self) -> str:
        """Serialise to a JSON string."""
        return json.dumps(self.to_dict())

    def to_mcp_response(self) -> dict[str, Any]:
        """Build an MCP-compatible ``isError: true`` response body."""
        return {
            "content": [{"type": "text", "text": self.to_json()}],
            "isError": True,
        }

    # ------------------------------------------------------------------
    # Deserialisation
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MCPToolError:
        """Reconstruct from a dictionary (e.g. parsed from JSON)."""
        field_errors = [
            FieldError(**fe) for fe in data.get("field_errors", [])
        ]
        return cls(
            code=MCPErrorCode(data["code"]),
            message=data["message"],
            tool_name=data.get("tool_name", ""),
            module=data.get("module", ""),
            field_errors=field_errors,
            suggestion=data.get("suggestion"),
            correlation_id=data.get("correlation_id", uuid.uuid4().hex[:12]),
        )

    @classmethod
    def from_json(cls, text: str) -> MCPToolError:
        """Reconstruct from a JSON string."""
        return cls.from_dict(json.loads(text))

    @classmethod
    def from_mcp_response(cls, response: dict[str, Any]) -> MCPToolError | None:
        """Attempt to parse an ``MCPToolError`` from an MCP response.

        Returns ``None`` if the response is not an error or doesn't contain
        a parseable structured error.
        """
        if not response.get("isError"):
            return None
        content = response.get("content", [])
        if not content:
            return None
        text = content[0].get("text", "")
        try:
            return cls.from_json(text)
        except (json.JSONDecodeError, KeyError, ValueError):
            # DEPRECATED(v0.2.0): Legacy unstructured error wrapping. Will be removed in v0.3.0.
            return cls(
                code=MCPErrorCode.INTERNAL,
                message=text,
            )


# ------------------------------------------------------------------
# Convenience constructors
# ------------------------------------------------------------------


def validation_error(
    tool_name: str,
    message: str,
    field_errors: list[FieldError] | None = None,
) -> MCPToolError:
    """Create a ``VALIDATION_ERROR``."""
    return MCPToolError(
        code=MCPErrorCode.VALIDATION_ERROR,
        message=message,
        tool_name=tool_name,
        field_errors=field_errors or [],
    )


def not_found_error(tool_name: str) -> MCPToolError:
    """Create a ``NOT_FOUND`` error for an unknown tool."""
    return MCPToolError(
        code=MCPErrorCode.NOT_FOUND,
        message=f"Tool not found: {tool_name!r}",
        tool_name=tool_name,
    )


def timeout_error(tool_name: str, seconds: float) -> MCPToolError:
    """Create a ``TIMEOUT`` error."""
    return MCPToolError(
        code=MCPErrorCode.TIMEOUT,
        message=f"Tool {tool_name!r} timed out after {seconds}s",
        tool_name=tool_name,
    )


def execution_error(
    tool_name: str,
    exception: Exception,
    *,
    module: str = "",
    suggestion: str | None = None,
) -> MCPToolError:
    """Create an ``EXECUTION_ERROR`` from a caught exception."""
    return MCPToolError(
        code=MCPErrorCode.EXECUTION_ERROR,
        message=f"{type(exception).__name__}: {exception}",
        tool_name=tool_name,
        module=module,
        suggestion=suggestion,
    )


__all__ = [
    "MCPErrorCode",
    "MCPToolError",
    "FieldError",
    "validation_error",
    "not_found_error",
    "timeout_error",
    "execution_error",
]
