"""Firecrawl integration for the scrape module.

This submodule provides integration with the Firecrawl Python SDK,
wrapping it in a typed interface that matches the core scraping abstractions.
"""

from .adapter import FirecrawlAdapter
from .client import FirecrawlClient

__all__ = ["FirecrawlClient", "FirecrawlAdapter"]

