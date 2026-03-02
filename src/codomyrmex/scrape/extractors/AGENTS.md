# Extractors Agentic Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Content extraction and web crawling logic for the `scrape` module. Agents use these classes to extract structured content from HTML and to manage multi-page crawl state.

## Key Components

| Component | Type | Role |
|-----------|------|------|
| `ContentExtractor` | Class | Regex-based HTML content extraction (title, headings, links, images, text, metadata) |
| `ExtractedContent` | Dataclass | Container for extraction results with `to_dict()` serialization |
| `text_similarity` | Function | Jaccard similarity between two text strings |
| `Crawler` | Class | URL queue manager with robots.txt respect and depth limiting |
| `CrawlConfig` | Dataclass | Max pages, depth, delay, allowed domains, user agent |
| `CrawlResult` | Dataclass | Per-URL crawl outcome (status, depth, timestamp) |
| `RobotsPolicy` | Class | Parses robots.txt Allow/Disallow directives per user-agent |

## Operating Contracts

- `ContentExtractor.extract(html)` returns an `ExtractedContent` with all fields populated via regex; no external parser required.
- `Crawler` does NOT perform HTTP requests itself -- it manages the queue and delegates fetching to callers.
- `Crawler.should_crawl(url)` checks domain allowlist, visited set, depth, and robots policy.
- `RobotsPolicy.parse(robots_txt)` accepts raw robots.txt text and populates allow/disallow rule lists.
- `text_similarity(a, b)` returns a float 0.0-1.0 using word-level Jaccard index.

## Integration Points

- Parent module `scrape` exposes `scrape_extract_content` and `scrape_text_similarity` MCP tools.
- Uses `logging_monitoring.get_logger` for structured logging.

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- Parent: [scrape](../README.md)
