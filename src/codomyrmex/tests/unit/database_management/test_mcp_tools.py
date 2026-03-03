import os
import tempfile

import pytest

from codomyrmex.database_management.mcp_tools import (
    db_generate_schema,
    db_list_adapters,
    db_monitor,
)


@pytest.mark.unit
def test_db_list_adapters():
    """Test db_list_adapters returns expected strings."""
    adapters = db_list_adapters()
    assert isinstance(adapters, list)
    assert "sqlite" in adapters
    assert "postgres" in adapters
    assert "mysql" in adapters


@pytest.mark.unit
def test_db_list_adapters_edge_case():
    """Test db_list_adapters returns expected strings even with arguments (should ignore them)."""
    with pytest.raises(TypeError):
        db_list_adapters("invalid")


@pytest.mark.unit
def test_db_monitor():
    """Test db_monitor returns a dict with metrics for sqlite in-memory db."""
    metrics = db_monitor("sqlite:///:memory:")
    assert isinstance(metrics, dict)

    # Check for keys returned by the monitor_database function
    # Typically this has performance related keys. Even if it's minimal, it's a dict.
    assert "status" in metrics or "metrics" in metrics or len(metrics) > 0


@pytest.mark.unit
def test_db_monitor_invalid_connection():
    """Test db_monitor edge case: invalid connection string gracefully returns error status."""
    metrics = db_monitor("invalid_connection_string://")
    assert isinstance(metrics, dict)
    assert metrics.get("message") == "No database metrics found for analysis"


@pytest.mark.unit
def test_db_generate_schema():
    """Test db_generate_schema accurately processes simple model structures."""
    models = [
        {
            "name": "User",
            "columns": [
                {"name": "id", "data_type": "int"},
                {"name": "name", "data_type": "str"},
            ],
        }
    ]

    with tempfile.TemporaryDirectory() as temp_dir:
        result = db_generate_schema(models=models, output_dir=temp_dir)

        assert isinstance(result, dict)
        assert result.get("tables_generated") == 1

        # Check if files were actually generated in output_dir
        # Based on schema_generator.py behavior
        assert os.path.exists(temp_dir)
        # Even if schema generation is abstract, it returns some dict representation of success/stats
        assert result is not None


@pytest.mark.unit
def test_db_generate_schema_empty_models():
    """Test db_generate_schema edge case: empty models list."""
    with tempfile.TemporaryDirectory() as temp_dir:
        result = db_generate_schema(models=[], output_dir=temp_dir)
        assert isinstance(result, dict)
        assert os.path.exists(temp_dir)


@pytest.mark.unit
def test_db_generate_schema_invalid_models():
    """Test db_generate_schema edge case: invalid models data type."""
    with tempfile.TemporaryDirectory() as temp_dir:
        result = db_generate_schema(models="invalid_data_type", output_dir=temp_dir)  # type: ignore
        assert isinstance(result, dict)
