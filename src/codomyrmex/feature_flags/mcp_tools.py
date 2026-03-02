"""MCP tools for the feature_flags module.

Exposes feature flag management — create, evaluate, and list flags — via the
PAI MCP bridge using in-process FlagDefinition + FlagEvaluator.
"""

from __future__ import annotations

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs):  # type: ignore[misc]
        def decorator(fn):
            fn._mcp_tool_meta = kwargs
            return fn
        return decorator


# Module-level flag registry — shared across all tool calls within a process session
_flags: dict[str, object] = {}


def _get_evaluator():  # type: ignore[return]
    """Return a shared FlagEvaluator instance."""
    from codomyrmex.feature_flags.evaluation import FlagEvaluator
    return FlagEvaluator()


@mcp_tool(
    category="feature_flags",
    description=(
        "Create or update a feature flag with a key, enabled state, and optional rollout percentage. "
        "Returns the flag definition as a dict."
    ),
)
def flag_create(
    key: str,
    enabled: bool = True,
    percentage: float = 100.0,
) -> dict:
    """Define (or overwrite) a feature flag.

    Args:
        key: Unique flag identifier.
        enabled: Global kill-switch; if ``False`` the flag is always off.
        percentage: Rollout percentage 0.0–100.0 (default 100.0 = fully on).

    Returns:
        Dict with ``key``, ``enabled``, and ``percentage`` keys.
    """
    from codomyrmex.feature_flags.evaluation import FlagDefinition

    flag = FlagDefinition(name=key, enabled=enabled, percentage=percentage)
    _flags[key] = flag
    return {"key": flag.name, "enabled": flag.enabled, "percentage": flag.percentage}


@mcp_tool(
    category="feature_flags",
    description=(
        "Evaluate whether a feature flag is enabled for an optional user ID. "
        "Returns True/False. Unknown flags return False."
    ),
)
def flag_is_enabled(key: str, user_id: str = "") -> bool:
    """Check if flag *key* is enabled for *user_id*.

    Args:
        key: Flag identifier to evaluate.
        user_id: Optional user/session identifier for percentage rollout (default ``""``).

    Returns:
        ``True`` if the flag is enabled for this user, ``False`` otherwise.
    """
    from codomyrmex.feature_flags.strategies import EvaluationContext

    flag = _flags.get(key)
    if flag is None:
        return False
    context = EvaluationContext(user_id=user_id or None)
    result = _get_evaluator().evaluate(flag, context)  # type: ignore[arg-type]
    return result.enabled


@mcp_tool(
    category="feature_flags",
    description=(
        "List all feature flags currently defined in this session. "
        "Returns a list of dicts with key, enabled, and percentage."
    ),
)
def flag_list() -> list[dict]:
    """Return all flags registered in the current session.

    Returns:
        List of dicts with ``key``, ``enabled``, and ``percentage`` keys.
    """
    return [
        {"key": f.name, "enabled": f.enabled, "percentage": f.percentage}  # type: ignore[union-attr]
        for f in _flags.values()
    ]
