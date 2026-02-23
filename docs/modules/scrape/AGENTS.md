# Agent Guidelines - Scrape

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Web scraping with browser automation and DOM extraction.

## Key Classes

- **Scraper** — High-level scraping
- **BrowserScraper** — Browser-based scraping
- **DOMExtractor** — Extract from DOM
- **RateLimiter** — Respect rate limits

## Agent Instructions

1. **Respect robots.txt** — Check before scraping
2. **Rate limit** — Don't overwhelm servers
3. **Handle failures** — Retry with backoff
4. **Cache responses** — Avoid repeat requests
5. **User-agent** — Set appropriate user agent

## Common Patterns

```python
from codomyrmex.scrape import Scraper, BrowserScraper, DOMExtractor

# Simple scraping
scraper = Scraper()
html = scraper.get("https://example.com")
links = scraper.extract_links(html)

# Browser for JavaScript sites
browser = BrowserScraper()
await browser.navigate("https://spa.example.com")
await browser.wait_for_selector(".data")
content = await browser.get_content()

# DOM extraction
extractor = DOMExtractor(html)
titles = extractor.select_all("h1")
data = extractor.extract({
    "title": "h1",
    "price": ".price",
    "description": ".desc"
})
```

## Testing Patterns

```python
# Verify extraction
extractor = DOMExtractor("<h1>Test</h1>")
titles = extractor.select_all("h1")
assert len(titles) == 1
assert titles[0].text == "Test"

# Verify rate limiting
scraper = Scraper(rate_limit=1.0)  # 1 req/sec
start = time.time()
scraper.get("url1")
scraper.get("url2")
assert time.time() - start >= 1.0
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
