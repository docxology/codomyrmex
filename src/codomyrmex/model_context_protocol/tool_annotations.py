"""Validated MCP behavior hints, independent of tool authorization."""

from collections.abc import Mapping
from copy import deepcopy
from typing import Any


def normalize_tool_annotations(
    annotations: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Copy behavior hints, filling omitted fields with MCP's cautious defaults.

    Hints describe behavior to clients; they never grant tool permissions.
    Boolean values are checked strictly so strings such as ``"false"`` cannot
    accidentally advertise a tool as safe.
    """
    result: dict[str, Any] = {
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    }
    if annotations is None:
        return result
    if not isinstance(annotations, Mapping):
        raise ValueError("tool annotations must be a mapping")
    for key, value in annotations.items():
        if key in result:
            if type(value) is not bool:
                raise ValueError(f"tool annotation {key} must be a boolean")
        elif key == "title":
            if not isinstance(value, str):
                raise ValueError("tool annotation title must be a string")
        else:
            raise ValueError(f"unknown tool annotation: {key}")
        result[key] = value
    return result


def annotated_tool_schema(
    schema: dict[str, Any], handler: Any = None
) -> dict[str, Any]:
    """Copy a tool schema and retain explicit or decorated behavior hints."""
    result = deepcopy(schema)
    annotations = result.get("annotations")
    if "annotations" not in result and handler is not None:
        metadata = getattr(handler, "_mcp_tool_meta", {})
        annotations = metadata.get("annotations")
    result["annotations"] = normalize_tool_annotations(annotations)
    return result
