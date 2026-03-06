"""Unit tests for the config_management MCP tools."""

import os
import tempfile

import pytest

from codomyrmex.config_management import Configuration, ConfigurationManager
from codomyrmex.config_management.mcp_tools import (
    get_config,
    set_config,
    validate_config,
)


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for configuration files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_config_manager(temp_config_dir, monkeypatch):
    """Fixture to set up a ConfigurationManager with a temporary directory."""
    # We use monkeypatch to alter os.getcwd() so the default ConfigurationManager uses our temp_dir
    monkeypatch.chdir(temp_config_dir)
    os.makedirs(os.path.join(temp_config_dir, "config"), exist_ok=True)

    # Initialize the manager
    manager = ConfigurationManager()

    # Save a test configuration
    config = Configuration(data={"database": {"host": "localhost", "port": 5432}})
    manager.configurations["default"] = config
    manager.save_configuration(
        "default", os.path.join(manager.config_dir, "default.yaml")
    )

    return manager


@pytest.mark.unit
def test_get_config_success(mock_config_manager):
    """Test get_config successfully retrieves a value."""
    result = get_config("database.host")

    assert result["status"] == "success"
    assert result["key"] == "database.host"
    assert result["namespace"] == "default"
    assert result["value"] == "localhost"


@pytest.mark.unit
def test_get_config_not_found(mock_config_manager):
    """Test get_config when key is not found."""
    result = get_config("database.username")

    assert result["status"] == "success"
    assert result["key"] == "database.username"
    assert result["value"] is None


@pytest.mark.unit
def test_get_config_error(mock_config_manager):
    """Test get_config handles errors properly without mocking."""
    # We pass an integer where a string is expected to cause an AttributeError in split()
    result = get_config(123)
    assert result["status"] == "error"
    assert "attribute 'split'" in result["message"].lower()


@pytest.mark.unit
def test_set_config_success(mock_config_manager):
    """Test set_config successfully sets and persists a value."""
    result = set_config("database.port", 5433)

    assert result["status"] == "success"
    assert result["key"] == "database.port"
    assert result["updated"] is True

    # Verify it was actually saved
    manager = ConfigurationManager()
    config = manager.load_configuration("default")
    assert config.get_value("database.port") == 5433


@pytest.mark.unit
def test_set_config_error(mock_config_manager):
    """Test set_config handles errors properly without mocking."""
    # Passing a non-string key will cause a split() error
    result = set_config(123, "value")
    assert result["status"] == "error"
    assert "attribute 'split'" in result["message"].lower()


@pytest.mark.unit
def test_validate_config_success(mock_config_manager):
    """Test validate_config returns valid result."""
    result = validate_config()

    assert result["status"] == "success"
    assert result["namespace"] == "default"
    assert result["valid"] is True
    assert result["issues"] == []


@pytest.mark.unit
def test_validate_config_error(mock_config_manager, monkeypatch):
    """Test validate_config handles errors properly without mocking."""
    # To cause validate_config to raise an exception, we monkeypatch the get_configuration method on the manager temporarily
    # Wait, the rule says: "The project's 'zero-mock' policy prohibits mocking core dependencies and application logic"
    # But we can monkeypatch os variables or paths. Instead of mocking the manager, let's pass a bad namespace type.

    # Passing an integer namespace causes string formatting errors during save/load
    result = validate_config(namespace=123)
    assert result["status"] == "error"
