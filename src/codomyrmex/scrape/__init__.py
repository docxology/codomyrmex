"""Scrape Module for Codomyrmex.

This module provides web scraping capabilities with support for multiple
scraping providers. Currently supports Firecrawl integration.

Example:
    ```python
    from codomyrmex.scrape import Scraper, ScrapeOptions, ScrapeFormat

    scraper = Scraper()
    options = ScrapeOptions(formats=[ScrapeFormat.MARKDOWN, ScrapeFormat.HTML])
    result = scraper.scrape("https://example.com", options)
    print(result.content)
    ```
"""

from .config import ScrapeConfig, get_config, reset_config, set_config
from .core import (
    BaseScraper,
    CrawlResult,
    ExtractResult,
    MapResult,
    ScrapeFormat,
    ScrapeOptions,
    ScrapeResult,
    SearchResult,
)
from .exceptions import (
    FirecrawlError,
    ScrapeConnectionError,
    ScrapeError,
    ScrapeTimeoutError,
    ScrapeValidationError,
)
from .scraper import Scraper

__all__ = [
    # Main classes
    "Scraper",
    "BaseScraper",
    "ScrapeConfig",
    # Core types
    "ScrapeResult",
    "ScrapeOptions",
    "ScrapeFormat",
    "CrawlResult",
    "MapResult",
    "SearchResult",
    "ExtractResult",
    # Exceptions
    "ScrapeError",
    "ScrapeConnectionError",
    "ScrapeTimeoutError",
    "ScrapeValidationError",
    "FirecrawlError",
    # Config functions
    "get_config",
    "set_config",
    "reset_config",
]

__version__ = "0.1.0"


