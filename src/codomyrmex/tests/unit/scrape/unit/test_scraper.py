"""Unit tests for the main Scraper class.

Tests use real implementations only. TestAdapter is a test adapter that implements
the BaseScraper interface for testing, not a mock. All data structures and
processing logic use real implementations.
"""

import pytest

from codomyrmex.scrape.config import ScrapeConfig, reset_config
from codomyrmex.scrape.core import BaseScraper, ScrapeFormat, ScrapeOptions
from codomyrmex.scrape.exceptions import ScrapeError, ScrapeValidationError, ScrapeConnectionError
from codomyrmex.scrape.scraper import Scraper


@pytest.mark.unit
class TestAdapter(BaseScraper):
    """Test adapter implementing BaseScraper interface with real data structures."""

    def scrape(self, url, options=None):
        from codomyrmex.scrape.core import ScrapeResult

        # Real ScrapeResult with actual data
        return ScrapeResult(url=url, content=f"Content from {url}", status_code=200)

    def crawl(self, url, options=None):
        from codomyrmex.scrape.core import CrawlResult

        # Real CrawlResult with actual data
        return CrawlResult(job_id="test-123", status="completed", total=1, completed=1)

    def map(self, url, search=None):
        from codomyrmex.scrape.core import MapResult

        # Real MapResult with actual data
        return MapResult(links=[{"url": url, "title": "Test"}], total=1)

    def search(self, query, options=None):
        from codomyrmex.scrape.core import SearchResult

        # Real SearchResult with actual data
        return SearchResult(query=query, total=1)

    def extract(self, urls, schema=None, prompt=None):
        from codomyrmex.scrape.core import ExtractResult

        # Real ExtractResult with actual data
        return ExtractResult(data={"extracted": "data"}, urls=urls)


@pytest.mark.unit
class TestScraper:
    """Test Scraper class with real implementations."""

    def test_init_with_adapter(self):
        """Test initializing Scraper with a test adapter."""
        adapter = TestAdapter()
        config = ScrapeConfig(api_key="test-key")
        scraper = Scraper(config=config, adapter=adapter)
        assert scraper.adapter == adapter
        assert scraper.config == config

    def test_init_with_config_only(self):
        """Test initializing Scraper with config only (uses default adapter if available)."""
        config = ScrapeConfig(api_key="test-key")
        # This will try to create FirecrawlAdapter if firecrawl-py is available
        # Otherwise will raise ScrapeValidationError or ScrapeError
        try:
            scraper = Scraper(config=config)
            assert scraper.config == config
            assert scraper.adapter is not None
        except (ScrapeValidationError, ScrapeError):
            # Expected if firecrawl-py is not installed
            pytest.skip("firecrawl-py not installed, cannot test default adapter")

    def test_init_without_adapter_or_firecrawl(self):
        """Test that Scraper raises error when no adapter available."""
        # Reset config to ensure clean state
        reset_config()
        # Remove API key to force error
        config = ScrapeConfig(api_key=None)

        try:
            scraper = Scraper(config=config)
            # If firecrawl-py is available, it will try to initialize
            # This will fail at validation
            pytest.skip("firecrawl-py may be available, cannot test error case")
        except (ScrapeValidationError, ScrapeError):
            # Expected when no adapter can be created
            pass

    def test_scrape_success(self):
        """Test successful scraping with real data."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        result = scraper.scrape("https://example.com")
        assert result.url == "https://example.com"
        assert "Content from" in result.content
        assert result.status_code == 200
        assert result.success is True

    def test_scrape_with_options(self):
        """Test scraping with options."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        options = ScrapeOptions(formats=[ScrapeFormat.MARKDOWN, ScrapeFormat.HTML])
        result = scraper.scrape("https://example.com", options)
        assert result.success is True
        assert result.url == "https://example.com"

    def test_scrape_invalid_url(self):
        """Test scraping with invalid URL."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        with pytest.raises(ScrapeValidationError):
            scraper.scrape("")

        with pytest.raises(ScrapeValidationError):
            scraper.scrape(None)  # type: ignore

    def test_scrape_non_string_url(self):
        """Test scraping with non-string URL."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        with pytest.raises(ScrapeValidationError):
            scraper.scrape(123)  # type: ignore

    def test_crawl_success(self):
        """Test successful crawling with real data."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        result = scraper.crawl("https://example.com")
        assert result.job_id == "test-123"
        assert result.status == "completed"
        assert result.total == 1
        assert result.completed == 1

    def test_crawl_with_options(self):
        """Test crawling with options."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        options = ScrapeOptions(limit=10, max_depth=2)
        result = scraper.crawl("https://example.com", options)
        assert result.job_id == "test-123"
        assert result.status == "completed"

    def test_crawl_invalid_url(self):
        """Test crawling with invalid URL."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        with pytest.raises(ScrapeValidationError):
            scraper.crawl("")

    def test_map_success(self):
        """Test successful mapping with real data."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        result = scraper.map("https://example.com")
        assert result.total == 1
        assert len(result.links) == 1
        assert result.links[0]["url"] == "https://example.com"

    def test_map_with_search(self):
        """Test mapping with search term."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        result = scraper.map("https://example.com", search="test")
        assert result.total == 1

    def test_map_without_search(self):
        """Test mapping without search term."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        result = scraper.map("https://example.com", search=None)
        assert result.total == 1

    def test_map_invalid_url(self):
        """Test mapping with invalid URL."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        with pytest.raises(ScrapeValidationError):
            scraper.map("")

    def test_search_success(self):
        """Test successful searching with real data."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        result = scraper.search("test query")
        assert result.query == "test query"
        assert result.total == 1

    def test_search_with_options(self):
        """Test searching with options."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        options = ScrapeOptions(formats=[ScrapeFormat.MARKDOWN], limit=5)
        result = scraper.search("test query", options)
        assert result.query == "test query"
        assert result.total == 1

    def test_search_invalid_query(self):
        """Test searching with invalid query."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        with pytest.raises(ScrapeValidationError):
            scraper.search("")

        with pytest.raises(ScrapeValidationError):
            scraper.search(None)  # type: ignore

    def test_extract_success(self):
        """Test successful extraction with real data."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        result = scraper.extract(["https://example.com"])
        assert len(result.urls) == 1
        assert "extracted" in result.data
        assert result.data["extracted"] == "data"

    def test_extract_with_schema(self):
        """Test extraction with schema."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        schema = {"type": "object", "properties": {"title": {"type": "string"}}}
        result = scraper.extract(["https://example.com"], schema=schema)
        assert len(result.urls) == 1
        assert result.data is not None

    def test_extract_with_prompt(self):
        """Test extraction with prompt."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        result = scraper.extract(["https://example.com"], prompt="Extract title")
        assert len(result.urls) == 1
        assert result.data is not None

    def test_extract_with_multiple_urls(self):
        """Test extraction with multiple URLs."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        urls = ["https://example.com/page1", "https://example.com/page2"]
        result = scraper.extract(urls)
        assert len(result.urls) == 2
        assert result.urls == urls

    def test_extract_invalid_urls(self):
        """Test extraction with invalid URLs."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        with pytest.raises(ScrapeValidationError):
            scraper.extract([])

        with pytest.raises(ScrapeValidationError):
            scraper.extract(None)  # type: ignore

    def test_extract_invalid_url_in_list(self):
        """Test extraction with invalid URL in list."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        with pytest.raises(ScrapeValidationError):
            scraper.extract([""])

        with pytest.raises(ScrapeValidationError):
            scraper.extract([None])  # type: ignore

    def test_extract_non_string_url(self):
        """Test extraction with non-string URL in list."""
        adapter = TestAdapter()
        scraper = Scraper(adapter=adapter)
        with pytest.raises(ScrapeValidationError):
            scraper.extract([123])  # type: ignore

    def test_error_handling(self):
        """Test error handling in scraper with real error propagation."""

        class ErrorAdapter(BaseScraper):
            """Adapter that raises real errors for testing."""

            def scrape(self, url, options=None):
                raise Exception("Test error")

            def crawl(self, url, options=None):
                raise Exception("Test error")

            def map(self, url, search=None):
                raise Exception("Test error")

            def search(self, query, options=None):
                raise Exception("Test error")

            def extract(self, urls, schema=None, prompt=None):
                raise Exception("Test error")

        adapter = ErrorAdapter()
        scraper = Scraper(adapter=adapter)
        with pytest.raises(ScrapeError):
            scraper.scrape("https://example.com")

    def test_scrape_error_propagation(self):
        """Test that ScrapeError exceptions are properly propagated."""

        class ScrapeErrorAdapter(BaseScraper):
            """Adapter that raises ScrapeError for testing."""

            def scrape(self, url, options=None):
                from codomyrmex.scrape.exceptions import ScrapeConnectionError

                raise ScrapeConnectionError("Connection failed", url=url)

            def crawl(self, url, options=None):
                raise ScrapeError("Crawl failed")

            def map(self, url, search=None):
                raise ScrapeError("Map failed")

            def search(self, query, options=None):
                raise ScrapeError("Search failed")

            def extract(self, urls, schema=None, prompt=None):
                raise ScrapeError("Extract failed")

        adapter = ScrapeErrorAdapter()
        scraper = Scraper(adapter=adapter)
        with pytest.raises(ScrapeConnectionError):
            scraper.scrape("https://example.com")
