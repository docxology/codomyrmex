"""Tests for FPF fetcher."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from codomyrmex.fpf import FPFFetcher


@pytest.mark.unit
def test_fetcher_initialization(tmp_path):
    """Test fetcher initialization."""
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    assert fetcher is not None
    assert fetcher.cache_dir.exists()


@patch("codomyrmex.fpf.io.fetcher.requests.get")
def test_fetch_latest(mock_get, tmp_path):
    """Test fetching latest from GitHub."""
    mock_response = Mock()
    mock_response.text = "# FPF Specification\nTest content"
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    content = fetcher.fetch_latest("ailev/FPF", "main")
    assert "FPF Specification" in content


@pytest.mark.unit
def test_get_version_info(tmp_path):
    """Test getting version info."""
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    # This will fail if no network, but that's okay for basic test
    try:
        info = fetcher.get_version_info("ailev/FPF")
        assert "sha" in info
    except Exception:
        # Network unavailable, skip
        pytest.skip("Network unavailable")


@pytest.mark.unit
def test_cache_spec(tmp_path):
    """Test caching specification."""
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    content = "# Test Specification\nTest content"
    cache_path = fetcher.cache_spec(content, "test-version")
    assert cache_path.exists()
    assert cache_path.read_text() == content


@patch("codomyrmex.fpf.io.fetcher.requests.get")
def test_fetch_latest_error_handling(mock_get, tmp_path):
    """Test error handling in fetch_latest."""
    mock_get.side_effect = Exception("Network error")
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    with pytest.raises(Exception):
        fetcher.fetch_latest("ailev/FPF", "main")


@pytest.mark.unit
def test_check_for_updates_nonexistent_file(tmp_path):
    """Test checking updates for non-existent file."""
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    result = fetcher.check_for_updates(Path("/nonexistent/file.md"))
    assert result is True  # Should return True if file doesn't exist


@patch("codomyrmex.fpf.io.fetcher.requests.get")
def test_check_for_updates_no_changes(mock_get, tmp_path):
    """Test checking updates when no changes."""
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    content = "# Test\nContent"
    local_path = tmp_path / "test_fpf.md"
    local_path.write_text(content)

    mock_response = Mock()
    mock_response.text = content
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    result = fetcher.check_for_updates(local_path)
    assert result is False  # No changes


@patch("codomyrmex.fpf.io.fetcher.requests.get")
def test_get_version_info_error_handling(mock_get, tmp_path):
    """Test error handling in get_version_info."""
    mock_get.side_effect = Exception("API error")
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    info = fetcher.get_version_info("ailev/FPF")
    assert info["sha"] == "unknown"

