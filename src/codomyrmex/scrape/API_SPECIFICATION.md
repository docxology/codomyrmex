# Scrape Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: January 2026

## 1. Overview
The `scrape` module provides capabilities for extracting data from web sources. It features a modular architecture supporting different scraping backends (e.g., Firecrawl).

## 2. Core Components

### 2.1 Classes
- **`Scraper`**: Main client for performing scrape operations.
- **`ScrapeOptions`**: Configuration object for requests (formats, depth, etc.).
- **`ScrapeResult`**: Container for scrape outputs.

### 2.2 Data Structures
- **`ScrapeFormat` (Enum)**: output formats (MARKDOWN, HTML, JSON).
- **`CrawlResult`**: Result of a crawling operation.
- **`SearchResult`**: Result of a search operation.

### 2.3 Exceptions
- **`ScrapeError`**: Base exception.
- **`ScrapeConnectionError`**: Network failures.
- **`ScrapeTimeoutError`**: Operation timeouts.
- **`FirecrawlError`**: Provider-specific errors.

## 3. Usage Example

```python
from codomyrmex.scrape import Scraper, ScrapeOptions, ScrapeFormat

scraper = Scraper()
options = ScrapeOptions(formats=[ScrapeFormat.MARKDOWN])

try:
    result = scraper.scrape("https://example.com", options)
    print(result.content)
except ScrapeError as e:
    print(f"Scrape failed: {e}")
```
