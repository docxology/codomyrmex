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

    report = verify_capabilities()  # audit everything
    trust_tool("codomyrmex.write_file")  # enable writes
    result = trusted_call_tool("codomyrmex.write_file", path="x.py", content="...")
"""

from __future__ import annotations

import collections
import enum
import hashlib
import json
import logging
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

from codomyrmex.agents.pai.mcp.discovery import discover_dynamic_tools
from codomyrmex.agents.pai.mcp_bridge import (
    create_codomyrmex_mcp_server,
    get_tool_registry,
)
from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.quality.validation import validate_tool_arguments

if TYPE_CHECKING:
    from collections.abc import Callable

logger = get_logger(__name__)


# =====================================================================
# Trust Model
# =====================================================================


class TrustLevel(enum.Enum):
    """Trust tier for an MCP tool."""

    UNTRUSTED = "untrusted"
    VERIFIED = "verified"
    TRUSTED = "trusted"


class SecurityError(Exception):
    """Raised when a security policy is violated."""


# Tools that can mutate state — require explicit TRUSTED promotion.
DESTRUCTIVE_TOOLS: frozenset[str] = frozenset(
    {
        "codomyrmex.write_file",
        "codomyrmex.run_command",
        "codomyrmex.run_tests",
        "codomyrmex.call_module_function",
    }
)

# Audit Log
_AUDIT_LOG_MAX_SIZE = 10000
_audit_log: collections.deque = collections.deque(maxlen=_AUDIT_LOG_MAX_SIZE)
_audit_lock = threading.Lock()

# Confirmation
_REQUIRE_CONFIRMATION: bool = False
_pending_confirmations: dict[str, dict[str, Any]] = {}
_confirmations_lock = threading.Lock()
_CONFIRMATION_TTL = 60.0  # seconds


class AuditEntry(TypedDict):
    """Immutable record of a single tool call stored in the trust gateway audit log."""

    timestamp: str
    tool_name: str
    args_hash: str
    result_status: str  # "success" | "error" | "blocked"
    trust_level: str
    duration_ms: float
    error_code: str | None


def _log_audit_entry(
    tool_name: str,
    args: dict[str, Any],
    status: str,
    trust_level: str,
    duration_ms: float,
    error: Exception | None = None,
) -> None:
    """Record an entry in the audit log."""
    # Canonicalize args for consistent hashing
    try:
        args_json = json.dumps(args, sort_keys=True)
        args_hash = hashlib.sha256(args_json.encode()).hexdigest()
    except (TypeError, ValueError):
        args_hash = "unhashable"

    entry: AuditEntry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "tool_name": tool_name,
        "args_hash": args_hash,
        "result_status": status,
        "trust_level": trust_level,
        "duration_ms": duration_ms,
        "error_code": type(error).__name__ if error else None,
    }

    with _audit_lock:
        _audit_log.append(entry)


def set_require_confirmation(enabled: bool) -> None:
    """Enable or disable confirmation requirement for destructive tools."""
    global _REQUIRE_CONFIRMATION
    _REQUIRE_CONFIRMATION = enabled


def _cleanup_expired_confirmations_locked() -> None:
    """Remove expired confirmation tokens. Caller MUST hold _confirmations_lock."""
    now = time.monotonic()
    expired = [
        token
        for token, data in _pending_confirmations.items()
        if now - data["timestamp"] > _CONFIRMATION_TTL
    ]
    for token in expired:
        del _pending_confirmations[token]


def get_audit_log(
    since: datetime | None = None,
    tool_name: str | None = None,
    status: str | None = None,
) -> list[AuditEntry]:
    """Retrieve filtered audit log entries."""
    with _audit_lock:
        # fast path if no filters
        if not any((since, tool_name, status)):
            return list(_audit_log)

        results = []
        for entry in _audit_log:
            if tool_name and entry["tool_name"] != tool_name:
                continue
            if status and entry["result_status"] != status:
                continue
            if since:
                entry_dt = datetime.fromisoformat(entry["timestamp"])
                if entry_dt < since:
                    continue
            results.append(entry)
        return results


def export_audit_log(path: str | Path, format: str = "jsonl") -> None:
    """Export audit log to file."""
    path = Path(path)
    entries = get_audit_log()

    if format == "jsonl":
        with open(path, "w") as f:
            f.writelines(json.dumps(entry) + "\n" for entry in entries)
    else:
        raise ValueError(f"Unsupported format: {format}")


def clear_audit_log(before: datetime | None = None) -> int:
    """Clear audit log entries. Returns count removed."""
    with _audit_lock:
        if before is None:
            count = len(_audit_log)
            _audit_log.clear()
            return count

        # Deque doesn't support efficient middle removal,
        # so we rebuild it.
        retained = []
        removed = 0
        while _audit_log:
            entry = _audit_log.popleft()
            entry_dt = datetime.fromisoformat(entry["timestamp"])
            if entry_dt < before:
                removed += 1
            else:
                retained.append(entry)

        _audit_log.extend(retained)
        return removed


# Patterns that indicate a tool may have side effects (for auto-discovered tools).
_DESTRUCTIVE_PATTERNS: frozenset[str] = frozenset(
    {
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
        "revoke",
        "reset",
        "clear",
        "kill",
        "terminate",
    }
)


# Trust Escalation Hooks
_on_trust_change: Callable[[TrustLevel, TrustLevel], None] | None = None


def set_trust_change_callback(
    callback: Callable[[TrustLevel, TrustLevel], None] | None,
) -> None:
    """Set a callback to be invoked when global trust level changes."""
    global _on_trust_change
    _on_trust_change = callback


def _trigger_trust_change(old_level: TrustLevel, new_level: TrustLevel) -> None:
    """Invoke callback and emit event on trust change."""
    if old_level == new_level:
        return

    if _on_trust_change:
        try:
            _on_trust_change(old_level, new_level)
        except (TypeError, RuntimeError) as e:
            logging.getLogger(__name__).error(f"Trust change callback failed: {e}")

    # Emit trust level change via EventBus
    try:
        from codomyrmex.events import publish_event
        from codomyrmex.events.core.event_schema import Event, EventType

        event = Event(
            event_type=EventType.TRUST_LEVEL_CHANGED,
            source="trust_gateway",
            data={
                "old_level": old_level.name,
                "new_level": new_level.name,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )
        publish_event(event)
        logger.debug(
            "Trust level change emitted: %s -> %s", old_level.name, new_level.name
        )
    except ImportError:
        logger.warning("EventBus not available; trust level change event not emitted")
    except (RuntimeError, AttributeError) as e:
        logger.warning("Failed to emit trust level change event: %s", e)


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


def __getattr__(name: str):
    """Lazy module-level accessors — computed on first access and cached."""
    if name == "SAFE_TOOLS":
        val: frozenset[str] = _get_safe_tools()
        globals()["SAFE_TOOLS"] = val
        return val
    if name == "SAFE_TOOL_COUNT":
        cached = globals().get("SAFE_TOOLS")
        val_i: int = len(cached if cached is not None else _get_safe_tools())
        globals()["SAFE_TOOL_COUNT"] = val_i
        return val_i
    if name == "DESTRUCTIVE_TOOL_COUNT":
        val_d: int = len(_get_destructive_tools())
        globals()["DESTRUCTIVE_TOOL_COUNT"] = val_d
        return val_d
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


class TrustRegistry:
    """In-memory trust ledger for Codomyrmex MCP tools.

    Thread-safe by design (single-process, GIL-protected dict ops).
    """

    def __init__(self) -> None:
        self._ledger_path = Path.home() / ".codomyrmex" / "trust_ledger.json"
        self._disk_loaded: bool = False

        # Initialize default state with ALL known tools (static + dynamic)
        registry = get_tool_registry()
        all_tool_names = registry.list_tools()

        self._levels: dict[str, TrustLevel] = {}
        for name in all_tool_names:
            self._levels[name] = TrustLevel.UNTRUSTED

        # Load persisted state if available
        self._load()

    def _load(self) -> None:
        """Load trust state from disk (skipped if already loaded this process)."""
        if getattr(self, "_disk_loaded", False):
            return
        if not self._ledger_path.exists():
            self._disk_loaded = True
            return

        try:
            data = json.loads(self._ledger_path.read_text())
            for name, level_val in data.items():
                if name in self._levels:
                    try:
                        self._levels[name] = TrustLevel(level_val)
                    except ValueError as e:
                        logger.warning(
                            "Invalid trust level %r for %r in ledger, skipping: %s",
                            level_val,
                            name,
                            e,
                        )
        except (json.JSONDecodeError, OSError, KeyError) as e:
            logger.warning(f"Failed to load trust ledger: {e}")
        self._disk_loaded = True
        # One-time migration: restrict existing file permissions
        try:
            current_mode = self._ledger_path.stat().st_mode & 0o777
            if current_mode != 0o600:
                self._ledger_path.chmod(0o600)
        except OSError:
            pass

    def _save(self) -> None:
        """Save trust state to disk (atomic write + restricted permissions)."""
        try:
            self._ledger_path.parent.mkdir(parents=True, exist_ok=True)
            data = {name: lvl.value for name, lvl in self._levels.items()}
            tmp_path = self._ledger_path.with_suffix(".tmp")
            tmp_path.write_text(json.dumps(data, indent=2))
            tmp_path.chmod(0o600)  # set before rename — avoids brief readable window
            tmp_path.rename(self._ledger_path)
            self._disk_loaded = True  # cache is now consistent with disk
        except OSError as e:
            logger.error(f"Failed to save trust ledger: {e}")

    # ── Queries ───────────────────────────────────────────────────

    def level(self, tool_name: str) -> TrustLevel:
        """Get the current trust level for *tool_name*.

        Uses in-memory cache (populated on init and kept consistent via
        write-through in ``_save``), avoiding disk I/O on every call.
        """
        if not getattr(self, "_disk_loaded", False):
            self._load()
        return self._levels.get(tool_name, TrustLevel.UNTRUSTED)

    # ── Mutations ─────────────────────────────────────────────────

    def verify_all_safe(self) -> list[str]:
        """Promote all safe (read-only) tools to VERIFIED. Return promoted names."""
        promoted = []
        for name in _get_safe_tools():
            if name in self._levels and self._levels[name] == TrustLevel.UNTRUSTED:
                self._levels[name] = TrustLevel.VERIFIED
                promoted.append(name)

        if promoted:
            self._save()

        return sorted(promoted)

    def trust_tool(self, tool_name: str) -> TrustLevel:
        """Promote *tool_name* to TRUSTED."""
        if tool_name not in self._levels:
            raise KeyError(
                f"Unknown tool: {tool_name!r}. Available: {sorted(self._levels.keys())}"
            )
        old_level = self._levels[tool_name]
        self._levels[tool_name] = TrustLevel.TRUSTED
        self._save()
        logger.info("Tool %s promoted to TRUSTED", tool_name)
        _trigger_trust_change(old_level, TrustLevel.TRUSTED)
        return TrustLevel.TRUSTED

    def trust_all(self) -> list[str]:
        """Promote **all** tools to TRUSTED. Return promoted names."""
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

    def get_aggregate_level(self) -> str:
        """Highest trust level present across all tools; 'untrusted' if nothing promoted."""
        levels = set(self._levels.values())
        if TrustLevel.TRUSTED in levels:
            return "trusted"
        if TrustLevel.VERIFIED in levels:
            return "verified"
        return "untrusted"

    def get_audit_count(self) -> int:
        """Number of audit log entries recorded this session."""
        return len(_audit_log)

    def call(self, name: str, **kwargs: Any) -> dict[str, Any]:
        """Execute a tool by name via the tool registry.

        Args:
            name: Fully-qualified tool name.
            **kwargs: Tool arguments.

        Returns:
            Tool result dictionary.

        Raises:
            KeyError: If the tool is not registered.
        """
        registry = get_tool_registry()
        tool = registry.get(name)
        if tool is None:
            raise KeyError(f"Unknown tool: {name!r}")
        handler = tool.get("handler")
        if handler is None:
            raise KeyError(f"Tool {name!r} has no handler")
        result = handler(**kwargs)
        if isinstance(result, dict):
            return result
        return {"result": result}

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
    # Ensures detailed tool stats, including versions and availability
    # Refresh discovery first just in case
    discover_dynamic_tools()

    registry = get_tool_registry()
    tool_names = sorted(registry.list_tools())

    # Calculate tool categorization stats
    safe_tools = _get_safe_tools()
    destructive_tools = _get_destructive_tools()
    by_category = {
        "safe": len(safe_tools),
        "destructive": len(destructive_tools),
        "total": len(tool_names),
    }

    # ── Module Stats ──────────────────────────────────────────────
    # We check discovery metrics for failed modules
    failed_modules = []
    discovery_cache_age = -1.0
    discovery_last_duration = 0.0
    try:
        from codomyrmex.agents.pai.mcp_bridge import get_discovery_metrics

        discovery_metrics = get_discovery_metrics()
        if discovery_metrics is not None:
            failed_modules = [
                {"name": m, "error": "Import failed"}
                for m in discovery_metrics["failed_modules"]
            ]
            last_scan = discovery_metrics["last_scan_time"]
            discovery_cache_age = (
                (datetime.now(UTC) - last_scan).total_seconds() if last_scan else -1.0
            )
            discovery_last_duration = discovery_metrics["scan_duration_ms"]
    except ImportError as e:
        logger.warning("Discovery metrics import failed during health check: %s", e)

    # ── MCP server health ─────────────────────────────────────────
    try:
        # We don't want to create a full server every time if we can avoid it,
        # but it's the robust check.
        server = create_codomyrmex_mcp_server()
        mcp_transport = "stdio/http"  # Configurable, but default
        mcp_resources = len(getattr(server, "_resources", {}))
        mcp_prompts = len(getattr(server, "_prompts", {}))
        server_config = getattr(server, "config", None)
        mcp_server_name = (
            getattr(server_config, "name", "unknown") if server_config else "unknown"
        )
    except (ImportError, TypeError):
        mcp_server_name = "unknown"
        mcp_transport = "unknown"
        mcp_resources = 0
        mcp_prompts = 0

    # ── Validation ────────────────────────────────────────────────

    report = {
        "status": "verified",
        "tools": {
            "safe": sorted(safe_tools),
            "destructive": sorted(destructive_tools),
            "total": len(tool_names),
            "by_category": by_category,
        },
        "modules": {
            "loaded": len(modules),
            "failed": failed_modules,
            "total": len(modules) + len(failed_modules),
        },
        "trust": {
            "promoted_to_verified": promoted,
            "level": _registry.get_aggregate_level(),
            "audit_entries": _registry.get_audit_count(),
            "gateway_healthy": True,
            "report": _registry.get_report(),
        },
        "mcp": {
            "server_name": mcp_server_name,
            "transport": mcp_transport,
            "resources": mcp_resources,
            "prompts": mcp_prompts,
        },
        "discovery": {
            "cache_age_seconds": discovery_cache_age,
            "last_scan_duration_ms": discovery_last_duration,
        },
    }

    logger.info(
        "Verify capabilities: %d tools (%d safe), %d modules loaded.",
        report["tools"]["total"],
        report["tools"]["by_category"]["safe"],
        report["modules"]["loaded"],
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
    old_level = TrustLevel(_registry.get_aggregate_level())
    promoted = _registry.trust_all()
    _trigger_trust_change(old_level, TrustLevel.TRUSTED)

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
    Validates arguments against schema **before** checking trust or executing.

    Args:
        name: Tool name (e.g. ``"codomyrmex.list_modules"``).
        **kwargs: Tool arguments.

    Returns:
        Tool result dictionary.

    Raises:
        PermissionError: If the tool's trust level is insufficient.
        KeyError: If the tool is unknown.
        jsonschema.ValidationError: If arguments match schema.
    """
    # Validate tool exists first (raises KeyError for unknown tools).
    registry = get_tool_registry()
    known_tools = set(registry.list_tools())
    if name not in known_tools:
        raise KeyError(f"Unknown tool: {name!r}. Available: {sorted(known_tools)}")

    # Validation Step (Secure by default)
    # We must validate before we even check trust, to catch malformed attacks early.
    tool_entry = registry.get(name)
    if tool_entry and "schema" in tool_entry:
        val_result = validate_tool_arguments(name, kwargs, tool_entry["schema"])
        if not val_result.valid:
            raise ValueError(f"Tool argument validation failed: {val_result.errors}")

    # Trust check: safe tools need VERIFIED, destructive tools need TRUSTED
    current_level = _registry.level(name)
    if _is_destructive(name):
        if not _registry.is_trusted(name):
            _log_audit_entry(name, kwargs, "blocked", current_level.name, 0.0)
            raise SecurityError(
                f"Tool '{name}' is not trusted (current level: {current_level.name}). "
                "Use trust_tool() or trust_all() to approve."
            )
    elif not _registry.is_at_least_verified(name):
        _log_audit_entry(name, kwargs, "blocked", current_level.name, 0.0)
        raise SecurityError(
            f"Tool '{name}' is not trusted (current level: {current_level.name}). "
            "Use trust_tool() or trust_all() to approve."
        )

    # Destructive Tool Confirmation
    if _REQUIRE_CONFIRMATION and name in DESTRUCTIVE_TOOLS:
        with _confirmations_lock:
            _cleanup_expired_confirmations_locked()

            # Check for token
            token = kwargs.pop("confirmation_token", None)

            if token:
                # Validate token
                if token not in _pending_confirmations:
                    _log_audit_entry(
                        name,
                        kwargs,
                        "blocked",
                        _registry.level(name).name,
                        0.0,
                        error=SecurityError("Invalid or expired confirmation token"),
                    )
                    raise SecurityError("Invalid or expired confirmation token")

                saved = _pending_confirmations[token]
                if saved["tool_name"] != name:
                    _log_audit_entry(
                        name,
                        kwargs,
                        "blocked",
                        _registry.level(name).name,
                        0.0,
                        error=SecurityError("Token mismatch"),
                    )
                    raise SecurityError("Confirmation token does not match tool")

                # Token valid, proceed. Remove used token.
                del _pending_confirmations[token]

            else:
                # Require confirmation
                import uuid

                new_token = str(uuid.uuid4())
                _pending_confirmations[new_token] = {
                    "timestamp": time.monotonic(),
                    "tool_name": name,
                    "args": kwargs,
                }

                _log_audit_entry(
                    name,
                    kwargs,
                    "pending_confirmation",
                    _registry.level(name).name,
                    0.0,
                )

                return {
                    "confirmation_required": True,
                    "tool_name": name,
                    "args_preview": kwargs,
                    "confirm_token": new_token,
                    "message": f"Destructive tool '{name}' requires confirmation. Call again with 'confirmation_token': '{new_token}'.",
                }

    t0 = time.monotonic()
    status = "success"
    error_obj: Exception | None = None

    try:
        # 3. Execute
        result = _registry.call(name, **kwargs)
        return result
    except Exception as e:
        status = "error"
        error_obj = e
        raise
    finally:
        duration = (time.monotonic() - t0) * 1000
        _log_audit_entry(
            name, kwargs, status, _registry.level(name).name, duration, error_obj
        )


def get_current_trust_level() -> TrustLevel:
    """Return the current global trust level derived from per-tool registry state.

    Derives the level from the registry so that per-tool promotions via
    ``trust_tool()`` are reflected immediately, keeping this function
    consistent with the trust level reported by ``verify_capabilities()``.
    """
    return TrustLevel(_registry.get_aggregate_level())


def reset_trust() -> None:
    """Reset all trust levels to UNTRUSTED."""
    old_level = TrustLevel(_registry.get_aggregate_level())
    _registry.reset()
    _trigger_trust_change(old_level, TrustLevel.UNTRUSTED)


# =====================================================================
# Constants (use the lazy definitions from lines ~198-199)
# =====================================================================


__all__ = [
    "DESTRUCTIVE_TOOLS",
    "DESTRUCTIVE_TOOL_COUNT",
    "SAFE_TOOLS",
    "SAFE_TOOL_COUNT",
    "SecurityError",
    "TrustLevel",
    "TrustRegistry",
    "clear_audit_log",
    "export_audit_log",
    "get_audit_log",
    "get_current_trust_level",
    "get_trust_report",
    "is_trusted",
    "trust_all",
    "trust_tool",
    "trusted_call_tool",
    "verify_capabilities",
]
