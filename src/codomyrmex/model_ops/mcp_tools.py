"""MCP tools for the model_ops module.

Exposes output scoring, dataset sanitization, and scorer listing.
All operations are pure Python — no GPU or external model dependencies.
"""

from __future__ import annotations

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs):
        def decorator(fn):
            fn._mcp_tool_meta = kwargs
            return fn
        return decorator


@mcp_tool(
    category="model_ops",
    description=(
        "Score a model output against a reference string using one or more named scorers "
        "(exact_match, contains, length, regex). Returns per-scorer scores 0.0–1.0 and an overall average."
    ),
)
def model_ops_score_output(
    output: str,
    reference: str,
    scorers: list[str] | None = None,
) -> dict:
    """Score output against reference using the requested scorers."""
    from codomyrmex.model_ops import (
        ContainsScorer,
        ExactMatchScorer,
        LengthScorer,
        RegexScorer,
    )

    scorer_map = {
        "exact_match": ExactMatchScorer(),
        "contains": ContainsScorer(),
        "length": LengthScorer(min_length=1, max_length=10000),
        "regex": RegexScorer(),
    }
    requested = scorers if scorers is not None else ["exact_match", "contains"]
    active = {name: scorer_map[name] for name in requested if name in scorer_map}
    results = {name: scorer.score(output, reference) for name, scorer in active.items()}
    overall = sum(results.values()) / len(results) if results else 0.0
    return {"scores": results, "overall": round(overall, 6)}


@mcp_tool(
    category="model_ops",
    description=(
        "Filter a list of dataset entries (dicts with 'prompt'/'completion' keys) by "
        "total content length. Returns only entries whose combined length is within [min_length, max_length]."
    ),
)
def model_ops_sanitize_dataset(
    data: list[dict],
    min_length: int = 1,
    max_length: int = 10000,
) -> list[dict]:
    """Filter dataset entries by content length."""
    from codomyrmex.model_ops import Dataset, DatasetSanitizer

    dataset = Dataset(data=list(data))
    filtered = DatasetSanitizer.filter_by_length(
        dataset, min_length=min_length, max_length=max_length
    )
    return filtered.data


@mcp_tool(
    category="model_ops",
    description="List the available scorer type names for model output evaluation.",
)
def model_ops_list_scorers() -> list[str]:
    """Return supported scorer identifiers."""
    return ["exact_match", "contains", "length", "regex", "composite"]
