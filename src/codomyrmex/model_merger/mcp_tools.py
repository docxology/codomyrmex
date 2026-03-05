"""MCP tool definitions for the model_merger module."""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="model_merger",
    description="Merge two model parameter sets using SLERP or linear interpolation.",
)
def merge_models(
    params_a: dict[str, list],
    params_b: dict[str, list],
    method: str = "slerp",
    alpha: float = 0.5,
) -> dict[str, Any]:
    """Merge two models by interpolating their parameters.

    Args:
        params_a: First model parameters (key -> list of floats).
        params_b: Second model parameters (key -> list of floats).
        method: Merge method ('slerp' or 'linear').
        alpha: Interpolation weight in [0, 1]. 0=model A, 1=model B.

    Returns:
        Dictionary with merged parameter keys and shapes.
    """
    try:
        import numpy as np

        from .merger import ModelMerger

        np_a = {k: np.array(v) for k, v in params_a.items()}
        np_b = {k: np.array(v) for k, v in params_b.items()}

        merger = ModelMerger(method=method)
        merged = merger.merge(np_a, np_b, alpha=alpha)

        return {
            "status": "success",
            "method": method,
            "alpha": alpha,
            "keys": list(merged.keys()),
            "shapes": {k: list(v.shape) for k, v in merged.items()},
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(
    category="model_merger",
    description="Create a model soup by averaging multiple model parameter sets.",
)
def create_model_soup(
    param_dicts: list[dict[str, list]],
    weights: list[float] = None,
) -> dict[str, Any]:
    """Average multiple models into a model soup.

    Args:
        param_dicts: List of model parameter dictionaries (key -> list of floats).
        weights: Optional weighting for each model (uniform if omitted).

    Returns:
        Dictionary with result parameter keys and shapes.
    """
    try:
        import numpy as np

        from .merger import model_soup

        np_dicts = [{k: np.array(v) for k, v in d.items()} for d in param_dicts]

        result = model_soup(np_dicts, weights=weights)

        return {
            "status": "success",
            "n_models": len(param_dicts),
            "keys": list(result.keys()),
            "shapes": {k: list(v.shape) for k, v in result.items()},
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
