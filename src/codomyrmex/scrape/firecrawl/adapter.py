"""Firecrawl adapter implementing the core scraper interface.

This module provides FirecrawlAdapter, which implements BaseScraper
using the Firecrawl service via FirecrawlClient.
"""

from typing import Any, Dict, List, Optional

from codomyrmex.logging_monitoring import get_logger

from ..config import ScrapeConfig
from ..core import (
    BaseScraper,
    CrawlResult,
    ExtractResult,
    MapResult,
    ScrapeFormat,
    ScrapeOptions,
    ScrapeResult,
    SearchResult,
)
from ..exceptions import FirecrawlError, ScrapeError

from .client import FirecrawlClient

logger = get_logger(__name__)


class FirecrawlAdapter(BaseScraper):
    """Adapter that implements BaseScraper using Firecrawl.

    This adapter converts between the core scraping abstractions
    and the Firecrawl SDK, handling format conversions and error translation.

    Example:
        ```python
        from codomyrmex.scrape.firecrawl import FirecrawlAdapter
        from codomyrmex.scrape.config import ScrapeConfig
        from codomyrmex.scrape.core import ScrapeOptions, ScrapeFormat

        config = ScrapeConfig(api_key="fc-your-key")
        adapter = FirecrawlAdapter(config)
        options = ScrapeOptions(formats=[ScrapeFormat.MARKDOWN])
        result = adapter.scrape("https://example.com", options)
        ```
    """

    def __init__(self, config: Optional[ScrapeConfig] = None):
        """Initialize the Firecrawl adapter.

        Args:
            config: Optional ScrapeConfig. If not provided, uses default config.

        Raises:
            FirecrawlError: If Firecrawl client cannot be initialized
        """
        from ..config import get_config

        self.config = config or get_config()
        self.client = FirecrawlClient(self.config)
        logger.debug("FirecrawlAdapter initialized")

    def scrape(self, url: str, options: Optional[ScrapeOptions] = None) -> ScrapeResult:
        """Scrape a single URL using Firecrawl.

        Args:
            url: The URL to scrape
            options: Optional scraping configuration

        Returns:
            ScrapeResult containing the scraped content with formats and metadata

        Example:
            ```python
            adapter = FirecrawlAdapter(config)
            options = ScrapeOptions(formats=[ScrapeFormat.MARKDOWN, ScrapeFormat.HTML])
            result = adapter.scrape("https://example.com", options)
            print(result.content)  # Markdown content
            print(result.formats.get("html"))  # HTML content
            ```
        """
        options = options or ScrapeOptions()
        formats = [f.value if isinstance(f, ScrapeFormat) else f for f in options.formats]

        try:
            firecrawl_result = self.client.scrape_url(
                url,
                formats=formats,
                actions=options.actions if options.actions else None,
                wait_for=options.wait_for,
            )

            # Convert Firecrawl result to ScrapeResult
            result = self._convert_scrape_result(firecrawl_result, url)
            return result
        except ScrapeError:
            raise
        except Exception as e:
            logger.error(f"Error in FirecrawlAdapter.scrape: {e}")
            raise ScrapeError(f"Failed to scrape {url}: {e}") from e

    def crawl(self, url: str, options: Optional[ScrapeOptions] = None) -> CrawlResult:
        """Crawl a website starting from a URL using Firecrawl.

        Args:
            url: The starting URL to crawl
            options: Optional crawling configuration (limit, max_depth, formats)

        Returns:
            CrawlResult containing the crawl job information and results

        Example:
            ```python
            adapter = FirecrawlAdapter(config)
            options = ScrapeOptions(limit=10, formats=[ScrapeFormat.MARKDOWN])
            result = adapter.crawl("https://example.com", options)
            print(f"Job ID: {result.job_id}, Status: {result.status}")
            for page in result.results:
                print(f"Scraped: {page.url}")
            ```
        """
        options = options or ScrapeOptions()
        scrape_options: Dict[str, Any] = {}

        if options.formats:
            scrape_options["formats"] = [
                f.value if isinstance(f, ScrapeFormat) else f for f in options.formats
            ]

        try:
            firecrawl_result = self.client.crawl_url(
                url,
                limit=options.limit,
                scrape_options=scrape_options if scrape_options else None,
            )

            # Convert Firecrawl result to CrawlResult
            result = self._convert_crawl_result(firecrawl_result, url)
            return result
        except ScrapeError:
            raise
        except Exception as e:
            logger.error(f"Error in FirecrawlAdapter.crawl: {e}")
            raise ScrapeError(f"Failed to crawl {url}: {e}") from e

    def map(self, url: str, search: Optional[str] = None) -> MapResult:
        """Map the structure of a website using Firecrawl.

        Args:
            url: The URL to map
            search: Optional search term to filter links

        Returns:
            MapResult containing discovered links with metadata

        Example:
            ```python
            adapter = FirecrawlAdapter(config)
            result = adapter.map("https://example.com", search="docs")
            print(f"Found {result.total} links")
            for link in result.links:
                print(f"{link.get('title')}: {link.get('url')}")
            ```
        """
        try:
            firecrawl_result = self.client.map_url(url, search=search)

            # Convert Firecrawl result to MapResult
            result = self._convert_map_result(firecrawl_result)
            return result
        except ScrapeError:
            raise
        except Exception as e:
            logger.error(f"Error in FirecrawlAdapter.map: {e}")
            raise ScrapeError(f"Failed to map {url}: {e}") from e

    def search(
        self, query: str, options: Optional[ScrapeOptions] = None
    ) -> SearchResult:
        """Search the web and optionally scrape results using Firecrawl.

        Args:
            query: The search query
            options: Optional scraping configuration for results (formats, limit)

        Returns:
            SearchResult containing search results with scraped content

        Example:
            ```python
            adapter = FirecrawlAdapter(config)
            options = ScrapeOptions(formats=[ScrapeFormat.MARKDOWN], limit=5)
            result = adapter.search("python web scraping", options)
            print(f"Found {result.total} results")
            for item in result.results:
                print(f"{item.url}: {item.content[:100]}")
            ```
        """
        options = options or ScrapeOptions()
        scrape_options: Dict[str, Any] = {}

        if options.formats:
            scrape_options["formats"] = [
                f.value if isinstance(f, ScrapeFormat) else f for f in options.formats
            ]

        try:
            firecrawl_result = self.client.search_web(
                query,
                limit=options.limit,
                scrape_options=scrape_options if scrape_options else None,
            )

            # Convert Firecrawl result to SearchResult
            result = self._convert_search_result(firecrawl_result, query)
            return result
        except ScrapeError:
            raise
        except Exception as e:
            logger.error(f"Error in FirecrawlAdapter.search: {e}")
            raise ScrapeError(f"Failed to search '{query}': {e}") from e

    def extract(
        self,
        urls: List[str],
        schema: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None,
    ) -> ExtractResult:
        """Extract structured data from URLs using Firecrawl LLM extraction.

        Args:
            urls: List of URLs to extract data from (supports wildcards like "https://example.com/*")
            schema: Optional JSON schema for extraction
            prompt: Optional prompt for extraction

        Returns:
            ExtractResult containing extracted structured data

        Example:
            ```python
            adapter = FirecrawlAdapter(config)
            schema = {
                "type": "object",
                "properties": {"title": {"type": "string"}}
            }
            result = adapter.extract(
                ["https://example.com"],
                schema=schema,
                prompt="Extract the page title"
            )
            print(result.data)
            ```
        """
        try:
            firecrawl_result = self.client.extract_data(urls, schema=schema, prompt=prompt)

            # Convert Firecrawl result to ExtractResult
            result = self._convert_extract_result(firecrawl_result, urls)
            return result
        except ScrapeError:
            raise
        except Exception as e:
            logger.error(f"Error in FirecrawlAdapter.extract: {e}")
            raise ScrapeError(f"Failed to extract data: {e}") from e

    def _convert_scrape_result(self, firecrawl_data: Dict[str, Any], url: str) -> ScrapeResult:
        """Convert Firecrawl scrape result to ScrapeResult.

        Args:
            firecrawl_data: Raw Firecrawl API response
            url: The URL that was scraped

        Returns:
            ScrapeResult instance
        """
        # Firecrawl returns data in different formats depending on SDK version
        # Handle both Document objects and dict responses
        if hasattr(firecrawl_data, "markdown"):
            # Document object
            content = firecrawl_data.markdown or ""
            formats = {}
            if hasattr(firecrawl_data, "markdown") and firecrawl_data.markdown:
                formats["markdown"] = firecrawl_data.markdown
            if hasattr(firecrawl_data, "html") and firecrawl_data.html:
                formats["html"] = firecrawl_data.html
            if hasattr(firecrawl_data, "json") and firecrawl_data.json:
                formats["json"] = firecrawl_data.json

            metadata = {}
            if hasattr(firecrawl_data, "metadata"):
                metadata = firecrawl_data.metadata if isinstance(firecrawl_data.metadata, dict) else {}
        elif isinstance(firecrawl_data, dict):
            # Dict response - handle both nested (data.markdown) and flat (markdown) structures
            data = firecrawl_data.get("data", firecrawl_data)
            if not isinstance(data, dict):
                data = firecrawl_data
            content = data.get("markdown", data.get("content", ""))
            formats = {}
            if "markdown" in data:
                formats["markdown"] = data["markdown"]
            if "html" in data:
                formats["html"] = data["html"]
            if "json" in data:
                formats["json"] = data["json"]

            metadata = data.get("metadata", {})
        else:
            # Fallback
            content = str(firecrawl_data)
            formats = {}
            metadata = {}

        status_code = metadata.get("statusCode") if isinstance(metadata, dict) else None

        return ScrapeResult(
            url=url,
            content=content,
            formats=formats,
            metadata=metadata if isinstance(metadata, dict) else {},
            status_code=status_code,
            success=True,
        )

    def _convert_crawl_result(self, firecrawl_data: Dict[str, Any], url: str) -> CrawlResult:
        """Convert Firecrawl crawl result to CrawlResult.

        Args:
            firecrawl_data: Raw Firecrawl API response
            url: The starting URL

        Returns:
            CrawlResult instance
        """
        # Firecrawl crawl returns job info or completed results
        if isinstance(firecrawl_data, dict):
            job_id = firecrawl_data.get("id", firecrawl_data.get("jobId", ""))
            status = firecrawl_data.get("status", "pending")
            total = firecrawl_data.get("total", 0)
            completed = firecrawl_data.get("completed", 0)
            credits_used = firecrawl_data.get("creditsUsed", 0)
            expires_at = firecrawl_data.get("expiresAt")

            # Convert data array to ScrapeResult list
            results = []
            data_list = firecrawl_data.get("data", [])
            for item in data_list:
                if isinstance(item, dict):
                    result_url = item.get("metadata", {}).get("sourceURL", url)
                    scrape_result = self._convert_scrape_result(item, result_url)
                    results.append(scrape_result)

            return CrawlResult(
                job_id=job_id,
                status=status,
                total=total,
                completed=completed,
                results=results,
                credits_used=credits_used,
                expires_at=expires_at,
            )
        else:
            # Fallback for unexpected format
            return CrawlResult(
                job_id="unknown",
                status="unknown",
                total=0,
                completed=0,
                results=[],
            )

    def _convert_map_result(self, firecrawl_data: Dict[str, Any]) -> MapResult:
        """Convert Firecrawl map result to MapResult.

        Args:
            firecrawl_data: Raw Firecrawl API response

        Returns:
            MapResult instance
        """
        if isinstance(firecrawl_data, dict):
            links = firecrawl_data.get("links", [])
            return MapResult(links=links, total=len(links))
        else:
            return MapResult(links=[], total=0)

    def _convert_search_result(self, firecrawl_data: Dict[str, Any], query: str) -> SearchResult:
        """Convert Firecrawl search result to SearchResult.

        Args:
            firecrawl_data: Raw Firecrawl API response
            query: The search query

        Returns:
            SearchResult instance
        """
        if isinstance(firecrawl_data, dict):
            data_list = firecrawl_data.get("data", [])
            results = []
            for item in data_list:
                if isinstance(item, dict):
                    url = item.get("url", "")
                    scrape_result = self._convert_scrape_result(item, url)
                    results.append(scrape_result)

            return SearchResult(query=query, results=results, total=len(results))
        else:
            return SearchResult(query=query, results=[], total=0)

    def _convert_extract_result(
        self, firecrawl_data: Dict[str, Any], urls: List[str]
    ) -> ExtractResult:
        """Convert Firecrawl extract result to ExtractResult.

        Args:
            firecrawl_data: Raw Firecrawl API response
            urls: List of URLs that were processed

        Returns:
            ExtractResult instance
        """
        if isinstance(firecrawl_data, dict):
            job_id = firecrawl_data.get("id", firecrawl_data.get("jobId"))
            status = firecrawl_data.get("status", "completed")
            data = firecrawl_data.get("data", {})

            return ExtractResult(
                job_id=job_id,
                status=status,
                data=data if isinstance(data, dict) else {},
                urls=urls,
            )
        else:
            return ExtractResult(
                job_id=None,
                status="completed",
                data={},
                urls=urls,
            )

