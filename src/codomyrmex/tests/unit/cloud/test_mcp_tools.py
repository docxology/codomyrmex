import pytest
from _stubs import Stub

from codomyrmex.cloud.mcp_tools import list_cloud_instances


def test_list_cloud_instances_success(monkeypatch):
    """Test successful listing of cloud instances."""

    # Create a mock instance
    mock_instance_1 = Stub()
    mock_instance_1.id = "inst-1"
    mock_instance_1.name = "web-server"
    mock_instance_1.status = "ACTIVE"
    mock_instance_1.flavor = {"original_name": "g1-small"}

    mock_instance_2 = Stub()
    mock_instance_2.id = "inst-2"
    mock_instance_2.name = "db-server"
    mock_instance_2.status = "STOPPED"
    # Test the fallback flavor case
    mock_instance_2.flavor = "g1-large"

    # Setup the mock client
    mock_client = Stub()
    mock_client.list_instances.return_value = [mock_instance_1, mock_instance_2]

    mock_client_class = Stub()
    mock_client_class.from_env.return_value = mock_client

    monkeypatch.setattr(
        "codomyrmex.cloud.infomaniak.InfomaniakComputeClient.from_env",
        mock_client_class.from_env,
    )

    # Call the tool
    result = list_cloud_instances()

    # Verify calls
    mock_client_class.from_env.assert_called_once()
    mock_client.list_instances.assert_called_once()

    # Verify results
    assert result["status"] == "success"
    assert result["count"] == 2
    assert len(result["instances"]) == 2

    # Check first instance
    assert result["instances"][0]["id"] == "inst-1"
    assert result["instances"][0]["name"] == "web-server"
    assert result["instances"][0]["status"] == "ACTIVE"
    assert result["instances"][0]["flavor"] == "g1-small"

    # Check second instance with fallback flavor
    assert result["instances"][1]["id"] == "inst-2"
    assert result["instances"][1]["flavor"] == "g1-large"


def test_list_cloud_instances_error(monkeypatch):
    """Test error handling in listing cloud instances."""

    # Setup the mock client to raise an exception
    mock_client_class = Stub()
    mock_client_class.from_env.side_effect = Exception("API Error")

    monkeypatch.setattr(
        "codomyrmex.cloud.infomaniak.InfomaniakComputeClient.from_env",
        mock_client_class.from_env,
    )

    # Call the tool
    result = list_cloud_instances()

    # Verify calls
    mock_client_class.from_env.assert_called_once()

    # Verify error result
    assert result["status"] == "error"
    assert "Failed to list instances" in result["message"]
    assert "API Error" in result["message"]
