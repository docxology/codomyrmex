"""Zero-mock unit tests for federated learning MCP tools."""

import pytest

from codomyrmex.federated_learning.mcp_tools import (
    federated_learning_aggregate,
    federated_learning_run_round,
)


@pytest.mark.unit
def test_federated_learning_run_round_success() -> None:
    """Test successful federated learning round."""
    clients = ["client_1", "client_2"]
    result = federated_learning_run_round(clients=clients, epochs=2)

    assert isinstance(result, dict)
    assert result["round_completed"] is True
    assert result["clients_participated"] == 2
    assert result["epochs_per_client"] == 2


@pytest.mark.unit
def test_federated_learning_run_round_no_clients() -> None:
    """Test federated learning round with no clients fails."""
    with pytest.raises(ValueError, match="At least one client is required"):
        federated_learning_run_round(clients=[])


@pytest.mark.unit
def test_federated_learning_aggregate_success() -> None:
    """Test successful model aggregation."""
    result = federated_learning_aggregate(strategy="fedprox")

    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert result["strategy_used"] == "fedprox"
    assert result["global_model_updated"] is True


@pytest.mark.unit
def test_federated_learning_aggregate_default() -> None:
    """Test successful model aggregation with default strategy."""
    result = federated_learning_aggregate()

    assert isinstance(result, dict)
    assert result["strategy_used"] == "fedavg"


@pytest.mark.unit
def test_federated_learning_aggregate_invalid_strategy() -> None:
    """Test aggregation fails with invalid strategy."""
    with pytest.raises(ValueError, match="Invalid strategy"):
        federated_learning_aggregate(strategy="invalid_strat")
