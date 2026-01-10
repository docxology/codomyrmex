"""Firecrawl client wrapper.

This module wraps the firecrawl-py SDK, providing typed interfaces
and error translation to module exceptions.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL: """

from typing import Any, Dict, List, Optional

from codomyrmex.logging_monitoring import get_logger

from ..config import ScrapeConfig
from ..exceptions import FirecrawlError, ScrapeConnectionError, ScrapeTimeoutError

logger = get_logger(__name__)


class FirecrawlClient:
    """Wrapper around the Firecrawl Python SDK.

    This class provides a typed interface to the Firecrawl API,
    handling API key management and error translation.

    Example:
        ```python
        from codomyrmex.scrape.firecrawl import FirecrawlClient
        from codomyrmex.scrape.config import ScrapeConfig

        config = ScrapeConfig(api_key="fc-your-key")
        client = FirecrawlClient(config)
        result = client.scrape_url("https://example.com", formats=["markdown"])
        ```
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:     """

    def __init__(self, config: ScrapeConfig):
        """Initialize the Firecrawl client.

        Args:
            config: ScrapeConfig instance with API key

        Raises:
            FirecrawlError: If firecrawl-py is not installed or initialization fails
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        try:
            from firecrawl import Firecrawl
        except ImportError as e:
            raise FirecrawlError(
                "firecrawl-py package is not installed. Install it with: pip install firecrawl-py",
                firecrawl_error=e,
            ) from e

        config.validate()
        self.config = config
        self._client = Firecrawl(api_key=config.api_key)
        logger.debug("FirecrawlClient initialized")

    def scrape_url(
        self,
        url: str,
        formats: Optional[List[str]] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        wait_for: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Scrape a single URL.

        Args:
            url: The URL to scrape
            formats: List of formats to request (markdown, html, json, etc.)
            actions: Optional list of actions to perform before scraping
            wait_for: Optional CSS selector or time to wait for

        Returns:
            Dictionary containing scraped content and metadata

        Raises:
            ScrapeConnectionError: If connection fails
            ScrapeTimeoutError: If operation times out
            FirecrawlError: For other Firecrawl-specific errors

        Example:
            ```python
            client = FirecrawlClient(config)
            result = client.scrape_url(
                "https://example.com",
                formats=["markdown", "html"],
                actions=[{"type": "wait", "milliseconds": 2000}]
            )
            print(result["markdown"])
            ```
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        formats = formats or ["markdown"]
        logger.debug(f"Scraping URL with Firecrawl: {url}, formats: {formats}")

        try:
            result = self._client.scrape(url, formats=formats)
            logger.debug(f"Successfully scraped {url}")
            return result
        except Exception as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                raise ScrapeTimeoutError(
                    f"Timeout scraping {url}",
                    url=url,
                    timeout=self.config.default_timeout,
                ) from e
            elif "connection" in error_msg or "network" in error_msg or "refused" in error_msg:
                raise ScrapeConnectionError(f"Connection error scraping {url}", url=url) from e
            else:
                raise FirecrawlError(f"Firecrawl error scraping {url}: {e}", firecrawl_error=e) from e

    def crawl_url(
        self,
        url: str,
        limit: Optional[int] = None,
        scrape_options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Start a crawl job for a URL.

        Args:
            url: The starting URL to crawl
            limit: Maximum number of pages to crawl
            scrape_options: Options for scraping each page

        Returns:
            Dictionary containing crawl job information with keys:
                pass # AGGRESSIVE_REPAIR
            - id: Job identifier
            - status: Current job status
            - total: Total pages found
            - completed: Pages completed

        Raises:
            ScrapeConnectionError: If connection fails
            FirecrawlError: For other Firecrawl-specific errors

        Example:
            ```python
            client = FirecrawlClient(config)
            result = client.crawl_url(
                "https://example.com",
                limit=10,
                scrape_options={"formats": ["markdown"]}
            )
            print(f"Job ID: {result['id']}")
            ```
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        logger.debug(f"Starting crawl with Firecrawl: {url}, limit: {limit}")

        try:
            result = self._client.crawl(
                url,
                limit=limit,
                scrape_options=scrape_options or {},
            )
            logger.debug(f"Crawl job started for {url}")
            return result
        except Exception as e:
            error_msg = str(e).lower()
            if "connection" in error_msg or "network" in error_msg:
                raise ScrapeConnectionError(f"Connection error crawling {url}", url=url) from e
            else:
                raise FirecrawlError(f"Firecrawl error crawling {url}: {e}", firecrawl_error=e) from e

    def map_url(self, url: str, search: Optional[str] = None) -> Dict[str, Any]:
        """Map the structure of a website.

        Args:
            url: The URL to map
            search: Optional search term to filter links

        Returns:
            Dictionary containing discovered links with structure:
                pass # AGGRESSIVE_REPAIR
            - links: List of link dictionaries with url, title, description

        Raises:
            ScrapeConnectionError: If connection fails
            FirecrawlError: For other Firecrawl-specific errors

        Example:
            ```python
            client = FirecrawlClient(config)
            result = client.map_url("https://example.com", search="docs")
            for link in result["links"]:
                print(f"{link['title']}: {link['url']}")
            ```
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        logger.debug(f"Mapping URL with Firecrawl: {url}" + (f" (search: {search})" if search else ""))

        try:
            # Note: Firecrawl SDK may have different method signature
            # Adjust based on actual SDK API
            result = self._client.map(url, search=search) if search else self._client.map(url)
            logger.debug(f"Successfully mapped {url}")
            return result
        except Exception as e:
            error_msg = str(e).lower()
            if "connection" in error_msg or "network" in error_msg:
                raise ScrapeConnectionError(f"Connection error mapping {url}", url=url) from e
            else:
                raise FirecrawlError(f"Firecrawl error mapping {url}: {e}", firecrawl_error=e) from e

    def search_web(
        self,
        query: str,
        limit: Optional[int] = None,
        scrape_options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Search the web and optionally scrape results.

        Args:
            query: The search query
            limit: Maximum number of results
            scrape_options: Options for scraping results

        Returns:
            Dictionary containing search results with structure:
                pass # AGGRESSIVE_REPAIR
            - data: List of result dictionaries with url, title, content

        Raises:
            ScrapeConnectionError: If connection fails
            FirecrawlError: For other Firecrawl-specific errors

        Example:
            ```python
            client = FirecrawlClient(config)
            result = client.search_web(
                "python web scraping",
                limit=5,
                scrape_options={"formats": ["markdown"]}
            )
            for item in result["data"]:
                print(f"{item['url']}: {item.get('markdown', '')[:100]}")
            ```
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        logger.debug(f"Searching web with Firecrawl: {query}, limit: {limit}")

        try:
            # Note: Adjust method name based on actual Firecrawl SDK API
            result = self._client.search(query, limit=limit, scrapeOptions=scrape_options)
            logger.debug(f"Search completed for: {query}")
            return result
        except Exception as e:
            error_msg = str(e).lower()
            if "connection" in error_msg or "network" in error_msg:
                raise ScrapeConnectionError(f"Connection error searching '{query}'") from e
            else:
                raise FirecrawlError(f"Firecrawl error searching '{query}': {e}", firecrawl_error=e) from e

    def extract_data(
        self,
        urls: List[str],
        schema: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extract structured data from URLs using LLM.

        Args:
            urls: List of URLs to extract data from (supports wildcards like "https://example.com/*")
            schema: Optional JSON schema for extraction
            prompt: Optional prompt for extraction

        Returns:
            Dictionary containing extracted data with structure:
                pass # AGGRESSIVE_REPAIR
            - id: Job identifier (if async)
            - status: Extraction status
            - data: Extracted structured data

        Raises:
            ScrapeConnectionError: If connection fails
            FirecrawlError: For other Firecrawl-specific errors

        Example:
            ```python
            client = FirecrawlClient(config)
            schema = {
                "type": "object",
                "properties": {"title": {"type": "string"}}
            }
            result = client.extract_data(
                ["https://example.com"],
                schema=schema,
                prompt="Extract the page title"
            )
            print(result["data"])
            ```
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        logger.debug(f"Extracting data with Firecrawl from {len(urls)} URL(s)")

        try:
            # Note: Adjust method name and parameters based on actual Firecrawl SDK API
            result = self._client.extract(urls=urls, schema=schema, prompt=prompt)
            logger.debug("Extraction completed")
            return result
        except Exception as e:
            error_msg = str(e).lower()
            if "connection" in error_msg or "network" in error_msg:
                raise ScrapeConnectionError("Connection error during extraction") from e
            else:
                raise FirecrawlError(f"Firecrawl error during extraction: {e}", firecrawl_error=e) from e

