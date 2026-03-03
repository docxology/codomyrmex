"""Unit tests for data lineage MCP tools."""

import pytest

from codomyrmex.data_lineage import mcp_tools


@pytest.fixture(autouse=True)
def reset_global_lineage():
    """Reset the global lineage tracker before each test."""
    mcp_tools._GLOBAL_LINEAGE = None
    yield
    mcp_tools._GLOBAL_LINEAGE = None


@pytest.mark.unit
def test_data_lineage_track_event_dataset():
    """Test tracking a dataset event."""
    result = mcp_tools.data_lineage_track_event(
        event_type="dataset",
        event_id="raw_data",
        name="Raw Logs",
        location="s3://logs",
    )

    assert result["id"] == "raw_data"
    assert result["name"] == "Raw Logs"
    assert result["type"] == "dataset"
    assert result["metadata"]["location"] == "s3://logs"


@pytest.mark.unit
def test_data_lineage_track_event_transformation():
    """Test tracking a transformation event."""
    # Track input dataset
    mcp_tools.data_lineage_track_event(
        event_type="dataset",
        event_id="raw_data",
        name="Raw Logs",
    )

    # Track transformation
    result = mcp_tools.data_lineage_track_event(
        event_type="transformation",
        event_id="clean_logs",
        name="Clean Logs Job",
        inputs=["raw_data"],
        outputs=["clean_data"],
    )

    assert result["id"] == "clean_logs"
    assert result["name"] == "Clean Logs Job"
    assert result["type"] == "transformation"


@pytest.mark.unit
def test_data_lineage_track_event_invalid_type():
    """Test tracking an event with invalid type raises ValueError."""
    with pytest.raises(ValueError, match="Unknown event type: invalid"):
        mcp_tools.data_lineage_track_event(
            event_type="invalid",
            event_id="test_id",
            name="test_name",
        )


@pytest.mark.unit
def test_data_lineage_analyze_impact():
    """Test analyzing downstream impact."""
    # Build lineage
    mcp_tools.data_lineage_track_event("dataset", "src_data", "Source Data")
    mcp_tools.data_lineage_track_event(
        "transformation",
        "transform",
        "Transform",
        inputs=["src_data"],
        outputs=["dest_data"]
    )

    # Analyze impact
    impact = mcp_tools.data_lineage_analyze_impact("src_data")

    assert impact["source_node"] == "src_data"
    assert impact["total_affected"] == 2
    assert "transform" in impact["affected_transformations"]
    assert "dest_data" in impact["affected_datasets"]


@pytest.mark.unit
def test_data_lineage_get_origin():
    """Test getting origins of a node."""
    # Build lineage
    mcp_tools.data_lineage_track_event("dataset", "source1", "Source 1")
    mcp_tools.data_lineage_track_event("dataset", "source2", "Source 2")
    mcp_tools.data_lineage_track_event(
        "transformation",
        "join_sources",
        "Join Sources",
        inputs=["source1", "source2"],
        outputs=["joined_data"]
    )

    # Get origins
    origins = mcp_tools.data_lineage_get_origin("joined_data")

    assert len(origins) == 2
    origin_ids = {n["id"] for n in origins}
    assert "source1" in origin_ids
    assert "source2" in origin_ids
