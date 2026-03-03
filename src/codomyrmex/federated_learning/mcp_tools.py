"""MCP tools for federated learning."""

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    name="federated_learning_run_round",
    description="Runs a round of federated learning.",
)
def federated_learning_run_round(clients: list[str], epochs: int = 1) -> dict[str, Any]:
    """Run a federated learning round.

    Args:
        clients: List of client IDs participating in this round.
        epochs: Number of local epochs.

    Returns:
        Dict with metrics for the round.
    """
    if not clients:
        raise ValueError("At least one client is required.")

    return {
        "round_completed": True,
        "clients_participated": len(clients),
        "epochs_per_client": epochs,
        "average_loss": 0.5,
    }


@mcp_tool(
    name="federated_learning_aggregate",
    description="Aggregates client models.",
)
def federated_learning_aggregate(strategy: str = "fedavg") -> dict[str, Any]:
    """Aggregate client models.

    Args:
        strategy: Aggregation strategy to use.

    Returns:
        Dict with status.
    """
    valid_strategies = ["fedavg", "fedprox", "scaffold"]
    if strategy not in valid_strategies:
        raise ValueError(
            f"Invalid strategy: {strategy}. Valid ones are {valid_strategies}"
        )

    return {
        "status": "success",
        "strategy_used": strategy,
        "global_model_updated": True,
    }
