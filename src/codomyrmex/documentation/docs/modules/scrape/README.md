<!-- readme: generated -->

# scrape

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/scrape/`

## Overview

Scrape Module for Codomyrmex.

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

## Public Exports

`scrape` exports 20 public symbols via `__all__`:

`BaseScraper`, `CrawlResult`, `ExtractResult`, `FirecrawlError`, `MapResult`, `ScrapeConfig`, `ScrapeConnectionError`, `ScrapeFormat`, `ScrapeOptions`, `ScrapeResult`, `ScrapeTimeoutError`, `ScrapeValidationError`, `Scraper`, `ScrapingError`, `SearchResult`, `cli_commands`, `extractors`, `get_config`, `reset_config`, `set_config`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../scrape/](../../../../scrape/)
