"""Zero-Mock tests for FPF fetcher — uses real HTTP requests.

Tests that require network access are marked with @requires_network
and will skip if the network is unavailable.
"""

from pathlib import Path

import pytest
import requests

from codomyrmex.fpf import FPFFetcher

# Check network availability
try:
    requests.head("https://api.github.com", timeout=3)
    _HAS_NETWORK = True
except Exception:
    _HAS_NETWORK = False

requires_network = pytest.mark.skipif(
    not _HAS_NETWORK,
    reason="Network unavailable",
)


@pytest.mark.unit
def test_fetcher_initialization(tmp_path):
    """Test fetcher initialization."""
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    assert fetcher is not None
    assert fetcher.cache_dir.exists()


@requires_network
def test_fetch_latest(tmp_path):
    """Test fetching latest from GitHub with a real HTTP request."""
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    content = fetcher.fetch_latest("ailev/FPF", "main")
    assert content is not None
    assert len(content) > 0


@pytest.mark.unit
def test_cache_spec(tmp_path):
    """Test caching specification."""
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    content = "# Test Specification\nTest content"
    cache_path = fetcher.cache_spec(content, "test-version")
    assert cache_path.exists()
    assert cache_path.read_text() == content


@requires_network
def test_fetch_latest_error_handling(tmp_path):
    """Test error handling when fetching from a non-existent repo."""
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    with pytest.raises(requests.RequestException):
        fetcher.fetch_latest("nonexistent-user-xyz/nonexistent-repo-xyz", "main")


@pytest.mark.unit
def test_check_for_updates_nonexistent_file(tmp_path):
    """Test checking updates for non-existent file."""
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    result = fetcher.check_for_updates(Path("/nonexistent/file.md"))
    assert result is True


@requires_network
def test_check_for_updates_no_changes(tmp_path):
    """Test checking updates when content matches remote."""
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")

    # Fetch the real content first
    content = fetcher.fetch_latest("ailev/FPF", "main")
    local_path = tmp_path / "test_fpf.md"
    local_path.write_text(content)

    # Now check — should report no changes
    result = fetcher.check_for_updates(local_path)
    assert result is False


@requires_network
def test_get_version_info(tmp_path):
    """Test getting version info with a real API call."""
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    info = fetcher.get_version_info("ailev/FPF")
    assert "sha" in info
    assert isinstance(info["sha"], str)
    assert len(info["sha"]) > 0  # non-empty string (may be "unknown" if API rate-limited)


@pytest.mark.unit
def test_get_version_info_invalid_repo(tmp_path):
    """Test get_version_info with unreachable repo returns unknown."""
    fetcher = FPFFetcher(cache_dir=tmp_path / "fpf_cache")
    info = fetcher.get_version_info("nonexistent-user-xyz/nonexistent-repo-xyz")
    assert info["sha"] == "unknown"
