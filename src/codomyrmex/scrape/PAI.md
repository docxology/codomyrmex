# Personal AI Infrastructure -- Scrape Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Scrape module is the web content acquisition engine for Codomyrmex, providing HTML extraction, structured data parsing, and text similarity analysis from web pages. It sits in the **Core Layer** of the architecture and serves as the primary mechanism for PAI agents to gather information from web sources -- extracting titles, headings, links, images, metadata, and full text from raw HTML without requiring a live network connection for offline content processing. For JavaScript-rendered pages, the module integrates with Firecrawl as a provider backend.

## PAI Capabilities

### Web Content Extraction

The `scrape_extract_content` MCP tool accepts raw HTML and returns a structured breakdown of the page content. It uses the `ContentExtractor` class, which performs regex-based extraction without requiring external HTML parser dependencies.

```python
from codomyrmex.scrape.extractors.content_extractor import ContentExtractor

extractor = ContentExtractor(base_url="https://docs.example.com")
result = extractor.extract("""
<html>
  <head>
    <title>API Reference</title>
    <meta name="description" content="REST API documentation">
  </head>
  <body>
    <h1>Getting Started</h1>
    <p>Welcome to the API reference guide.</p>
    <h2>Authentication</h2>
    <p>All requests require a Bearer token.</p>
    <a href="/endpoints">View Endpoints</a>
    <img src="/logo.png" alt="Logo">
  </body>
</html>
""")

print(result.title)          # "API Reference"
print(result.headings)       # [(1, "Getting Started"), (2, "Authentication")]
print(result.paragraphs)     # ["Welcome to the API ...", "All requests ..."]
print(result.links)          # [("https://docs.example.com/endpoints", "View Endpoints")]
print(result.images)         # [("https://docs.example.com/logo.png", "Logo")]
print(result.meta)           # {"description": "REST API documentation"}
print(result.word_count)     # 14
print(result.content_hash)   # SHA-256 hex digest of concatenated paragraph text
```

The `ExtractedContent` dataclass returned contains:

| Field | Type | Description |
|-------|------|-------------|
| `url` | `str` | Source URL (for resolving relative links) |
| `title` | `str` | Extracted `<title>` content |
| `headings` | `list[tuple[int, str]]` | Heading level and text pairs |
| `paragraphs` | `list[str]` | Text blocks from `<p>` elements |
| `links` | `list[tuple[str, str]]` | Resolved (URL, anchor text) tuples |
| `images` | `list[tuple[str, str]]` | Resolved (src, alt text) tuples |
| `meta` | `dict[str, str]` | Meta tag name/content pairs |
| `word_count` | `int` | Total word count across paragraphs |
| `content_hash` | `str` | SHA-256 hash of full text for deduplication |

### Text Similarity

The `scrape_text_similarity` MCP tool computes Jaccard word-level similarity between two text strings, returning a score in the range [0.0, 1.0]. This enables PAI agents to compare extracted content across pages, detect near-duplicate documents, and measure content drift over time.

```python
from codomyrmex.scrape.extractors.content_extractor import text_similarity

# Compare two extracted paragraphs
score = text_similarity(
    "The API requires authentication via Bearer tokens for all endpoints",
    "All endpoints require Bearer token authentication through the API"
)
print(score)  # ~0.7 (high overlap in word sets)

# Detect near-duplicates
score = text_similarity(page_a_text, page_b_text)
if score > 0.85:
    print("Near-duplicate content detected")
```

### Firecrawl Integration

For JavaScript-rendered single-page applications and dynamic content that cannot be extracted from raw HTML alone, the module delegates to Firecrawl as a provider backend. The `Scraper` class acts as a facade over the `FirecrawlAdapter`, supporting scraping, crawling, site mapping, web search, and LLM-powered structured extraction.

```python
from codomyrmex.scrape import Scraper, ScrapeOptions, ScrapeFormat

# Scraper auto-initializes with FirecrawlAdapter when FIRECRAWL_API_KEY is set
scraper = Scraper()

# Scrape a JS-rendered page into markdown
options = ScrapeOptions(
    formats=[ScrapeFormat.MARKDOWN],
    wait_for=".content-loaded",   # Wait for CSS selector before extracting
    respect_robots_txt=True,
)
result = scraper.scrape("https://spa-app.example.com/docs", options)
print(result.content)             # Clean markdown output

# Crawl an entire documentation site
crawl_result = scraper.crawl(
    "https://docs.example.com",
    ScrapeOptions(max_depth=3, limit=50)
)
for page in crawl_result.results:
    print(f"{page.url}: {len(page.content)} chars")
```

### Full Scraper Operations

Beyond the two MCP tools, the `Scraper` class provides five operations via the Firecrawl provider:

| Operation | Method | Description |
|-----------|--------|-------------|
| Scrape | `scraper.scrape(url, options)` | Extract content from a single URL |
| Crawl | `scraper.crawl(url, options)` | Crawl a site with depth and page limits |
| Map | `scraper.map(url, search)` | Discover all links on a website |
| Search | `scraper.search(query, options)` | Search the web and scrape results |
| Extract | `scraper.extract(urls, schema, prompt)` | LLM-powered structured extraction |

## MCP Tools

Two tools are auto-discovered via the `@mcp_tool` decorator in `mcp_tools.py` and surfaced through the PAI MCP bridge. Both are read-only and do not require trust escalation.

| Tool | Description | Trust Level | Parameters |
|------|-------------|-------------|------------|
| `scrape_extract_content` | Extract structured content (title, headings, links, images, metadata) from raw HTML | READ-ONLY | `html: str`, `base_url: str = ""` |
| `scrape_text_similarity` | Compute Jaccard word-level similarity between two text strings | READ-ONLY | `text_a: str`, `text_b: str` |

Both tools return a `dict` with `"status": "ok"` on success or `"status": "error"` with an `"error"` message on failure. Neither tool makes network requests -- they operate on content already in memory.

## PAI Algorithm Phase Mapping

| Phase | Scrape Contribution | Typical Usage |
|-------|---------------------|---------------|
| **OBSERVE** | Extract and structure content from web documentation, API references, and source pages | Agent fetches HTML via `requests` or browser, passes to `scrape_extract_content` for structured parsing |
| **THINK** | Compare extracted content against known sources to assess relevance and novelty | Use `scrape_text_similarity` to measure overlap between scraped content and existing knowledge |
| **PLAN** | Identify which web sources to scrape and in what order based on site mapping results | Use `scraper.map()` to discover documentation structure before planning extraction sequence |
| **BUILD** | Provide raw material for documentation generation and knowledge base construction | Feed extracted paragraphs and headings into `documents/` or `graph_rag/` pipelines |
| **EXECUTE** | Run batch scraping operations across multiple pages with rate limiting | Use `scraper.crawl()` with `ScrapeOptions` for controlled multi-page extraction |
| **VERIFY** | Validate that scraped content matches expected structure and is not stale | Compare `content_hash` values across runs to detect content changes |
| **LEARN** | Index scraped web sources into agentic memory for future retrieval | Store `ExtractedContent` with URL provenance in `agentic_memory/` |

## PAI Configuration

### Environment Variables

```bash
# Firecrawl provider (required for JS-rendered page support)
export FIRECRAWL_API_KEY="fc-..."        # Primary API key
export FC_API_KEY="fc-..."               # Alternate env var name (fallback)

# Endpoint configuration
export SCRAPE_BASE_URL="https://api.firecrawl.dev"  # Default Firecrawl endpoint

# Timeout and retry settings
export SCRAPE_TIMEOUT="30.0"             # Request timeout in seconds (default: 30)
export SCRAPE_MAX_RETRIES="3"            # Maximum retry attempts (default: 3)
export SCRAPE_RETRY_DELAY="1.0"          # Delay between retries in seconds (default: 1.0)

# Rate limiting
export SCRAPE_RATE_LIMIT="2.0"           # Requests per second (optional, unset = unlimited)

# Polite crawling
export SCRAPE_USER_AGENT="Codomyrmex-Scraper/0.1.0"  # User agent string
export SCRAPE_RESPECT_ROBOTS_TXT="true"               # Honor robots.txt (default: true)
```

### Programmatic Configuration

```python
from codomyrmex.scrape import ScrapeConfig, set_config

# Load from environment
config = ScrapeConfig.from_env()
config.validate()  # Raises ScrapeValidationError if api_key is missing

# Or configure explicitly
config = ScrapeConfig(
    api_key="fc-...",
    default_timeout=60.0,
    rate_limit=1.0,
    respect_robots_txt=True,
)
set_config(config)
```

## PAI Best Practices

### 1. Use scrape_extract_content for offline HTML parsing, Scraper for live pages

The two MCP tools (`scrape_extract_content`, `scrape_text_similarity`) operate on content already in memory -- they never make network requests. Use them when you have raw HTML from any source (file, cache, prior fetch). Use the `Scraper` class when you need to fetch live content, especially from JavaScript-rendered pages.

```python
# Offline: parse HTML you already have
from codomyrmex.scrape.extractors.content_extractor import ContentExtractor
result = ContentExtractor().extract(cached_html)

# Online: fetch and parse a live page
from codomyrmex.scrape import Scraper
result = Scraper().scrape("https://live-site.example.com")
```

### 2. Respect rate limits and robots.txt

The module defaults to honoring `robots.txt` and supports configurable rate limiting. When scraping external sites, always set `SCRAPE_RATE_LIMIT` to avoid overwhelming target servers. For batch crawling, use `ScrapeOptions.limit` and `ScrapeOptions.max_depth` to bound the operation.

```python
from codomyrmex.scrape import ScrapeConfig, ScrapeOptions

config = ScrapeConfig(rate_limit=1.0, respect_robots_txt=True)
options = ScrapeOptions(max_depth=2, limit=20, respect_robots_txt=True)
```

### 3. Integrate with agentic_memory for persistent web knowledge

After extracting content, store it in `agentic_memory/` with URL provenance so agents can retrieve web-sourced knowledge in future sessions without re-scraping.

```python
from codomyrmex.scrape.extractors.content_extractor import ContentExtractor

extractor = ContentExtractor(base_url="https://docs.example.com")
content = extractor.extract(html)

# Store in agentic memory with provenance
memory_entry = {
    "source_url": content.url,
    "title": content.title,
    "text": " ".join(content.paragraphs),
    "content_hash": content.content_hash,
    "extracted_at": "2026-02-24T00:00:00Z",
}
```

### 4. Use content_hash for change detection

The `content_hash` field (SHA-256 of concatenated paragraph text) provides a stable fingerprint for detecting content changes between scraping runs without storing full page content.

## Architecture Role

**Core Layer** -- The scrape module depends on `logging_monitoring` (structured logging) and `exceptions` (base error classes). It is consumed by:

- `documents/` -- Web document import and conversion to internal formats
- `graph_rag/` -- Knowledge graph population from web-sourced structured content
- `agentic_memory/` -- Web source indexing with URL provenance and content hashing

### Internal Structure

| Component | File | Responsibility |
|-----------|------|----------------|
| Content Extractor | `extractors/content_extractor.py` | Regex-based HTML parsing, text similarity |
| Scraper Facade | `extractors/scraper.py` | Unified interface delegating to provider adapters |
| Core Abstractions | `core.py` | `BaseScraper` ABC, result dataclasses, format enums |
| Configuration | `config.py` | `ScrapeConfig` dataclass, env var loading, validation |
| Exceptions | `exceptions.py` | `ScrapeError` hierarchy with context metadata |
| MCP Tools | `mcp_tools.py` | `@mcp_tool`-decorated functions for PAI bridge |
| Firecrawl Adapter | `firecrawl/` | Provider-specific implementation for JS-rendered pages |

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
