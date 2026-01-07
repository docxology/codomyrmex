# firecrawl

## Signposting
- **Parent**: [firecrawl](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Firecrawl scraping provider integration. Provides adapter and client for Firecrawl API, enabling web scraping, crawling, and content extraction through the Firecrawl service.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `adapter.py` – File
- `client.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [scrape](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.scrape.firecrawl import FirecrawlClient, FirecrawlAdapter

# Initialize Firecrawl client
client = FirecrawlClient(api_key="your-api-key")

# Use adapter for scraping
adapter = FirecrawlAdapter(client=client)

# Scrape a URL
result = adapter.scrape(url="https://example.com")
print(f"Scraped content: {result.content[:100]}...")

# Crawl a website
crawl_result = adapter.crawl(url="https://example.com", max_depth=2)
print(f"Crawled {len(crawl_result.pages)} pages")
```

