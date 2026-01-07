# scrape

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [firecrawl](firecrawl/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Web data extraction engine providing a unified interface for scraping web content, crawling websites, mapping site structures, and extracting structured data. Abstracts different scraping providers (e.g., Firecrawl) behind a consistent Pythonic interface with support for multiple formats (markdown, HTML, JSON, screenshots, metadata), batch operations, JavaScript-rendered content, and LLM-powered structured data extraction.

## Directory Contents
- `CHANGELOG.md` – File
- `NO_MOCKS_VERIFICATION.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `TESTING.md` – File
- `__init__.py` – File
- `config.py` – File
- `core.py` – File
- `docs/` – Subdirectory
- `exceptions.py` – File
- `firecrawl/` – Subdirectory
- `requirements.txt` – File
- `scraper.py` – File
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.scrape import (
    Scraper,
    ScrapeOptions,
    ScrapeFormat,
)

# Initialize scraper
scraper = Scraper()

# Scrape a single URL
options = ScrapeOptions(
    formats=[ScrapeFormat.MARKDOWN, ScrapeFormat.HTML],
    include_links=True
)
result = scraper.scrape("https://example.com", options)
print(f"Content: {result.content[:100]}...")

# Crawl a website
crawl_result = scraper.crawl("https://example.com", max_pages=10)
print(f"Crawled {len(crawl_result.pages)} pages")

# Extract structured data
extract_result = scraper.extract(
    url="https://example.com",
    schema={"title": "string", "description": "string"}
)
print(f"Extracted data: {extract_result.data}")
```

