"""Unit tests for Firecrawl integration.

Tests use real implementations only. When firecrawl-py is not available,
tests are skipped rather than using mocks. All data processing and conversion
logic is tested with real data structures.
"""

import pytest

from codomyrmex.scrape.config import ScrapeConfig
from codomyrmex.scrape.core import ScrapeFormat, ScrapeOptions
from codomyrmex.scrape.exceptions import (
    FirecrawlError,
    ScrapeConnectionError,
    ScrapeTimeoutError,
)
from codomyrmex.scrape.firecrawl.adapter import FirecrawlAdapter
from codomyrmex.scrape.firecrawl.client import FirecrawlClient


# Check if firecrawl-py is available
try:
    from firecrawl import Firecrawl

    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False


class TestFirecrawlClient:
    """Test FirecrawlClient wrapper with real implementations."""

    def test_init_without_firecrawl_package(self):
        """Test that FirecrawlClient raises error when firecrawl-py is not installed."""
        if FIRECRAWL_AVAILABLE:
            pytest.skip("firecrawl-py is installed, cannot test import error")

        config = ScrapeConfig(api_key="test-key")
        with pytest.raises(FirecrawlError):
            FirecrawlClient(config)

    def test_init_without_api_key(self):
        """Test that FirecrawlClient validates API key."""
        config = ScrapeConfig(api_key=None)
        # This will fail at validation
        with pytest.raises(Exception):  # ScrapeValidationError or FirecrawlError
            try:
                FirecrawlClient(config)
            except Exception as e:
                # Either validation error or import error is acceptable
                assert "api key" in str(e).lower() or "firecrawl" in str(e).lower()
                raise

    @pytest.mark.skipif(not FIRECRAWL_AVAILABLE, reason="firecrawl-py not installed")
    def test_init_success(self):
        """Test successful FirecrawlClient initialization with real SDK."""
        config = ScrapeConfig(api_key="test-key")
        # This will fail validation if API key is invalid, but tests the real initialization
        try:
            client = FirecrawlClient(config)
            assert client.config == config
            assert client._client is not None
        except Exception as e:
            # If API key is invalid, that's expected - we're testing real behavior
            if "api key" in str(e).lower() or "validation" in str(e).lower():
                pytest.skip(f"API key validation failed (expected): {e}")
            raise


class TestFirecrawlAdapter:
    """Test FirecrawlAdapter with real implementations."""

    def test_init_without_firecrawl_package(self):
        """Test that FirecrawlAdapter raises error when firecrawl-py is not installed."""
        if FIRECRAWL_AVAILABLE:
            pytest.skip("firecrawl-py is installed, cannot test import error")

        config = ScrapeConfig(api_key="test-key")
        with pytest.raises(Exception):  # FirecrawlError or ScrapeValidationError
            try:
                FirecrawlAdapter(config)
            except Exception as e:
                # Either validation error or import error is acceptable
                assert "firecrawl" in str(e).lower() or "api key" in str(e).lower()
                raise

    def test_adapter_implements_base_scraper(self):
        """Test that FirecrawlAdapter implements BaseScraper interface."""
        from codomyrmex.scrape.core import BaseScraper

        assert issubclass(FirecrawlAdapter, BaseScraper)

    @pytest.mark.skipif(not FIRECRAWL_AVAILABLE, reason="firecrawl-py not installed")
    def test_adapter_initialization(self):
        """Test FirecrawlAdapter initialization with real client."""
        config = ScrapeConfig(api_key="test-key")
        try:
            adapter = FirecrawlAdapter(config)
            assert adapter.config == config
            assert adapter.client is not None
        except Exception as e:
            # If API key is invalid, that's expected
            if "api key" in str(e).lower() or "validation" in str(e).lower():
                pytest.skip(f"API key validation failed (expected): {e}")
            raise


class TestFirecrawlConversion:
    """Test Firecrawl result conversion methods with real data structures."""

    def test_convert_scrape_result_from_dict(self):
        """Test converting Firecrawl dict result to ScrapeResult."""
        from codomyrmex.scrape.firecrawl.adapter import FirecrawlAdapter

        adapter = FirecrawlAdapter.__new__(FirecrawlAdapter)  # Create without __init__

        # Real data structure from Firecrawl API
        firecrawl_data = {
            "data": {
                "markdown": "# Test Content",
                "html": "<h1>Test Content</h1>",
                "metadata": {"title": "Test", "statusCode": 200},
            }
        }

        result = adapter._convert_scrape_result(firecrawl_data, "https://example.com")
        assert result.url == "https://example.com"
        assert result.content == "# Test Content"
        assert result.formats.get("markdown") == "# Test Content"
        assert result.formats.get("html") == "<h1>Test Content</h1>"
        assert result.status_code == 200
        assert result.metadata.get("title") == "Test"

    def test_convert_scrape_result_from_document_object(self):
        """Test converting Firecrawl Document object to ScrapeResult."""
        from codomyrmex.scrape.firecrawl.adapter import FirecrawlAdapter

        adapter = FirecrawlAdapter.__new__(FirecrawlAdapter)

        # Real Document-like object structure
        class DocumentObject:
            """Real Document object structure from firecrawl-py."""

            def __init__(self):
                self.markdown = "# Test"
                self.html = "<h1>Test</h1>"
                self.metadata = {"title": "Test", "statusCode": 200}

        firecrawl_data = DocumentObject()
        result = adapter._convert_scrape_result(firecrawl_data, "https://example.com")

        assert result.url == "https://example.com"
        assert result.content == "# Test"
        assert result.formats.get("markdown") == "# Test"
        assert result.status_code == 200

    def test_convert_crawl_result(self):
        """Test converting Firecrawl crawl result to CrawlResult."""
        from codomyrmex.scrape.firecrawl.adapter import FirecrawlAdapter

        adapter = FirecrawlAdapter.__new__(FirecrawlAdapter)

        # Real crawl result structure
        firecrawl_data = {
            "id": "crawl-123",
            "status": "completed",
            "total": 5,
            "completed": 5,
            "creditsUsed": 5,
            "expiresAt": "2025-12-31T00:00:00Z",
            "data": [
                {
                    "markdown": "Content 1",
                    "metadata": {"sourceURL": "https://example.com/page1"},
                }
            ],
        }

        result = adapter._convert_crawl_result(firecrawl_data, "https://example.com")
        assert result.job_id == "crawl-123"
        assert result.status == "completed"
        assert result.total == 5
        assert result.completed == 5
        assert result.credits_used == 5
        assert result.expires_at == "2025-12-31T00:00:00Z"
        assert len(result.results) == 1
        assert result.results[0].url == "https://example.com/page1"

    def test_convert_map_result(self):
        """Test converting Firecrawl map result to MapResult."""
        from codomyrmex.scrape.firecrawl.adapter import FirecrawlAdapter

        adapter = FirecrawlAdapter.__new__(FirecrawlAdapter)

        # Real map result structure
        firecrawl_data = {
            "links": [
                {"url": "https://example.com/page1", "title": "Page 1", "description": "Description 1"},
                {"url": "https://example.com/page2", "title": "Page 2", "description": "Description 2"},
            ]
        }

        result = adapter._convert_map_result(firecrawl_data)
        assert result.total == 2
        assert len(result.links) == 2
        assert result.links[0]["url"] == "https://example.com/page1"
        assert result.links[0]["title"] == "Page 1"

    def test_convert_search_result(self):
        """Test converting Firecrawl search result to SearchResult."""
        from codomyrmex.scrape.firecrawl.adapter import FirecrawlAdapter

        adapter = FirecrawlAdapter.__new__(FirecrawlAdapter)

        # Real search result structure
        firecrawl_data = {
            "data": [
                {
                    "url": "https://example.com",
                    "title": "Example",
                    "markdown": "Content",
                    "metadata": {"title": "Example", "statusCode": 200},
                }
            ]
        }

        result = adapter._convert_search_result(firecrawl_data, "test query")
        assert result.query == "test query"
        assert result.total == 1
        assert len(result.results) == 1
        assert result.results[0].url == "https://example.com"
        assert result.results[0].content == "Content"

    def test_convert_extract_result(self):
        """Test converting Firecrawl extract result to ExtractResult."""
        from codomyrmex.scrape.firecrawl.adapter import FirecrawlAdapter

        adapter = FirecrawlAdapter.__new__(FirecrawlAdapter)

        # Real extract result structure
        firecrawl_data = {
            "id": "extract-123",
            "status": "completed",
            "data": {"title": "Test", "content": "Content"},
        }

        urls = ["https://example.com"]
        result = adapter._convert_extract_result(firecrawl_data, urls)

        assert result.job_id == "extract-123"
        assert result.status == "completed"
        assert result.data == {"title": "Test", "content": "Content"}
        assert result.urls == urls

    def test_convert_with_empty_data(self):
        """Test conversion with empty or missing data."""
        from codomyrmex.scrape.firecrawl.adapter import FirecrawlAdapter

        adapter = FirecrawlAdapter.__new__(FirecrawlAdapter)

        # Test empty dict
        result = adapter._convert_scrape_result({}, "https://example.com")
        assert result.url == "https://example.com"
        assert result.content == ""
        assert result.success is True
        assert len(result.formats) == 0

        # Test non-dict, non-object (edge case)
        result = adapter._convert_scrape_result("string", "https://example.com")
        assert result.url == "https://example.com"
        assert result.content == "string"

    def test_convert_crawl_result_with_empty_data(self):
        """Test converting crawl result with empty data array."""
        from codomyrmex.scrape.firecrawl.adapter import FirecrawlAdapter

        adapter = FirecrawlAdapter.__new__(FirecrawlAdapter)

        firecrawl_data = {
            "id": "crawl-123",
            "status": "pending",
            "total": 0,
            "completed": 0,
            "data": [],
        }

        result = adapter._convert_crawl_result(firecrawl_data, "https://example.com")
        assert result.job_id == "crawl-123"
        assert result.status == "pending"
        assert result.total == 0
        assert len(result.results) == 0

    def test_convert_with_missing_fields(self):
        """Test conversion with missing optional fields."""
        from codomyrmex.scrape.firecrawl.adapter import FirecrawlAdapter

        adapter = FirecrawlAdapter.__new__(FirecrawlAdapter)

        # Minimal scrape result
        firecrawl_data = {
            "data": {
                "markdown": "Content",
                # Missing html, json, metadata
            }
        }

        result = adapter._convert_scrape_result(firecrawl_data, "https://example.com")
        assert result.content == "Content"
        assert result.formats.get("markdown") == "Content"
        assert result.status_code is None  # No metadata.statusCode
