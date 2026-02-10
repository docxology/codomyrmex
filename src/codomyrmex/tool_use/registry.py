"""
Tool registry for managing available tools.

Provides a central registry where tools can be registered, discovered,
and invoked. Includes a decorator for marking functions as tools.
"""

from __future__ import annotations

import functools
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from codomyrmex.schemas import Result, ResultStatus, ToolDefinition

from .validation import ValidationResult, validate_input, validate_output


@dataclass
class ToolEntry:
    """
    A registered tool entry in the registry.

    Attributes:
        name: Unique identifier for the tool.
        description: Human-readable description of what the tool does.
        handler: The callable that executes the tool logic.
        input_schema: JSON-schema-like dict describing expected input.
        output_schema: JSON-schema-like dict describing expected output.
        tags: Categorization tags for search and filtering.
    """

    name: str
    description: str
    handler: Callable[..., Any]
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def to_tool_definition(self, module: str = "tool_use") -> ToolDefinition:
        """Convert to the shared ToolDefinition schema type."""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            module=module,
            input_schema=self.input_schema,
            output_schema=self.output_schema,
            tags=list(self.tags),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "tags": self.tags,
        }


class ToolRegistry:
    """
    Central registry for managing available tools.

    Supports registration, lookup, search by tags/name, and
    invocation with optional input/output validation.

    Example::

        registry = ToolRegistry()
        registry.register(ToolEntry(
            name="greet",
            description="Say hello",
            handler=lambda data: {"message": f"Hello, {data['name']}!"},
            input_schema={"type": "object", "required": ["name"],
                          "properties": {"name": {"type": "string"}}},
        ))

        result = registry.invoke("greet", {"name": "World"})
        assert result.ok
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolEntry] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, entry: ToolEntry) -> None:
        """
        Register a tool entry.

        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        if entry.name in self._tools:
            raise ValueError(
                f"Tool '{entry.name}' is already registered. "
                "Unregister it first or use a different name."
            )
        self._tools[entry.name] = entry

    def unregister(self, name: str) -> bool:
        """
        Remove a tool by name.

        Returns:
            True if the tool existed and was removed, False otherwise.
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, name: str) -> ToolEntry | None:
        """Retrieve a tool entry by exact name, or None if not found."""
        return self._tools.get(name)

    def list(self) -> list[ToolEntry]:
        """Return all registered tool entries, sorted by name."""
        return sorted(self._tools.values(), key=lambda e: e.name)

    def list_names(self) -> list[str]:
        """Return sorted list of all registered tool names."""
        return sorted(self._tools.keys())

    def search(
        self,
        *,
        name_contains: str | None = None,
        tags: list[str] | None = None,
        match_all_tags: bool = False,
    ) -> list[ToolEntry]:
        """
        Search for tools by name substring and/or tags.

        Args:
            name_contains: Substring to match against tool names (case-insensitive).
            tags: Tags to filter by.
            match_all_tags: If True, tool must have ALL specified tags.
                If False (default), tool must have at least one.

        Returns:
            List of matching ToolEntry objects, sorted by name.
        """
        results: list[ToolEntry] = []
        for entry in self._tools.values():
            # Name filter
            if name_contains is not None:
                if name_contains.lower() not in entry.name.lower():
                    continue

            # Tag filter
            if tags is not None and len(tags) > 0:
                entry_tag_set = set(entry.tags)
                search_tag_set = set(tags)
                if match_all_tags:
                    if not search_tag_set.issubset(entry_tag_set):
                        continue
                else:
                    if not search_tag_set.intersection(entry_tag_set):
                        continue

            results.append(entry)

        return sorted(results, key=lambda e: e.name)

    # ------------------------------------------------------------------
    # Invocation
    # ------------------------------------------------------------------

    def invoke(
        self,
        name: str,
        input_data: Any = None,
        *,
        validate: bool = True,
    ) -> Result:
        """
        Look up a tool by name and invoke it with validation.

        Args:
            name: Name of the registered tool.
            input_data: Data to pass to the tool handler.
            validate: Whether to validate input/output against schemas.

        Returns:
            A Result object with the tool's output or error information.
        """
        entry = self.get(name)
        if entry is None:
            return Result(
                status=ResultStatus.FAILURE,
                message=f"Tool '{name}' not found in registry.",
                errors=[f"Unknown tool: {name}"],
            )

        # Input validation
        if validate and entry.input_schema:
            vr = validate_input(input_data, entry.input_schema)
            if not vr.valid:
                return Result(
                    status=ResultStatus.FAILURE,
                    message=f"Input validation failed for tool '{name}'.",
                    errors=vr.errors,
                )

        # Execute
        start = time.monotonic()
        try:
            output = entry.handler(input_data)
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            return Result(
                status=ResultStatus.FAILURE,
                message=f"Tool '{name}' raised an exception: {exc}",
                errors=[str(exc)],
                duration_ms=elapsed,
            )
        elapsed = (time.monotonic() - start) * 1000

        # Output validation
        if validate and entry.output_schema:
            vr = validate_output(output, entry.output_schema)
            if not vr.valid:
                return Result(
                    status=ResultStatus.PARTIAL,
                    data=output,
                    message=f"Output validation failed for tool '{name}'.",
                    errors=vr.errors,
                    duration_ms=elapsed,
                )

        return Result(
            status=ResultStatus.SUCCESS,
            data=output,
            message=f"Tool '{name}' executed successfully.",
            duration_ms=elapsed,
        )

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __repr__(self) -> str:
        return f"ToolRegistry(tools={self.list_names()})"


# ======================================================================
# Decorator API
# ======================================================================

def tool(
    name: str,
    description: str = "",
    input_schema: dict[str, Any] | None = None,
    output_schema: dict[str, Any] | None = None,
    tags: list[str] | None = None,
    registry: ToolRegistry | None = None,
) -> Callable:
    """
    Decorator that marks a function as a tool and optionally registers it.

    The decorated function retains a `tool_entry` attribute containing
    the ToolEntry, which can be used for deferred registration.

    Args:
        name: Unique tool name.
        description: Human-readable description.
        input_schema: JSON-schema-like dict for input validation.
        output_schema: JSON-schema-like dict for output validation.
        tags: Categorization tags.
        registry: If provided, the tool is immediately registered here.

    Example::

        @tool(name="add", description="Add two numbers",
              input_schema={"type": "object", "required": ["a", "b"],
                            "properties": {"a": {"type": "number"},
                                           "b": {"type": "number"}}})
        def add(data):
            return {"sum": data["a"] + data["b"]}

        # Later, register it:
        my_registry.register(add.tool_entry)
    """

    def decorator(fn: Callable) -> Callable:
        entry = ToolEntry(
            name=name,
            description=description or fn.__doc__ or "",
            handler=fn,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            tags=tags or [],
        )

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return fn(*args, **kwargs)

        wrapper.tool_entry = entry  # type: ignore[attr-defined]

        if registry is not None:
            registry.register(entry)

        return wrapper

    return decorator


__all__ = [
    "ToolEntry",
    "ToolRegistry",
    "tool",
]
