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

from . import extractors
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
from .extractors.scraper import Scraper

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the scrape module."""
    return {
        "fetch": {
            "help": "Fetch a URL and return scraped content",
            "args": ["--url"],
            "handler": lambda url=None: (
                print(Scraper().scrape(url).content)
                if url
                else print("Usage: scrape fetch --url <URL>")
            ),
        },
        "formats": {
            "help": "List available output formats",
            "handler": lambda: print(
                "\n".join(f"- {fmt.value}" for fmt in ScrapeFormat)
            ),
        },
    }


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
    # Submodules
    "extractors",
    # CLI integration
    "cli_commands",
]

__version__ = "0.1.0"


