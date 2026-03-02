# Extractors -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Content extraction engine and crawl state manager for the `scrape` module. `ContentExtractor` uses regex patterns to pull structured data from HTML without external parsing libraries. `Crawler` manages URL queues, depth limits, and robots.txt compliance.

## Architecture

```
ContentExtractor
  +-- extract(html) -> ExtractedContent
  +-- _extract_title / _extract_headings / _extract_links / etc.

Crawler(CrawlConfig)
  +-- add_url(url, depth)
  +-- next_url() -> (url, depth)
  +-- should_crawl(url) -> bool
  +-- mark_visited(url, status)
  +-- get_results() -> list[CrawlResult]

RobotsPolicy
  +-- parse(robots_txt)
  +-- is_allowed(url, user_agent) -> bool
```

## Key Classes

### ContentExtractor Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `extract(html)` | `ExtractedContent` | Full extraction pipeline |
| `_extract_title(html)` | `str` | First `<title>` tag content |
| `_extract_headings(html)` | `list[dict]` | All h1-h6 with level and text |
| `_extract_links(html)` | `list[dict]` | All `<a>` href + text pairs |
| `_extract_images(html)` | `list[dict]` | All `<img>` src + alt pairs |
| `_extract_text(html)` | `str` | Strip all HTML tags, collapse whitespace |
| `_extract_meta(html)` | `dict` | Meta tag name-content pairs |

### Crawler Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `add_url(url, depth)` | `None` | Enqueue URL if not visited and within limits |
| `next_url()` | `tuple` | Pop next (url, depth) from queue |
| `should_crawl(url)` | `bool` | Check domain, depth, visited, robots |
| `mark_visited(url, status)` | `None` | Record CrawlResult |
| `get_results()` | `list[CrawlResult]` | All visited URLs with outcomes |

### CrawlConfig Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_pages` | `int` | `100` | Maximum pages to visit |
| `max_depth` | `int` | `3` | Maximum link-follow depth |
| `delay` | `float` | `1.0` | Seconds between requests (advisory) |
| `allowed_domains` | `list[str]` | `[]` | Domain allowlist (empty = all) |
| `user_agent` | `str` | `"Codomyrmex"` | User-agent for robots.txt matching |

## Constraints

- Extraction is regex-based; malformed HTML may yield incomplete results.
- Crawler is a state manager only -- callers must perform HTTP fetches.
- `text_similarity` uses word-level Jaccard; not suitable for semantic similarity.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- Parent: [scrape](../README.md)
