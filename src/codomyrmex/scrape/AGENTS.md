# Agent Guidelines - Scrape

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Web scraping with browser automation and DOM extraction. Provides `Scraper` for simple HTTP-based
scraping, `BrowserScraper` for JavaScript-heavy sites, and `DOMExtractor` for structured DOM
parsing. Two MCP tools (`scrape_extract_content`, `scrape_text_similarity`) expose content
extraction and similarity comparison.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `Scraper`, `BrowserScraper`, `DOMExtractor`, `RateLimiter` |
| `extractors/scraper.py` | `Scraper` — HTTP-based content fetching with URL validation |
| `browser_scraper.py` | `BrowserScraper` — async browser automation for JavaScript sites |
| `dom_extractor.py` | `DOMExtractor` — CSS-selector-based DOM parsing |
| `rate_limiter.py` | `RateLimiter` — per-domain rate limiting |
| `mcp_tools.py` | MCP tools: `scrape_extract_content`, `scrape_text_similarity` |

## Key Classes

- **Scraper** — High-level scraping
- **BrowserScraper** — Browser-based scraping
- **DOMExtractor** — Extract from DOM
- **RateLimiter** — Respect rate limits

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `scrape_extract_content` | Extract structured content (title, headings, links) from raw HTML | Safe |
| `scrape_text_similarity` | Compute text similarity between two strings using Jaccard index | Safe |

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

## Operating Contracts

- `Scraper.get()` validates URL scheme — only `http://` and `https://` are accepted; others raise `ValueError`
- `BrowserScraper` requires an async runtime — always `await` its methods
- `RateLimiter` is enforced per-domain — create one instance and reuse across requests
- `scrape_text_similarity` uses Jaccard index — returns 0.0–1.0 (1.0 = identical)
- **DO NOT** pass raw file paths or file:// URLs to `Scraper.get()` — only web URLs

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

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `scrape_extract_content`, `scrape_text_similarity` | TRUSTED |
| **Architect** | Read + Design | `scrape_text_similarity` — content similarity analysis, data extraction design | OBSERVED |
| **QATester** | Validation | `scrape_extract_content`, `scrape_text_similarity` — extraction correctness verification | OBSERVED |
| **Researcher** | Read-only | `scrape_extract_content`, `scrape_text_similarity` — full read access for research | SAFE |

### Engineer Agent
**Use Cases**: Extracting web content during OBSERVE phase, computing text similarity for research, gathering external data.

### Architect Agent
**Use Cases**: Designing content extraction pipelines, reviewing similarity metrics, planning data aggregation.

### QATester Agent
**Use Cases**: Validating extraction quality during VERIFY, confirming URL validation works correctly.

### Researcher Agent
**Use Cases**: Extracting structured content from web pages and computing text similarity for research analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
