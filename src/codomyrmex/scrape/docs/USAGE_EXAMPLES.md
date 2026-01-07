# Scrape Module Usage Examples

This document provides comprehensive usage examples for the scrape module.

## Basic Scraping

### Simple Scrape

```python
from codomyrmex.scrape import Scraper

scraper = Scraper()
result = scraper.scrape("https://example.com")

print(result.content)  # Markdown content
print(result.metadata.get("title"))  # Page title
```

### Multiple Formats

```python
from codomyrmex.scrape import Scraper, ScrapeOptions, ScrapeFormat

scraper = Scraper()
options = ScrapeOptions(
    formats=[ScrapeFormat.MARKDOWN, ScrapeFormat.HTML, ScrapeFormat.METADATA]
)
result = scraper.scrape("https://example.com", options)

print(result.formats.get("markdown"))  # Markdown
print(result.formats.get("html"))  # HTML
print(result.formats.get("metadata"))  # Metadata
```

### With Custom Headers

```python
from codomyrmex.scrape import Scraper, ScrapeOptions

scraper = Scraper()
options = ScrapeOptions(
    headers={
        "User-Agent": "MyBot/1.0",
        "Accept": "text/html",
    }
)
result = scraper.scrape("https://example.com", options)
```

## Website Crawling

### Basic Crawl

```python
from codomyrmex.scrape import Scraper, ScrapeOptions, ScrapeFormat

scraper = Scraper()
options = ScrapeOptions(
    formats=[ScrapeFormat.MARKDOWN],
    limit=10,  # Maximum pages
)

crawl_result = scraper.crawl("https://example.com", options)

print(f"Job ID: {crawl_result.job_id}")
print(f"Status: {crawl_result.status}")
print(f"Total pages: {crawl_result.total}")

for page in crawl_result.results:
    print(f"  - {page.url}: {len(page.content)} chars")
```

### Crawl with Depth Control

```python
from codomyrmex.scrape import Scraper, ScrapeOptions

scraper = Scraper()
options = ScrapeOptions(
    max_depth=2,  # Only crawl 2 levels deep
    limit=50,
)

crawl_result = scraper.crawl("https://example.com", options)
```

## Site Mapping

### Map All Links

```python
from codomyrmex.scrape import Scraper

scraper = Scraper()
map_result = scraper.map("https://example.com")

print(f"Found {map_result.total} links")
for link in map_result.links[:10]:
    print(f"  {link.get('title', 'No title')}: {link.get('url')}")
```

### Search for Specific Links

```python
from codomyrmex.scrape import Scraper

scraper = Scraper()
# Find links related to "docs"
map_result = scraper.map("https://example.com", search="docs")

print(f"Found {map_result.total} matching links")
for link in map_result.links:
    print(f"  {link.get('title')}: {link.get('url')}")
```

## Web Search

### Basic Search

```python
from codomyrmex.scrape import Scraper

scraper = Scraper()
search_result = scraper.search("python web scraping")

print(f"Found {search_result.total} results")
for result in search_result.results:
    print(f"  {result.url}: {result.metadata.get('title')}")
```

### Search with Content Scraping

```python
from codomyrmex.scrape import Scraper, ScrapeOptions, ScrapeFormat

scraper = Scraper()
options = ScrapeOptions(
    formats=[ScrapeFormat.MARKDOWN],
    limit=5,  # Number of results to scrape
)

search_result = scraper.search("python web scraping", options)

for result in search_result.results:
    print(f"
{result.url}")
    print(result.content[:200])  # First 200 chars
```

## Structured Data Extraction

### Extract with Schema

```python
from codomyrmex.scrape import Scraper

scraper = Scraper()

schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "author": {"type": "string"},
        "published_date": {"type": "string"},
        "content": {"type": "string"}
    },
    "required": ["title", "content"]
}

extract_result = scraper.extract(
    urls=["https://example.com/article"],
    schema=schema
)

print(extract_result.data)
```

### Extract with Prompt

```python
from codomyrmex.scrape import Scraper

scraper = Scraper()

extract_result = scraper.extract(
    urls=["https://example.com/article"],
    prompt="Extract the main points and key takeaways from this article"
)

print(extract_result.data)
```

### Extract from Multiple URLs

```python
from codomyrmex.scrape import Scraper

scraper = Scraper()

extract_result = scraper.extract(
    urls=[
        "https://example.com/article1",
        "https://example.com/article2",
        "https://example.com/article3",
    ],
    prompt="Extract article summaries"
)

for url, data in zip(extract_result.urls, extract_result.data):
    print(f"{url}: {data}")
```

## Configuration

### Environment Variables

```bash
export FIRECRAWL_API_KEY="fc-your-api-key"
export SCRAPE_TIMEOUT="60.0"
export SCRAPE_MAX_RETRIES="5"
```

```python
from codomyrmex.scrape import Scraper

# Automatically uses environment variables
scraper = Scraper()
```

### Programmatic Configuration

```python
from codomyrmex.scrape import Scraper, ScrapeConfig, set_config

config = ScrapeConfig(
    api_key="fc-your-key",
    default_timeout=60.0,
    max_retries=5,
    respect_robots_txt=True,
)

set_config(config)  # Set as global
scraper = Scraper()  # Uses global config
```

### Per-Instance Configuration

```python
from codomyrmex.scrape import Scraper, ScrapeConfig

config = ScrapeConfig(api_key="fc-your-key")
scraper = Scraper(config=config)
```

## Error Handling

### Comprehensive Error Handling

```python
from codomyrmex.scrape import Scraper
from codomyrmex.scrape.exceptions import (
    ScrapeValidationError,
    ScrapeConnectionError,
    ScrapeTimeoutError,
    FirecrawlError,
    ScrapeError,
)

scraper = Scraper()

try:
    result = scraper.scrape("https://example.com")
except ScrapeValidationError as e:
    print(f"Invalid input: {e}")
except ScrapeConnectionError as e:
    print(f"Connection failed: {e.url}")
except ScrapeTimeoutError as e:
    print(f"Timeout after {e.context.get('timeout')}s")
except FirecrawlError as e:
    print(f"Firecrawl error: {e}")
except ScrapeError as e:
    print(f"Scraping error: {e}")
```

## Batch Processing

### Process Multiple URLs

```python
from codomyrmex.scrape import Scraper, ScrapeOptions, ScrapeFormat

scraper = Scraper()
options = ScrapeOptions(formats=[ScrapeFormat.MARKDOWN])

urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3",
]

results = []
for url in urls:
    try:
        result = scraper.scrape(url, options)
        results.append(result)
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")

print(f"Successfully scraped {len(results)} URLs")
```

## Advanced Usage

### Dynamic Content with Actions

```python
from codomyrmex.scrape import Scraper, ScrapeOptions

scraper = Scraper()
options = ScrapeOptions(
    actions=[
        {"type": "wait", "milliseconds": 2000},
        {"type": "click", "selector": "button.load-more"},
        {"type": "wait", "milliseconds": 3000},
    ]
)

result = scraper.scrape("https://example.com/dynamic", options)
```

### Custom Timeout

```python
from codomyrmex.scrape import Scraper, ScrapeOptions

scraper = Scraper()
options = ScrapeOptions(timeout=120.0)  # 2 minute timeout

result = scraper.scrape("https://slow-site.com", options)
```


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
