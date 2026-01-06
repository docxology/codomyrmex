"""Unit tests for core scraping abstractions."""

import pytest

from codomyrmex.scrape.core import (
    BaseScraper,
    CrawlResult,
    ExtractResult,
    MapResult,
    ScrapeFormat,
    ScrapeOptions,
    ScrapeResult,
    SearchResult,
)


class TestScrapeFormat:
    """Test ScrapeFormat enum."""

    def test_format_values(self):
        """Test that format values are correct."""
        assert ScrapeFormat.MARKDOWN == "markdown"
        assert ScrapeFormat.HTML == "html"
        assert ScrapeFormat.JSON == "json"
        assert ScrapeFormat.LINKS == "links"
        assert ScrapeFormat.SCREENSHOT == "screenshot"
        assert ScrapeFormat.METADATA == "metadata"


class TestScrapeResult:
    """Test ScrapeResult dataclass."""

    def test_basic_creation(self):
        """Test creating a basic ScrapeResult."""
        result = ScrapeResult(url="https://example.com")
        assert result.url == "https://example.com"
        assert result.content == ""
        assert result.success is True
        assert result.error is None

    def test_with_content(self):
        """Test ScrapeResult with content."""
        result = ScrapeResult(
            url="https://example.com",
            content="Test content",
            status_code=200,
        )
        assert result.content == "Test content"
        assert result.status_code == 200

    def test_get_format(self):
        """Test get_format method."""
        result = ScrapeResult(
            url="https://example.com",
            formats={"markdown": "md content", "html": "<html>content</html>"},
        )
        assert result.get_format(ScrapeFormat.MARKDOWN) == "md content"
        assert result.get_format("html") == "<html>content</html>"
        assert result.get_format("json") is None

    def test_has_format(self):
        """Test has_format method."""
        result = ScrapeResult(
            url="https://example.com",
            formats={"markdown": "content"},
        )
        assert result.has_format(ScrapeFormat.MARKDOWN) is True
        assert result.has_format("html") is False


class TestScrapeOptions:
    """Test ScrapeOptions dataclass."""

    def test_default_options(self):
        """Test default ScrapeOptions."""
        options = ScrapeOptions()
        assert ScrapeFormat.MARKDOWN in options.formats
        assert options.timeout is None
        assert options.follow_links is True
        assert options.respect_robots_txt is True

    def test_custom_options(self):
        """Test custom ScrapeOptions."""
        options = ScrapeOptions(
            formats=[ScrapeFormat.MARKDOWN, ScrapeFormat.HTML],
            timeout=60.0,
            limit=10,
            max_depth=2,
        )
        assert len(options.formats) == 2
        assert options.timeout == 60.0
        assert options.limit == 10
        assert options.max_depth == 2

    def test_to_dict(self):
        """Test to_dict method."""
        options = ScrapeOptions(
            formats=[ScrapeFormat.MARKDOWN],
            timeout=30.0,
            limit=5,
        )
        result = options.to_dict()
        assert "formats" in result
        assert result["timeout"] == 30.0
        assert result["limit"] == 5


class TestCrawlResult:
    """Test CrawlResult dataclass."""

    def test_basic_creation(self):
        """Test creating a basic CrawlResult."""
        result = CrawlResult(job_id="test-123", status="pending")
        assert result.job_id == "test-123"
        assert result.status == "pending"
        assert result.total == 0
        assert len(result.results) == 0


class TestMapResult:
    """Test MapResult dataclass."""

    def test_basic_creation(self):
        """Test creating a basic MapResult."""
        result = MapResult()
        assert len(result.links) == 0
        assert result.total == 0

    def test_with_links(self):
        """Test MapResult with links."""
        links = [
            {"url": "https://example.com/page1", "title": "Page 1"},
            {"url": "https://example.com/page2", "title": "Page 2"},
        ]
        result = MapResult(links=links)
        assert len(result.links) == 2
        assert result.total == 2


class TestSearchResult:
    """Test SearchResult dataclass."""

    def test_basic_creation(self):
        """Test creating a basic SearchResult."""
        result = SearchResult(query="test query")
        assert result.query == "test query"
        assert len(result.results) == 0
        assert result.total == 0


class TestExtractResult:
    """Test ExtractResult dataclass."""

    def test_basic_creation(self):
        """Test creating a basic ExtractResult."""
        result = ExtractResult()
        assert result.status == "completed"
        assert len(result.data) == 0
        assert len(result.urls) == 0


class TestBaseScraper:
    """Test BaseScraper abstract class."""

    def test_is_abstract(self):
        """Test that BaseScraper cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseScraper()  # type: ignore

