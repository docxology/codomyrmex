"""MCP tool definitions for the relations module.

Exposes relationship strength scoring and social graph analysis
as MCP tools for agent consumption.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func
        return decorator


@mcp_tool(
    category="relations",
    description="Score the relationship strength between two entities based on interactions.",
)
def relations_score_strength(
    source: str,
    target: str,
    interactions: list[dict[str, Any]],
    decay_function: str = "exponential",
    half_life_days: float = 30.0,
) -> dict[str, Any]:
    """Score a pairwise relationship from interaction history.

    Args:
        source: First entity ID.
        target: Second entity ID.
        interactions: List of dicts with keys: type, timestamp, weight (optional).
        decay_function: One of: exponential, linear, step, none.
        half_life_days: Half-life in days for exponential decay.
    """
    try:
        import time
        from codomyrmex.relations.strength_scoring import (
            Interaction, RelationStrengthScorer, StrengthConfig, DecayFunction,
        )
        decay = DecayFunction(decay_function)
        config = StrengthConfig(decay_function=decay, half_life=half_life_days * 86400)
        scorer = RelationStrengthScorer(config=config)
        for ix in interactions:
            scorer.add_interaction(Interaction(
                source=source, target=target,
                interaction_type=ix.get("type", "generic"),
                timestamp=ix.get("timestamp", time.time()),
                weight=ix.get("weight", 1.0),
            ))
        score = scorer.score(source, target, now=time.time())
        return {
            "status": "ok",
            "source": source,
            "target": target,
            "raw_score": score.raw_score,
            "interaction_count": score.interaction_count,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
