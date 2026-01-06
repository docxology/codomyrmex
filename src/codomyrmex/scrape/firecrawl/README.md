# Firecrawl Integration

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

Firecrawl integration submodule providing access to the Firecrawl web scraping service. This submodule wraps the Firecrawl Python SDK and provides a typed interface that integrates with the core scraping abstractions.

## Features

- **Single URL Scraping**: Scrape individual web pages with multiple format support
- **Website Crawling**: Crawl entire websites and extract content from all accessible pages
- **Site Mapping**: Discover and map the structure of websites
- **Web Search**: Search the web and optionally scrape search results
- **LLM Extraction**: Extract structured data from pages using AI/LLM
- **Batch Operations**: Process multiple URLs efficiently
- **Dynamic Content**: Support for JavaScript-rendered content with actions (click, scroll, wait)

## Quick Start

```python
from codomyrmex.scrape.firecrawl import FirecrawlAdapter
from codomyrmex.scrape.config import ScrapeConfig
from codomyrmex.scrape.core import ScrapeOptions, ScrapeFormat

# Configure with API key
config = ScrapeConfig(api_key="fc-your-api-key")
adapter = FirecrawlAdapter(config)

# Scrape a URL
options = ScrapeOptions(formats=[ScrapeFormat.MARKDOWN, ScrapeFormat.HTML])
result = adapter.scrape("https://example.com", options)
print(result.content)
```

## Components

### FirecrawlClient

Low-level wrapper around the Firecrawl Python SDK. Handles API communication, error translation, and provides typed interfaces.

**Key Methods**:
- `scrape_url()`: Scrape a single URL
- `crawl_url()`: Start a crawl job
- `map_url()`: Map website structure
- `search_web()`: Search the web
- `extract_data()`: Extract structured data

### FirecrawlAdapter

High-level adapter implementing the `BaseScraper` interface. Converts between core abstractions and Firecrawl SDK types.

**Key Methods**:
- `scrape()`: Scrape with ScrapeResult return type
- `crawl()`: Crawl with CrawlResult return type
- `map()`: Map with MapResult return type
- `search()`: Search with SearchResult return type
- `extract()`: Extract with ExtractResult return type

## Configuration

The Firecrawl integration uses `ScrapeConfig` for configuration:

```python
from codomyrmex.scrape.config import ScrapeConfig

# From environment variables
config = ScrapeConfig.from_env()  # Reads FIRECRAWL_API_KEY

# Or explicitly
config = ScrapeConfig(
    api_key="fc-your-api-key",
    default_timeout=30.0,
    max_retries=3,
)
```

### Environment Variables

- `FIRECRAWL_API_KEY` or `FC_API_KEY`: Firecrawl API key (required)
- `SCRAPE_BASE_URL`: Base URL for API (default: https://api.firecrawl.dev)
- `SCRAPE_TIMEOUT`: Default timeout in seconds (default: 30.0)
- `SCRAPE_MAX_RETRIES`: Maximum retry attempts (default: 3)

## Usage Examples

### Basic Scraping

```python
from codomyrmex.scrape.firecrawl import FirecrawlAdapter
from codomyrmex.scrape.config import ScrapeConfig

config = ScrapeConfig(api_key="fc-your-key")
adapter = FirecrawlAdapter(config)

result = adapter.scrape("https://example.com")
print(result.content)  # Markdown content
print(result.formats.get("html"))  # HTML content
```

### Crawling a Website

```python
from codomyrmex.scrape.core import ScrapeOptions, ScrapeFormat

options = ScrapeOptions(
    formats=[ScrapeFormat.MARKDOWN],
    limit=10,  # Maximum pages
)

crawl_result = adapter.crawl("https://example.com", options)
print(f"Crawl job: {crawl_result.job_id}")
print(f"Status: {crawl_result.status}")
print(f"Total pages: {crawl_result.total}")

for page_result in crawl_result.results:
    print(f"Scraped: {page_result.url}")
```

### Mapping Website Structure

```python
map_result = adapter.map("https://example.com")
print(f"Found {map_result.total} links")

for link in map_result.links[:10]:  # First 10 links
    print(f"{link.get('title', 'No title')}: {link.get('url')}")
```

### Searching the Web

```python
search_result = adapter.search(
    "python web scraping",
    options=ScrapeOptions(formats=[ScrapeFormat.MARKDOWN])
)

print(f"Found {search_result.total} results")
for result in search_result.results:
    print(f"{result.url}: {result.metadata.get('title', 'No title')}")
```

### Extracting Structured Data

```python
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "author": {"type": "string"}
    }
}

extract_result = adapter.extract(
    urls=["https://example.com/article"],
    schema=schema,
    prompt="Extract article information"
)

print(extract_result.data)
```

## Error Handling

The Firecrawl integration raises module-specific exceptions:

```python
from codomyrmex.scrape.exceptions import (
    ScrapeConnectionError,
    ScrapeTimeoutError,
    FirecrawlError,
)

try:
    result = adapter.scrape("https://example.com")
except ScrapeConnectionError as e:
    print(f"Connection failed: {e}")
except ScrapeTimeoutError as e:
    print(f"Timeout: {e}")
except FirecrawlError as e:
    print(f"Firecrawl error: {e}")
```

## Dependencies

- `firecrawl-py`: Firecrawl Python SDK (install with `pip install firecrawl-py`)

## Navigation

- **Parent**: [scrape](../README.md) - Main scrape module
- **Technical Docs**: [AGENTS.md](AGENTS.md) - Agent documentation
- **Specification**: [SPEC.md](SPEC.md) - Functional specification

