"""Dependency-free destructive-tool classification metadata.

This module intentionally contains no registry, filesystem, or runtime
initialization. Both the trust gateway and read-only capability navigation can
use it without creating a circular dependency or performing a live probe.
"""

from __future__ import annotations

EXPLICIT_DESTRUCTIVE_TOOLS: frozenset[str] = frozenset(
    {
        "codomyrmex.write_file",
        "codomyrmex.run_command",
        "codomyrmex.run_tests",
        "codomyrmex.call_module_function",
        # Pickle deserialization can execute attacker-controlled reducers.
        "codomyrmex.deserialize_data",
    }
)

DESTRUCTIVE_TOOL_NAME_PATTERNS: frozenset[str] = frozenset(
    {
        # VCS, deployment, and external-communication verbs are side effects
        # even when a dynamically discovered handler does not use one of the
        # generic mutation verbs below.
        "broadcast",
        "checkout",
        "clean",
        "clone",
        "commit",
        "deploy",
        "write",
        "delete",
        "remove",
        "execute",
        "run",
        "drop",
        "create",
        "update",
        "modify",
        "change",
        "set",
        "grant",
        "init",
        "install",
        "invalidate",
        "migrate",
        "move",
        "pull",
        "push",
        "publish",
        "revoke",
        "reset",
        "clear",
        "send",
        "stage",
        "start",
        "stop",
        "sync",
        "kill",
        "terminate",
        "trigger",
        "upload",
        "put",
    }
)


def is_destructive_tool(tool_name: str) -> bool:
    """Return whether a canonical MCP tool name needs elevated trust."""
    if not isinstance(tool_name, str):
        return False
    if tool_name in EXPLICIT_DESTRUCTIVE_TOOLS:
        return True
    # Dynamic registries occasionally expose a bare callable name.  Trust
    # classification must not become fail-open merely because the name has no
    # module prefix.
    function_name = tool_name.rsplit(".", 1)[-1].lower()
    return any(pattern in function_name for pattern in DESTRUCTIVE_TOOL_NAME_PATTERNS)


__all__ = [
    "DESTRUCTIVE_TOOL_NAME_PATTERNS",
    "EXPLICIT_DESTRUCTIVE_TOOLS",
    "is_destructive_tool",
]
