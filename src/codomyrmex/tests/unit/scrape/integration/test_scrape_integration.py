"""Integration tests for scraping workflows.

Note: These tests may require actual API keys and network access.
They are designed to test end-to-end workflows but should be run
with caution and proper API key configuration.
"""

import os

import pytest

from codomyrmex.scrape import ScrapeConfig, ScrapeFormat, ScrapeOptions, Scraper
from codomyrmex.scrape.exceptions import ScrapeError


@pytest.mark.skipif(
    not os.getenv("FIRECRAWL_API_KEY") and not os.getenv("FC_API_KEY"),
    reason="Firecrawl API key not set",
)
class TestScrapeIntegration:
    """Integration tests for scraping operations.

    These tests require:
        pass
    - FIRECRAWL_API_KEY environment variable set
    - Network access
    - Firecrawl service availability
    """

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        config = ScrapeConfig.from_env()
        return Scraper(config=config)

    def test_basic_scrape(self, scraper):
        """Test basic scraping functionality."""
        # Use a simple, reliable test URL
        result = scraper.scrape("https://example.com")
        assert result.success is True
        assert result.url == "https://example.com"
        assert len(result.content) > 0

    def test_scrape_with_formats(self, scraper):
        """Test scraping with multiple formats."""
        options = ScrapeOptions(
            formats=[ScrapeFormat.MARKDOWN, ScrapeFormat.METADATA]
        )
        result = scraper.scrape("https://example.com", options)
        assert result.success is True
        assert result.has_format(ScrapeFormat.MARKDOWN)

    def test_map_website(self, scraper):
        """Test website mapping."""
        result = scraper.map("https://example.com")
        assert result.total >= 0
        # Example.com may have links or may not, so we just check structure

    def test_search_web(self, scraper):
        """Test web search."""
        result = scraper.search("python programming")
        assert result.query == "python programming"
        assert result.total >= 0
        # Search results may vary, so we just check structure

    def test_extract_data(self, scraper):
        """Test data extraction."""
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
            },
        }
        result = scraper.extract(
            urls=["https://example.com"],
            schema=schema,
            prompt="Extract the page title",
        )
        assert result.status in ["completed", "pending"]
        assert len(result.urls) == 1



# Check if firecrawl-py is available
try:
    from firecrawl import Firecrawl  # noqa: F401
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False


@pytest.mark.skipif(not FIRECRAWL_AVAILABLE, reason="firecrawl-py not installed")
class TestScrapeErrorHandling:
    """Test error handling in integration scenarios.

    Requires firecrawl-py to be installed.
    """

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        config = ScrapeConfig(api_key="invalid-key-for-testing")
        return Scraper(config=config)

    def test_invalid_api_key_handling(self, scraper):
        """Test that invalid API keys are handled gracefully."""
        # This will likely fail, but should raise a proper exception
        with pytest.raises(ScrapeError):
            scraper.scrape("https://example.com")

    def test_invalid_url_handling(self, scraper):
        """Test that invalid URLs are handled."""
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        with pytest.raises(ScrapeValidationError):
            scraper.scrape("")

        with pytest.raises(ScrapeValidationError):
            scraper.scrape("not-a-url")
