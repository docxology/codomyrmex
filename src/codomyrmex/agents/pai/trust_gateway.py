"""Trust gateway for PAI ↔ Codomyrmex MCP tool access control.

Implements a three-tier trust model: UNTRUSTED → VERIFIED → TRUSTED.

- ``/codomyrmexVerify`` audits capabilities and promotes safe tools to VERIFIED.
- ``/codomyrmexTrust`` promotes destructive tools to TRUSTED for execution.

Example::

    from codomyrmex.agents.pai.trust_gateway import (
        verify_capabilities,
        trust_tool,
        trusted_call_tool,
    )

    report = verify_capabilities()       # audit everything
    trust_tool("codomyrmex.write_file")  # enable writes
    result = trusted_call_tool("codomyrmex.write_file", path="x.py", content="...")
"""

from __future__ import annotations

import enum
import importlib
import json
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.agents.pai.mcp_bridge import (
    RESOURCE_COUNT,
    _TOOL_DEFINITIONS,
    _RESOURCE_DEFINITIONS,
    _PROMPT_DEFINITIONS,
    call_tool,
    create_codomyrmex_mcp_server,
    get_skill_manifest,
    get_tool_registry,
    get_total_tool_count,
)

logger = get_logger(__name__)


# =====================================================================
# Trust Model
# =====================================================================

class TrustLevel(enum.Enum):
    """Trust tier for an MCP tool."""

    UNTRUSTED = "untrusted"
    VERIFIED = "verified"
    TRUSTED = "trusted"


# Tools that can mutate state — require explicit TRUSTED promotion.
DESTRUCTIVE_TOOLS: frozenset[str] = frozenset({
    "codomyrmex.write_file",
    "codomyrmex.run_command",
    "codomyrmex.run_tests",
    "codomyrmex.call_module_function",
})

# Patterns that indicate a tool may have side effects (for auto-discovered tools).
_DESTRUCTIVE_PATTERNS: frozenset[str] = frozenset({
    "write", "delete", "remove", "execute", "run", "drop",
    "create", "update", "modify", "set", "reset", "clear",
    "purge", "destroy", "kill", "terminate", "send", "push",
    "mutate", "shutdown", "stop",
})


def _is_destructive(tool_name: str) -> bool:
    """Check if an auto-discovered tool name matches destructive patterns."""
    if tool_name in DESTRUCTIVE_TOOLS:
        return True
    # Only apply pattern matching to auto-discovered tools (codomyrmex.module.func)
    parts = tool_name.split(".")
    if len(parts) >= 3:
        func_name = parts[-1].lower()
        return any(pattern in func_name for pattern in _DESTRUCTIVE_PATTERNS)
    return False


def _get_destructive_tools() -> frozenset[str]:
    """Get all destructive tool names (explicit + pattern-matched)."""
    registry = get_tool_registry()
    all_names = registry.list_tools()
    return frozenset(name for name in all_names if _is_destructive(name))


def _get_safe_tools() -> frozenset[str]:
    """Get all safe tool names (static + dynamic, minus destructive)."""
    registry = get_tool_registry()
    all_names = frozenset(registry.list_tools())
    return all_names - _get_destructive_tools()



class _LazyToolSets:
    """Non-caching lazy evaluator for tool sets.

    Each access computes fresh from the registry, avoiding
    import-ordering issues with dynamic tool discovery.
    """

    @staticmethod
    def safe_tools() -> frozenset[str]:
        return _get_safe_tools()

    @staticmethod
    def destructive_tools_set() -> frozenset[str]:
        return _get_destructive_tools()


# Module-level names for backwards compatibility — computed lazily.
class _FrozenSetProxy:
    """Proxy that behaves like a frozenset but delegates to lazy computation."""

    def __init__(self, accessor):
        self._accessor = accessor

    def __contains__(self, item):
        return item in self._accessor()

    def __iter__(self):
        return iter(self._accessor())

    def __len__(self):
        return len(self._accessor())

    def __or__(self, other):
        return self._accessor() | other

    def __ror__(self, other):
        return other | self._accessor()

    def __and__(self, other):
        return self._accessor() & other

    def __sub__(self, other):
        return self._accessor() - other

    def __repr__(self):
        return repr(self._accessor())


SAFE_TOOLS = _FrozenSetProxy(_LazyToolSets.safe_tools)


class _LazyInt:
    """Integer proxy that always evaluates fresh from a callable."""

    def __init__(self, fn):
        self._fn = fn

    def _get(self):
        return self._fn()

    def __eq__(self, other):
        return self._get() == other

    def __ne__(self, other):
        return self._get() != other

    def __lt__(self, other):
        return self._get() < other

    def __gt__(self, other):
        return self._get() > other

    def __le__(self, other):
        return self._get() <= other

    def __ge__(self, other):
        return self._get() >= other

    def __add__(self, other):
        return self._get() + (other._get() if isinstance(other, _LazyInt) else other)

    def __radd__(self, other):
        return other + self._get()

    def __sub__(self, other):
        return self._get() - (other._get() if isinstance(other, _LazyInt) else other)

    def __rsub__(self, other):
        return other - self._get()

    def __int__(self):
        return self._get()

    def __repr__(self):
        return repr(self._get())

    def __hash__(self):
        return hash(self._get())


SAFE_TOOL_COUNT = _LazyInt(lambda: len(_get_safe_tools()))
DESTRUCTIVE_TOOL_COUNT = _LazyInt(lambda: len(_get_destructive_tools()))



class TrustRegistry:
    """In-memory trust ledger for Codomyrmex MCP tools.

    Thread-safe by design (single-process, GIL-protected dict ops).
    """

    def __init__(self) -> None:
        self._ledger_path = Path.home() / ".codomyrmex" / "trust_ledger.json"
        
        # Initialize default state with ALL known tools (static + dynamic)
        registry = get_tool_registry()
        all_tool_names = registry.list_tools()
        
        self._levels: dict[str, TrustLevel] = {}
        for name in all_tool_names:
            self._levels[name] = TrustLevel.UNTRUSTED
            
        # Load persisted state if available
        self._load()

    def _load(self) -> None:
        """Load trust state from disk."""
        if not self._ledger_path.exists():
            return
            
        try:
            data = json.loads(self._ledger_path.read_text())
            for name, level_val in data.items():
                if name in self._levels:
                    try:
                        self._levels[name] = TrustLevel(level_val)
                    except ValueError:
                        pass
        except Exception as e:
            logger.warning(f"Failed to load trust ledger: {e}")

    def _save(self) -> None:
        """Save trust state to disk."""
        try:
            self._ledger_path.parent.mkdir(parents=True, exist_ok=True)
            data = {name: lvl.value for name, lvl in self._levels.items()}
            self._ledger_path.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Failed to save trust ledger: {e}")

    # ── Queries ───────────────────────────────────────────────────

    def level(self, tool_name: str) -> TrustLevel:
        """Get the current trust level for *tool_name*."""
        # Reload to ensure we see updates from other processes
        self._load()
        return self._levels.get(tool_name, TrustLevel.UNTRUSTED)

    # ── Mutations ─────────────────────────────────────────────────

    def verify_all_safe(self) -> list[str]:
        """Promote all safe (read-only) tools to VERIFIED. Return promoted names."""
        self._load() # Refresh first
        promoted = []
        for name in SAFE_TOOLS:
            if name in self._levels and self._levels[name] == TrustLevel.UNTRUSTED:
                self._levels[name] = TrustLevel.VERIFIED
                promoted.append(name)
        
        if promoted:
            self._save()
            
        return sorted(promoted)

    def trust_tool(self, tool_name: str) -> TrustLevel:
        """Promote *tool_name* to TRUSTED."""
        self._load() # Refresh first
        if tool_name not in self._levels:
            raise KeyError(
                f"Unknown tool: {tool_name!r}. "
                f"Available: {sorted(self._levels.keys())}"
            )
        self._levels[tool_name] = TrustLevel.TRUSTED
        self._save()
        logger.info("Tool %s promoted to TRUSTED", tool_name)
        return TrustLevel.TRUSTED

    def trust_all(self) -> list[str]:
        """Promote **all** tools to TRUSTED. Return promoted names."""
        self._load() # Refresh first
        promoted = []
        for name in self._levels:
            if self._levels[name] != TrustLevel.TRUSTED:
                self._levels[name] = TrustLevel.TRUSTED
                promoted.append(name)
        
        if promoted:
            self._save()
            
        logger.info("All %d tools promoted to TRUSTED", len(promoted))
        return sorted(promoted)

    def is_at_least_verified(self, tool_name: str) -> bool:
        """Return ``True`` if the tool is VERIFIED or TRUSTED."""
        return self.level(tool_name) in (TrustLevel.VERIFIED, TrustLevel.TRUSTED)

    def is_trusted(self, tool_name: str) -> bool:
        """Return ``True`` if the tool is TRUSTED."""
        return self.level(tool_name) == TrustLevel.TRUSTED

    def get_report(self) -> dict[str, Any]:
        """Return current trust state as a JSON-serializable dict."""
        # Reload before reporting
        self._load()
        by_level: dict[str, list[str]] = {
            "untrusted": [],
            "verified": [],
            "trusted": [],
        }
        for name, lvl in sorted(self._levels.items()):
            by_level[lvl.value].append(name)
        return {
            "total_tools": len(self._levels),
            "by_level": by_level,
            "counts": {k: len(v) for k, v in by_level.items()},
        }

    def reset(self) -> None:
        """Reset all tools to UNTRUSTED."""
        for name in self._levels:
            self._levels[name] = TrustLevel.UNTRUSTED
        self._save()


# ── Module-level singleton ────────────────────────────────────────────

_registry = TrustRegistry()


# =====================================================================
# Public API
# =====================================================================

def verify_capabilities() -> dict[str, Any]:
    """Run a full read-only audit of all Codomyrmex capabilities.

    This is the backing function for ``/codomyrmexVerify``.

    Returns:
        Structured report with modules, tools, resources, prompts,
        MCP server health, PAI bridge status, and trust state.
    """
    # ── Module inventory ──────────────────────────────────────────
    import codomyrmex
    modules = codomyrmex.list_modules()

    # ── Promote safe tools to VERIFIED (before snapshot) ──────────
    promoted = _registry.verify_all_safe()

    # ── Tool registry ─────────────────────────────────────────────
    registry = get_tool_registry()
    tool_names = registry.list_tools()

    tool_details = []
    for name in sorted(tool_names):
        entry = registry.get(name)
        tool_details.append({
            "name": name,
            "description": entry["schema"].get("description", "") if entry else "",
            "has_handler": entry is not None and entry.get("handler") is not None,
            "category": "destructive" if name in DESTRUCTIVE_TOOLS else "safe",
            "trust_level": _registry.level(name).value,
        })

    # ── Resources & Prompts ───────────────────────────────────────
    resources = [
        {"uri": r[0], "name": r[1], "description": r[2]}
        for r in _RESOURCE_DEFINITIONS
    ]
    prompts = [
        {"name": p[0], "description": p[1]}
        for p in _PROMPT_DEFINITIONS
    ]

    # ── MCP server health ─────────────────────────────────────────
    expected_tool_count = get_total_tool_count()
    expected_prompt_count = len(_PROMPT_DEFINITIONS)
    try:
        server = create_codomyrmex_mcp_server()
        server_tool_count = len(server._tool_registry.list_tools())
        server_resource_count = len(server._resources)
        server_prompt_count = len(server._prompts)
        mcp_healthy = (
            server_tool_count == expected_tool_count
            and server_resource_count == RESOURCE_COUNT
            and server_prompt_count == expected_prompt_count
        )
    except Exception as exc:
        mcp_healthy = False
        server_tool_count = 0
        server_resource_count = 0
        server_prompt_count = 0
        logger.warning("MCP server health check failed: %s", exc)

    # ── PAI bridge status ─────────────────────────────────────────
    try:
        from codomyrmex.agents.pai import PAIBridge
        bridge = PAIBridge()
        pai_status = {
            "installed": bridge.is_installed(),
            "components": bridge.get_components() if bridge.is_installed() else {},
        }
    except Exception as exc:
        pai_status = {"installed": False, "error": str(exc)}

    # ── Skill manifest ────────────────────────────────────────────
    manifest = get_skill_manifest()
    manifest_valid = (
        manifest.get("name") == "Codomyrmex"
        and len(manifest.get("tools", [])) == expected_tool_count
    )

    report = {
        "status": "verified",
        "modules": {
            "count": len(modules),
            "names": modules,
        },
        "tools": {
            "count": len(tool_details),
            "expected": expected_tool_count,
            "match": len(tool_details) == expected_tool_count,
            "safe_count": len(_get_safe_tools()),
            "destructive_count": len(_get_destructive_tools()),
            "items": tool_details,
        },
        "resources": {
            "count": len(resources),
            "expected": RESOURCE_COUNT,
            "items": resources,
        },
        "prompts": {
            "count": len(prompts),
            "expected": expected_prompt_count,
            "items": prompts,
        },
        "mcp_server": {
            "healthy": mcp_healthy,
            "tools": server_tool_count,
            "resources": server_resource_count,
            "prompts": server_prompt_count,
        },
        "pai_bridge": pai_status,
        "skill_manifest": {
            "valid": manifest_valid,
            "version": manifest.get("version"),
        },
        "trust": {
            "promoted_to_verified": promoted,
            "current_state": _registry.get_report(),
        },
    }

    logger.info(
        "Verify complete: %d modules, %d tools (%d safe, %d destructive), MCP %s",
        len(modules),
        len(tool_details),
        len(SAFE_TOOLS),
        len(DESTRUCTIVE_TOOLS),
        "healthy" if mcp_healthy else "UNHEALTHY",
    )
    return report


def trust_tool(tool_name: str) -> dict[str, Any]:
    """Promote a single tool to TRUSTED.

    This is the backing function for ``/codomyrmexTrust <tool>``.

    Args:
        tool_name: Fully-qualified tool name (e.g. ``"codomyrmex.write_file"``).

    Returns:
        Trust state after promotion.
    """
    new_level = _registry.trust_tool(tool_name)
    return {
        "tool": tool_name,
        "new_level": new_level.value,
        "report": _registry.get_report(),
    }


def trust_all() -> dict[str, Any]:
    """Promote **all** tools to TRUSTED.

    Returns:
        Trust state after promotion.
    """
    promoted = _registry.trust_all()
    return {
        "promoted": promoted,
        "count": len(promoted),
        "report": _registry.get_report(),
    }


def get_trust_report() -> dict[str, Any]:
    """Get the current trust state for all tools."""
    return _registry.get_report()


def is_trusted(tool_name: str) -> bool:
    """Check if a tool is TRUSTED for execution."""
    return _registry.is_trusted(tool_name)


def trusted_call_tool(name: str, **kwargs: Any) -> dict[str, Any]:
    """Call a Codomyrmex MCP tool with trust enforcement.

    Safe tools require at least VERIFIED.  Destructive tools require TRUSTED.

    Args:
        name: Tool name (e.g. ``"codomyrmex.list_modules"``).
        **kwargs: Tool arguments.

    Returns:
        Tool result dictionary.

    Raises:
        PermissionError: If the tool's trust level is insufficient.
        KeyError: If the tool is unknown.
    """
    # Validate tool exists first (raises KeyError for unknown tools).
    registry = get_tool_registry()
    known_tools = set(registry.list_tools())
    if name not in known_tools:
        raise KeyError(
            f"Unknown tool: {name!r}. "
            f"Available: {sorted(known_tools)}"
        )

    level = _registry.level(name)

    if name in DESTRUCTIVE_TOOLS and level != TrustLevel.TRUSTED:
        raise PermissionError(
            f"Tool {name!r} requires TRUSTED level (current: {level.value}). "
            f"Run /codomyrmexTrust or call trust_tool({name!r}) first."
        )

    if level == TrustLevel.UNTRUSTED:
        raise PermissionError(
            f"Tool {name!r} is UNTRUSTED. "
            f"Run /codomyrmexVerify or call verify_capabilities() first."
        )

    return call_tool(name, **kwargs)


def reset_trust() -> None:
    """Reset all trust levels to UNTRUSTED."""
    _registry.reset()



# =====================================================================
# Constants (use the lazy definitions from lines ~198-199)
# =====================================================================


__all__ = [
    "TrustLevel",
    "TrustRegistry",
    "DESTRUCTIVE_TOOLS",
    "SAFE_TOOLS",
    "SAFE_TOOL_COUNT",
    "DESTRUCTIVE_TOOL_COUNT",
    "_get_destructive_tools",
    "_is_destructive",
    "verify_capabilities",
    "trust_tool",
    "trust_all",
    "get_trust_report",
    "is_trusted",
    "trusted_call_tool",
    "reset_trust",
]

