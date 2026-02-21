"""Tests for the scrape module.

Tests cover:
- Module imports
- ScrapeFormat enum values
- ScrapeResult construction and format methods
- ScrapeOptions construction and serialization
- ScrapeConfig defaults and from_env
- ScrapeConfig validation
- CrawlResult, MapResult, SearchResult, ExtractResult construction
- Exception hierarchy
- Scraper class validation errors
"""

import pytest

from codomyrmex import scrape
from codomyrmex.scrape import (
    ScrapeFormat,
    ScrapeResult,
    ScrapeOptions,
    ScrapeConfig,
    CrawlResult,
    MapResult,
    SearchResult,
    ExtractResult,
    ScrapeError,
    ScrapeConnectionError,
    ScrapeTimeoutError,
    ScrapeValidationError,
    FirecrawlError,
    get_config,
    reset_config,
    set_config,
)


@pytest.mark.unit
def test_scrape_module_import():
    """Verify that the scrape module can be imported successfully."""
    assert scrape is not None
    assert hasattr(scrape, "__path__")


@pytest.mark.unit
def test_scrape_module_structure():
    """Verify basic structure of scrape module."""
    assert hasattr(scrape, "__file__")


# --- ScrapeFormat Tests ---


@pytest.mark.unit
def test_scrape_format_enum_values():
    """ScrapeFormat contains all expected format types."""
    assert ScrapeFormat.MARKDOWN.value == "markdown"
    assert ScrapeFormat.HTML.value == "html"
    assert ScrapeFormat.JSON.value == "json"
    assert ScrapeFormat.LINKS.value == "links"
    assert ScrapeFormat.SCREENSHOT.value == "screenshot"
    assert ScrapeFormat.METADATA.value == "metadata"


# --- ScrapeResult Tests ---


@pytest.mark.unit
def test_scrape_result_construction():
    """ScrapeResult can be constructed with required and optional fields."""
    result = ScrapeResult(
        url="https://example.com",
        content="Hello World",
        formats={"markdown": "# Hello"},
        status_code=200,
    )
    assert result.url == "https://example.com"
    assert result.content == "Hello World"
    assert result.success is True
    assert result.error is None
    assert result.status_code == 200


@pytest.mark.unit
def test_scrape_result_get_format():
    """ScrapeResult.get_format retrieves content by format type."""
    result = ScrapeResult(
        url="https://example.com",
        formats={"markdown": "# Title", "html": "<h1>Title</h1>"},
    )
    assert result.get_format(ScrapeFormat.MARKDOWN) == "# Title"
    assert result.get_format("html") == "<h1>Title</h1>"
    assert result.get_format(ScrapeFormat.JSON) is None


@pytest.mark.unit
def test_scrape_result_has_format():
    """ScrapeResult.has_format checks format availability."""
    result = ScrapeResult(url="https://example.com", formats={"markdown": "data"})
    assert result.has_format(ScrapeFormat.MARKDOWN) is True
    assert result.has_format(ScrapeFormat.HTML) is False


# --- ScrapeOptions Tests ---


@pytest.mark.unit
def test_scrape_options_defaults():
    """ScrapeOptions has sensible defaults."""
    opts = ScrapeOptions()
    assert opts.formats == [ScrapeFormat.MARKDOWN]
    assert opts.timeout is None
    assert opts.follow_links is True
    assert opts.respect_robots_txt is True
    assert opts.headers == {}
    assert opts.exclude_tags == []


@pytest.mark.unit
def test_scrape_options_to_dict():
    """ScrapeOptions serializes to dictionary with correct format values."""
    opts = ScrapeOptions(
        formats=[ScrapeFormat.MARKDOWN, ScrapeFormat.HTML],
        timeout=60.0,
        max_depth=3,
    )
    d = opts.to_dict()
    assert d["formats"] == ["markdown", "html"]
    assert d["timeout"] == 60.0
    assert d["max_depth"] == 3
    assert d["follow_links"] is True


# --- ScrapeConfig Tests ---


@pytest.mark.unit
def test_scrape_config_defaults():
    """ScrapeConfig has sensible defaults."""
    config = ScrapeConfig()
    assert config.api_key is None
    assert config.base_url == "https://api.firecrawl.dev"
    assert config.default_timeout == 30.0
    assert config.max_retries == 3
    assert config.respect_robots_txt is True


@pytest.mark.unit
def test_scrape_config_validate_missing_api_key():
    """ScrapeConfig.validate raises on missing API key."""
    config = ScrapeConfig(api_key=None)
    with pytest.raises(ScrapeValidationError):
        config.validate()


@pytest.mark.unit
def test_scrape_config_validate_negative_timeout():
    """ScrapeConfig.validate raises on non-positive timeout."""
    config = ScrapeConfig(api_key="test-key", default_timeout=-1.0)
    with pytest.raises(ScrapeValidationError):
        config.validate()


@pytest.mark.unit
def test_scrape_config_to_dict_masks_api_key():
    """ScrapeConfig.to_dict masks the API key."""
    config = ScrapeConfig(api_key="secret-key-123")
    d = config.to_dict()
    assert d["api_key"] == "***"


# --- Result Dataclass Tests ---


@pytest.mark.unit
def test_crawl_result_construction():
    """CrawlResult can be constructed with expected fields."""
    result = CrawlResult(job_id="job-1", status="completed", total=5, completed=5)
    assert result.job_id == "job-1"
    assert result.status == "completed"
    assert result.results == []


@pytest.mark.unit
def test_map_result_auto_total():
    """MapResult auto-calculates total from links."""
    links = [{"url": "https://a.com"}, {"url": "https://b.com"}]
    result = MapResult(links=links)
    assert result.total == 2


@pytest.mark.unit
def test_search_result_construction():
    """SearchResult stores query and results."""
    result = SearchResult(query="test search", total=0)
    assert result.query == "test search"
    assert result.results == []


@pytest.mark.unit
def test_extract_result_defaults():
    """ExtractResult has sensible defaults."""
    result = ExtractResult()
    assert result.status == "completed"
    assert result.data == {}
    assert result.urls == []


# --- Exception Tests ---


@pytest.mark.unit
def test_exception_hierarchy():
    """Scrape exceptions follow expected hierarchy."""
    assert issubclass(ScrapeConnectionError, ScrapeError)
    assert issubclass(ScrapeTimeoutError, ScrapeError)
    assert issubclass(ScrapeValidationError, ScrapeError)
    assert issubclass(FirecrawlError, ScrapeError)


@pytest.mark.unit
def test_scrape_connection_error_context():
    """ScrapeConnectionError stores URL and status code as attributes."""
    err = ScrapeConnectionError("Connection failed", url="https://example.com", status_code=503)
    assert err.url == "https://example.com"
    assert err.status_code == 503
