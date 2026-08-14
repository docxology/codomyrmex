"""Filesystem boundary policy for PAI/MCP tool entrypoints.

The low-level file helpers remain useful as ordinary Python utilities and do
not impose an application-specific root.  MCP and PAI callers, however, are
untrusted input boundaries.  This module constrains their path-bearing
arguments to the current working tree by default, with explicit additional
roots supplied through ``CODOMYRMEX_MCP_ALLOWED_ROOTS``.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


class PathPolicyError(ValueError):
    """Raised when an MCP path escapes the configured capability roots."""


_PATH_FIELDS: dict[str, tuple[str, ...]] = {
    "read_file": ("path",),
    "write_file": ("path",),
    "list_directory": ("path",),
    "analyze_python": ("path",),
    "analyze_python_file": ("path",),
    "search_codebase": ("path",),
    "json_query": ("path",),
    "checksum_file": ("path",),
    "git_status": ("path",),
    "git_diff": ("path",),
    "run_command": ("cwd",),
    "list_workflows": ("project_root",),
}

_PATH_FIELD_NAMES = frozenset(
    {
        "path",
        "cwd",
        "root",
        "directory",
        "directories",
        "file",
        "files",
        "file_path",
        "input_path",
        "output_path",
        "output_dir",
        "project_path",
        "repo_path",
        "source_path",
        "target_path",
        "workspace_path",
    }
)


def _allowed_roots() -> tuple[Path, ...]:
    roots = [Path.cwd()]
    configured = os.environ.get("CODOMYRMEX_MCP_ALLOWED_ROOTS", "")
    roots.extend(Path(value) for value in configured.split(os.pathsep) if value)

    normalized: list[Path] = []
    for root in roots:
        try:
            resolved = root.expanduser().resolve()
        except OSError as exc:
            raise PathPolicyError(f"Unable to resolve allowed root {root!s}") from exc
        if resolved not in normalized:
            normalized.append(resolved)
    return tuple(normalized)


def resolve_allowed_path(raw_path: str, *, field: str) -> Path:
    """Resolve *raw_path* and require containment in an allowed root."""
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise PathPolicyError(f"{field} must be a non-empty string")
    try:
        candidate = Path(raw_path).expanduser().resolve()
    except OSError as exc:
        raise PathPolicyError(f"Unable to resolve {field}") from exc

    for root in _allowed_roots():
        try:
            candidate.relative_to(root)
            return candidate
        except ValueError:
            continue
    raise PathPolicyError(
        f"{field} resolves outside the configured MCP capability roots"
    )


def guard_tool_arguments(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Return arguments after enforcing path containment for a tool."""
    if not isinstance(arguments, dict):
        raise PathPolicyError("tool arguments must be an object")
    function_name = tool_name.rsplit(".", 1)[-1]
    fields = set(_PATH_FIELDS.get(function_name, ()))
    fields.update(
        key
        for key in arguments
        if isinstance(key, str)
        and (key in _PATH_FIELD_NAMES or key.endswith(("_path", "_dir", "_directory")))
    )
    guarded = dict(arguments)
    for field in fields:
        if field in guarded:
            value = guarded[field]
            if isinstance(value, (list, tuple)):
                guarded[field] = [
                    str(resolve_allowed_path(item, field=field)) for item in value
                ]
            else:
                guarded[field] = str(resolve_allowed_path(value, field=field))
    return guarded


__all__ = ["PathPolicyError", "guard_tool_arguments", "resolve_allowed_path"]
