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
    CrawlResult,
    ExtractResult,
    FirecrawlError,
    MapResult,
    ScrapeConfig,
    ScrapeConnectionError,
    ScrapeError,
    ScrapeFormat,
    ScrapeOptions,
    ScrapeResult,
    ScrapeTimeoutError,
    ScrapeValidationError,
    SearchResult,
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


# From test_tier3_promotions.py
class TestCrawler:
    """Tests for Crawler."""

    def test_add_seeds_dedup(self):
        """Test functionality: add seeds dedup."""
        from codomyrmex.scrape.extractors.crawler import CrawlConfig, Crawler
        crawler = Crawler(config=CrawlConfig(max_pages=10))
        added = crawler.add_seeds(["https://example.com", "https://example.com"])
        assert added == 1
        assert crawler.frontier_size == 1

    def test_has_next_respects_max(self):
        """Test functionality: has next respects max."""
        from codomyrmex.scrape.extractors.crawler import (
            CrawlConfig,
            Crawler,
            CrawlResult,
            CrawlStatus,
        )
        crawler = Crawler(config=CrawlConfig(max_pages=1))
        crawler.add_seeds(["https://example.com", "https://example.com/page2"])
        url, depth = crawler.next_url()
        crawler.record_result(CrawlResult(url=url, status=CrawlStatus.SUCCESS, depth=depth))
        assert crawler.has_next() is False

    def test_domain_filtering(self):
        """Test functionality: domain filtering."""
        from codomyrmex.scrape.extractors.crawler import CrawlConfig, Crawler
        crawler = Crawler(config=CrawlConfig(allowed_domains=["example.com"]))
        assert crawler.is_allowed("https://example.com/page") is True
        assert crawler.is_allowed("https://other.com/page") is False


# From test_tier3_promotions_pass2.py
class TestContentExtractor:
    """Tests for ContentExtractor."""

    def test_extract_title(self):
        """Test functionality: extract title."""
        from codomyrmex.scrape.extractors.content_extractor import ContentExtractor
        ext = ContentExtractor()
        result = ext.extract("<html><title>Hello World</title></html>")
        assert result.title == "Hello World"

    def test_extract_headings(self):
        """Test functionality: extract headings."""
        from codomyrmex.scrape.extractors.content_extractor import ContentExtractor
        ext = ContentExtractor()
        html = "<h1>Main</h1><h2>Sub</h2>"
        result = ext.extract(html)
        assert len(result.headings) == 2
        assert result.headings[0] == (1, "Main")

    def test_extract_links(self):
        """Test functionality: extract links."""
        from codomyrmex.scrape.extractors.content_extractor import ContentExtractor
        ext = ContentExtractor(base_url="https://example.com")
        html = '<a href="/page">Link</a>'
        result = ext.extract(html)
        assert len(result.links) == 1
        assert result.links[0][0] == "https://example.com/page"

    def test_text_similarity(self):
        """Test functionality: text similarity."""
        from codomyrmex.scrape.extractors.content_extractor import text_similarity
        assert text_similarity("hello world", "hello world") == 1.0
        assert text_similarity("hello", "goodbye") == 0.0


# Phase 2b — scrape/core
class TestScrapeDataclasses:
    """Tests for scrape dataclasses and enums."""

    def test_scrape_format_enum(self):
        from codomyrmex.scrape.core import ScrapeFormat
        assert len(list(ScrapeFormat)) > 0

    def test_scrape_options_defaults(self):
        from codomyrmex.scrape.core import ScrapeOptions
        opts = ScrapeOptions()
        assert opts.follow_links is True
        assert opts.respect_robots_txt is True

    def test_scrape_options_to_dict(self):
        from codomyrmex.scrape.core import ScrapeFormat, ScrapeOptions
        opts = ScrapeOptions(formats=[ScrapeFormat.MARKDOWN], timeout=30.0)
        d = opts.to_dict()
        assert isinstance(d, dict)

    def test_scrape_result_creation(self):
        from codomyrmex.scrape.core import ScrapeResult
        r = ScrapeResult(url="https://example.com", content="Hello", status_code=200)
        assert r.url == "https://example.com"
        assert r.success is True

    def test_scrape_result_has_format(self):
        from codomyrmex.scrape.core import ScrapeResult
        r = ScrapeResult(url="https://ex.com", formats={"markdown": "# Title"})
        assert r.has_format("markdown") is True
        assert r.has_format("html") is False

    def test_scrape_result_get_format(self):
        from codomyrmex.scrape.core import ScrapeResult
        r = ScrapeResult(url="https://ex.com", formats={"markdown": "# Title"})
        assert r.get_format("markdown") == "# Title"
        assert r.get_format("html") is None

    def test_crawl_result(self):
        from codomyrmex.scrape.core import CrawlResult
        cr = CrawlResult(job_id="job1", status="completed", total=10, completed=10)
        assert cr.total == 10
        assert cr.credits_used == 0

    def test_extract_result(self):
        from codomyrmex.scrape.core import ExtractResult
        er = ExtractResult(data={"key": "value"}, urls=["https://ex.com"])
        assert er.status == "completed"

    def test_map_result(self):
        from codomyrmex.scrape.core import MapResult
        mr = MapResult(links=[{"url": "https://ex.com", "title": "Ex"}], total=1)
        assert mr.total == 1

    def test_search_result(self):
        from codomyrmex.scrape.core import SearchResult
        sr = SearchResult(query="python scraping")
        assert sr.query == "python scraping"
        assert sr.total == 0
