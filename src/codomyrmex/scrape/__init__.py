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

import contextlib

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
with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus


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
            "help": "list available output formats",
            "handler": lambda: print(
                "\n".join(f"- {fmt.value}" for fmt in ScrapeFormat)
            ),
        },
    }


__all__ = [
    "BaseScraper",
    "CrawlResult",
    "ExtractResult",
    "FirecrawlError",
    "MapResult",
    "ScrapeConfig",
    "ScrapeConnectionError",
    # Exceptions
    "ScrapeError",
    "ScrapeFormat",
    "ScrapeOptions",
    # Core types
    "ScrapeResult",
    "ScrapeTimeoutError",
    "ScrapeValidationError",
    # Main classes
    "Scraper",
    "SearchResult",
    # CLI integration
    "cli_commands",
    # Submodules
    "extractors",
    # Config functions
    "get_config",
    "reset_config",
    "set_config",
]

__version__ = "0.1.0"
