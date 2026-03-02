"""Main scraper class implementing the core scraping interface.

This module provides the main Scraper class that serves as the primary
interface for scraping operations, delegating to provider-specific adapters.
"""

from urllib.parse import urlparse

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.scrape.config import ScrapeConfig, get_config
from codomyrmex.scrape.core import (
    BaseScraper,
    CrawlResult,
    ExtractResult,
    MapResult,
    ScrapeOptions,
    ScrapeResult,
    SearchResult,
)
from codomyrmex.scrape.exceptions import ScrapeError, ScrapeValidationError

logger = get_logger(__name__)


class Scraper(BaseScraper):
    """Main scraper class providing a unified interface for scraping operations.

    This class acts as a facade that delegates to provider-specific adapters
    (e.g., FirecrawlAdapter). It handles configuration, error handling, and logging.

    Example:
        ```python
        from codomyrmex.scrape import Scraper, ScrapeOptions, ScrapeFormat

        scraper = Scraper()
        options = ScrapeOptions(formats=[ScrapeFormat.MARKDOWN, ScrapeFormat.HTML])
        result = scraper.scrape("https://example.com", options)
        print(result.content)
        ```
    """

    def __init__(self, config: ScrapeConfig | None = None, adapter: BaseScraper | None = None):
        """Initialize the scraper.

        Args:
            config: Optional configuration. If not provided, uses global config.
            adapter: Optional scraper adapter. If not provided, attempts to create
                     a default adapter (FirecrawlAdapter if available).

        Raises:
            ScrapeValidationError: If configuration is invalid or no adapter is available
        """
        self.config = config or get_config()
        self.adapter = adapter

        if self.adapter is None:
            # Try to create a default adapter (Firecrawl)
            try:
                from codomyrmex.scrape.firecrawl.adapter import FirecrawlAdapter

                self.adapter = FirecrawlAdapter(config=self.config)
                logger.info("Using FirecrawlAdapter as default scraper")
            except ImportError as e:
                raise ScrapeValidationError(
                    "No scraper adapter available. Install firecrawl-py: pip install firecrawl-py",
                    context={"import_error": str(e)},
                ) from e
            except Exception as e:
                raise ScrapeError(
                    f"Failed to initialize scraper adapter: {e}",
                    context={"error_type": type(e).__name__},
                ) from e

        logger.debug(f"Scraper initialized with config: {self.config.to_dict()}")

    def scrape(self, url: str, options: ScrapeOptions | None = None) -> ScrapeResult:
        """Scrape a single URL.

        Args:
            url: The URL to scrape
            options: Optional scraping configuration

        Returns:
            ScrapeResult containing the scraped content

        Raises:
            ScrapeValidationError: If URL is invalid
            ScrapeConnectionError: If connection fails
            ScrapeTimeoutError: If operation times out
        """
        if not url or not isinstance(url, str):
            raise ScrapeValidationError("URL must be a non-empty string", field="url", value=str(url))
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ScrapeValidationError(
                f"URL must start with http:// or https://, got: {url}", field="url", value=url
            )

        logger.info(f"Scraping URL: {url}")
        try:
            result = self.adapter.scrape(url, options)
            logger.debug(f"Successfully scraped {url}, status: {result.status_code}")
            return result
        except ScrapeError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            raise ScrapeError(f"Failed to scrape {url}: {e}") from e

    def crawl(self, url: str, options: ScrapeOptions | None = None) -> CrawlResult:
        """Crawl a website starting from a URL.

        Args:
            url: The starting URL to crawl
            options: Optional crawling configuration

        Returns:
            CrawlResult containing the crawl job information

        Raises:
            ScrapeValidationError: If URL is invalid
            ScrapeConnectionError: If connection fails
        """
        if not url or not isinstance(url, str):
            raise ScrapeValidationError("URL must be a non-empty string", field="url", value=str(url))
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ScrapeValidationError(
                f"URL must start with http:// or https://, got: {url}", field="url", value=url
            )

        logger.info(f"Starting crawl from URL: {url}")
        try:
            result = self.adapter.crawl(url, options)
            logger.info(f"Crawl job {result.job_id} created, status: {result.status}")
            return result
        except ScrapeError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error crawling {url}: {e}")
            raise ScrapeError(f"Failed to crawl {url}: {e}") from e

    def map(self, url: str, search: str | None = None) -> MapResult:
        """Map the structure of a website.

        Args:
            url: The URL to map
            search: Optional search term to filter links

        Returns:
            MapResult containing discovered links

        Raises:
            ScrapeValidationError: If URL is invalid
            ScrapeConnectionError: If connection fails
        """
        if not url or not isinstance(url, str):
            raise ScrapeValidationError("URL must be a non-empty string", field="url", value=str(url))
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ScrapeValidationError(
                f"URL must start with http:// or https://, got: {url}", field="url", value=url
            )

        logger.info(f"Mapping website structure: {url}" + (f" (search: {search})" if search else ""))
        try:
            result = self.adapter.map(url, search)
            logger.info(f"Found {result.total} links for {url}")
            return result
        except ScrapeError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error mapping {url}: {e}")
            raise ScrapeError(f"Failed to map {url}: {e}") from e

    def search(
        self, query: str, options: ScrapeOptions | None = None
    ) -> SearchResult:
        """Search the web and optionally scrape results.

        Args:
            query: The search query
            options: Optional scraping configuration for results

        Returns:
            SearchResult containing search results

        Raises:
            ScrapeValidationError: If query is invalid
            ScrapeConnectionError: If connection fails
        """
        if not query or not isinstance(query, str):
            raise ScrapeValidationError("Query must be a non-empty string", field="query", value=str(query))

        logger.info(f"Searching web: {query}")
        try:
            result = self.adapter.search(query, options)
            logger.info(f"Found {result.total} results for query: {query}")
            return result
        except ScrapeError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error searching '{query}': {e}")
            raise ScrapeError(f"Failed to search '{query}': {e}") from e

    def extract(
        self,
        urls: list[str],
        schema: dict | None = None,
        prompt: str | None = None,
    ) -> ExtractResult:
        """Extract structured data from URLs using LLM.

        Args:
            urls: List of URLs to extract data from
            schema: Optional JSON schema for extraction
            prompt: Optional prompt for extraction

        Returns:
            ExtractResult containing extracted data

        Raises:
            ScrapeValidationError: If URLs are invalid
            ScrapeConnectionError: If connection fails
        """
        if not urls or not isinstance(urls, list):
            raise ScrapeValidationError("URLs must be a non-empty list", field="urls", value=str(urls))

        for url in urls:
            if not isinstance(url, str) or not url:
                raise ScrapeValidationError(
                    f"All URLs must be non-empty strings, got: {url}",
                    field="urls",
                    value=str(url),
                )
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                raise ScrapeValidationError(
                    f"URL must start with http:// or https://, got: {url}", field="urls", value=url
                )

        logger.info(f"Extracting data from {len(urls)} URL(s)")
        try:
            result = self.adapter.extract(urls, schema, prompt)
            logger.info(f"Extraction completed, status: {result.status}")
            return result
        except ScrapeError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error extracting from URLs: {e}")
            raise ScrapeError(f"Failed to extract data: {e}") from e


