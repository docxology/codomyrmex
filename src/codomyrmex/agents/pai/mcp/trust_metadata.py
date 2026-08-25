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

# Tools explicitly declared safe.  Because the default for dynamically
# discovered tools is DESTRUCTIVE (fail-closed), any tool not in this list
# or in EXPLICIT_DESTRUCTIVE_TOOLS is treated as destructive.
EXPLICIT_SAFE_TOOLS: frozenset[str] = frozenset(
    {
        "codomyrmex.read_file",
        "codomyrmex.list_directory",
        "codomyrmex.search_codebase",
        "codomyrmex.git_status",
        "codomyrmex.git_diff",
        "codomyrmex.json_query",
        "codomyrmex.checksum_file",
        "codomyrmex.get_package_version",
        "codomyrmex.tool_list_modules",
        "codomyrmex.tool_module_info",
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
    """Return whether a canonical MCP tool name needs elevated trust.

    Default is ``True`` (destructive/fail-closed).  A tool is classified as
    *safe* only when it appears in ``EXPLICIT_SAFE_TOOLS``.  The name-pattern
    heuristic in ``DESTRUCTIVE_TOOL_NAME_PATTERNS`` is a *warning* fallback
    only — it never downgrades a tool from destructive to safe.
    """
    if not isinstance(tool_name, str):
        return True  # fail-closed: unclassifiable → destructive
    if tool_name in EXPLICIT_SAFE_TOOLS:
        return False
    if tool_name in EXPLICIT_DESTRUCTIVE_TOOLS:
        return True
    # Dynamic registries occasionally expose a bare callable name.  Trust
    # classification must not become fail-open merely because the name has no
    # module prefix.
    function_name = tool_name.rsplit(".", 1)[-1].lower()
    # Pattern match is advisory: if the name *does* match a destructive
    # pattern, confirm it.  If it does NOT match, the safe-by-default
    # behaviour is eliminated — we still return True (destructive).
    if any(pattern in function_name for pattern in DESTRUCTIVE_TOOL_NAME_PATTERNS):
        return True
    return True  # default: destructive by default


__all__ = [
    "DESTRUCTIVE_TOOL_NAME_PATTERNS",
    "EXPLICIT_DESTRUCTIVE_TOOLS",
    "EXPLICIT_SAFE_TOOLS",
    "is_destructive_tool",
]
