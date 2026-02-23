# Scrape Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Web scraping module providing a unified interface for extracting content from websites. Supports multiple output formats (Markdown, HTML), site crawling, URL mapping, search, and structured data extraction. Abstracts provider-specific details (currently Firecrawl) behind a consistent API with configurable options and a robust exception hierarchy.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Main Classes

- **`Scraper`** -- Primary scraping interface that delegates to provider-specific backends; supports `scrape()`, `crawl()`, `map()`, `search()`, and `extract()` operations
- **`BaseScraper`** -- Abstract base class defining the scraper contract for provider implementations
- **`ScrapeConfig`** -- Configuration dataclass holding API keys, timeouts, and provider settings

### Core Types

- **`ScrapeResult`** -- Result object from a single page scrape containing content and metadata
- **`ScrapeOptions`** -- Options dataclass for configuring scrape behavior (formats, selectors, wait strategies)
- **`ScrapeFormat`** -- Enum of supported output formats (`MARKDOWN`, `HTML`, etc.)
- **`CrawlResult`** -- Result object from a multi-page crawl operation
- **`MapResult`** -- Result object from a site URL mapping operation
- **`SearchResult`** -- Result object from a web search operation
- **`ExtractResult`** -- Result object from structured data extraction

### Exceptions

- **`ScrapeError`** -- Base exception for all scraping errors
- **`ScrapeConnectionError`** -- Raised when connection to the target URL fails
- **`ScrapeTimeoutError`** -- Raised when a scrape operation exceeds the configured timeout
- **`ScrapeValidationError`** -- Raised for invalid input parameters or configuration
- **`FirecrawlError`** -- Raised for Firecrawl provider-specific errors

### Config Functions

- **`get_config()`** -- Retrieve the current scrape configuration
- **`set_config()`** -- Update scrape configuration values
- **`reset_config()`** -- Reset configuration to defaults

## Directory Contents

- `scraper.py` -- `Scraper` class implementation with provider delegation
- `core.py` -- `BaseScraper` ABC and all result/option dataclasses and enums
- `config.py` -- `ScrapeConfig` and configuration management functions
- `exceptions.py` -- Exception hierarchy for scrape error handling
- `firecrawl/` -- Firecrawl provider implementation

## Quick Start

```python
from codomyrmex.scrape import ScrapeConfig, ScrapeFormat, ScrapeResult

# Initialize ScrapeConfig
instance = ScrapeConfig()
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k scrape -v
```

## Navigation

- **Full Documentation**: [docs/modules/scrape/](../../../docs/modules/scrape/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
