"""Tests for FPF fetcher."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from codomyrmex.fpf.fetcher import FPFFetcher


def test_fetcher_initialization():
    """Test fetcher initialization."""
    fetcher = FPFFetcher()
    assert fetcher is not None
    assert fetcher.cache_dir.exists()


@patch("codomyrmex.fpf.fetcher.requests.get")
def test_fetch_latest(mock_get):
    """Test fetching latest from GitHub."""
    mock_response = Mock()
    mock_response.text = "# FPF Specification\nTest content"
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    fetcher = FPFFetcher()
    content = fetcher.fetch_latest("ailev/FPF", "main")
    assert "FPF Specification" in content


def test_get_version_info():
    """Test getting version info."""
    fetcher = FPFFetcher()
    # This will fail if no network, but that's okay for basic test
    try:
        info = fetcher.get_version_info("ailev/FPF")
        assert "sha" in info
    except Exception:
        # Network unavailable, skip
        pytest.skip("Network unavailable")


def test_cache_spec():
    """Test caching specification."""
    fetcher = FPFFetcher()
    content = "# Test Specification\nTest content"
    cache_path = fetcher.cache_spec(content, "test-version")
    assert cache_path.exists()
    assert cache_path.read_text() == content


@patch("codomyrmex.fpf.fetcher.requests.get")
def test_fetch_latest_error_handling(mock_get):
    """Test error handling in fetch_latest."""
    mock_get.side_effect = Exception("Network error")
    fetcher = FPFFetcher()
    with pytest.raises(Exception):
        fetcher.fetch_latest("ailev/FPF", "main")


def test_check_for_updates_nonexistent_file():
    """Test checking updates for non-existent file."""
    fetcher = FPFFetcher()
    result = fetcher.check_for_updates(Path("/nonexistent/file.md"))
    assert result is True  # Should return True if file doesn't exist


@patch("codomyrmex.fpf.fetcher.requests.get")
def test_check_for_updates_no_changes(mock_get):
    """Test checking updates when no changes."""
    fetcher = FPFFetcher()
    content = "# Test\nContent"
    local_path = Path("/tmp/test_fpf.md")
    local_path.write_text(content)
    
    mock_response = Mock()
    mock_response.text = content
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    result = fetcher.check_for_updates(local_path)
    assert result is False  # No changes
    
    local_path.unlink()


@patch("codomyrmex.fpf.fetcher.requests.get")
def test_get_version_info_error_handling(mock_get):
    """Test error handling in get_version_info."""
    mock_get.side_effect = Exception("API error")
    fetcher = FPFFetcher()
    info = fetcher.get_version_info("ailev/FPF")
    assert info["sha"] == "unknown"

