"""Tests for the preprocessing MCP tools."""

from codomyrmex.preprocessing.mcp_tools import preprocess_data


def test_preprocess_data():
    """Test preprocess_data tool."""
    result = preprocess_data("  Hello World  ")
    assert result == {"status": "success", "preprocessed": "hello world"}


def test_preprocess_data_empty():
    """Test preprocess_data tool with empty string."""
    result = preprocess_data("")
    assert result == {"status": "success", "preprocessed": ""}


def test_preprocess_data_non_string_returns_error_status():
    """The spec promises a status dict, not an AttributeError, for bad input."""
    result = preprocess_data(42)  # type: ignore[arg-type]
    assert result == {"status": "error", "message": "data must be a string, got int"}


def test_package_exports_preprocess_data():
    import codomyrmex.preprocessing as pkg

    assert pkg.__all__ == ["preprocess_data"]
    assert pkg.preprocess_data is preprocess_data
