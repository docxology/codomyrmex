"""
MCP tools for the nas (Neural Architecture Search) module.

Exposes architecture search and sampling capabilities through the
Model Context Protocol.
"""

from __future__ import annotations

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .search import NASSearcher, NASSearchSpace, size_heuristic_eval


@mcp_tool(category="nas")
def nas_sample_architecture(seed: int = None) -> dict:
    """Sample a random architecture from the default search space.

    Args:
        seed: Optional random seed for reproducibility

    Returns:
        dict with keys: n_layers, d_model, n_heads, d_ff, dropout,
        activation, total_params_estimate
    """
    space = NASSearchSpace()
    config = space.sample(seed=seed)
    return {
        "n_layers": config.n_layers,
        "d_model": config.d_model,
        "n_heads": config.n_heads,
        "d_ff": config.d_ff,
        "dropout": config.dropout,
        "activation": config.activation,
        "total_params_estimate": config.total_params_estimate,
    }


@mcp_tool(category="nas")
def nas_random_search(n_trials: int = 20, seed: int = 42) -> dict:
    """Run random NAS with a size-based evaluation heuristic.

    Args:
        n_trials: Number of random architectures to evaluate
        seed: Random seed for reproducibility

    Returns:
        dict with keys: best_config (dict), best_score (float),
        total_evaluated (int)
    """
    space = NASSearchSpace()
    searcher = NASSearcher(space, size_heuristic_eval)
    best = searcher.random_search(n_trials=n_trials, seed=seed)
    _, best_score = searcher.best()

    return {
        "best_config": {
            "n_layers": best.n_layers,
            "d_model": best.d_model,
            "n_heads": best.n_heads,
            "d_ff": best.d_ff,
            "dropout": best.dropout,
            "activation": best.activation,
        },
        "best_score": round(best_score, 4),
        "total_evaluated": len(searcher.history),
    }
