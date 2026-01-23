# Codomyrmex Agents — src/codomyrmex/scrape

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Scrape module provides web scraping capabilities with support for multiple scraping providers, primarily through Firecrawl integration. It offers URL scraping, website crawling, site mapping, web search, and LLM-powered structured data extraction with configurable output formats including Markdown, HTML, JSON, and screenshots.

## Active Components

### Core Infrastructure

- `scraper.py` - Main scraper facade
  - Key Classes: `Scraper`
  - Key Functions: `scrape()`, `crawl()`, `map()`, `search()`, `extract()`
- `core.py` - Core abstractions and data structures
  - Key Classes: `BaseScraper`, `ScrapeResult`, `ScrapeOptions`, `CrawlResult`, `MapResult`, `SearchResult`, `ExtractResult`, `ScrapeFormat`
- `config.py` - Configuration management
  - Key Classes: `ScrapeConfig`
  - Key Functions: `get_config()`, `set_config()`, `reset_config()`
- `exceptions.py` - Exception hierarchy
  - Key Classes: `ScrapeError`, `ScrapeConnectionError`, `ScrapeTimeoutError`, `ScrapeValidationError`, `FirecrawlError`

### Provider Integrations

- `firecrawl/` - Firecrawl API adapter
  - Key Classes: `FirecrawlAdapter`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `Scraper` | scraper | Main scraper facade delegating to adapters |
| `BaseScraper` | core | Abstract base class for scraper implementations |
| `ScrapeResult` | core | Standard result structure for scrape operations |
| `ScrapeOptions` | core | Configuration options for scraping |
| `ScrapeConfig` | config | Global configuration management |
| `ScrapeFormat` | core | Enum for output formats (MARKDOWN, HTML, JSON, etc.) |
| `CrawlResult` | core | Result structure for crawl operations |
| `MapResult` | core | Result structure for site mapping |
| `SearchResult` | core | Result structure for web search |
| `ExtractResult` | core | Result structure for LLM extraction |
| `ScrapeError` | exceptions | Base exception for scrape errors |
| `ScrapeConnectionError` | exceptions | Network/connection failures |
| `ScrapeTimeoutError` | exceptions | Operation timeout errors |
| `ScrapeValidationError` | exceptions | Input validation failures |
| `FirecrawlError` | exceptions | Firecrawl-specific errors |
| `scrape()` | scraper | Scrape a single URL |
| `crawl()` | scraper | Crawl website starting from URL |
| `map()` | scraper | Map website structure/links |
| `search()` | scraper | Search web and scrape results |
| `extract()` | scraper | Extract structured data with LLM |
| `get_config()` | config | Get global configuration |
| `set_config()` | config | Set global configuration |

## Operating Contracts

1. **Logging**: All operations use `logging_monitoring` for structured logging
2. **Error Handling**: Operations raise `ScrapeError` subclasses for consistent error handling
3. **Configuration**: Environment variables supported (FIRECRAWL_API_KEY, SCRAPE_TIMEOUT, etc.)
4. **Rate Limiting**: Configurable rate limiting for API compliance
5. **Robots.txt**: Respect robots.txt by default (configurable)
6. **Retry Logic**: Configurable retry attempts with exponential backoff

## Integration Points

- **logging_monitoring** - Structured logging for all operations
- **exceptions** - Base exception classes (`CodomyrmexError`)
- **llm** - LLM integration for structured data extraction
- **documents** - Document processing from scraped content

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| llm | [../llm/AGENTS.md](../llm/AGENTS.md) | LLM infrastructure for extraction |
| documents | [../documents/AGENTS.md](../documents/AGENTS.md) | Document processing |
| cache | [../cache/AGENTS.md](../cache/AGENTS.md) | Response caching |

### Child Directories

| Directory | Purpose |
| :--- | :--- |
| firecrawl/ | Firecrawl API integration |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification
- [TESTING.md](TESTING.md) - Testing documentation
- [SECURITY.md](SECURITY.md) - Security considerations
- [CHANGELOG.md](CHANGELOG.md) - Version history
