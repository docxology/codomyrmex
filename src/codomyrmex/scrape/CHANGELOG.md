# Changelog

All notable changes to the scrape module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-XX

### Added
- Initial release of scrape module
- Core scraping abstractions (`ScrapeResult`, `ScrapeOptions`, `ScrapeFormat`)
- Main `Scraper` class implementing unified scraping interface
- `ScrapeConfig` for configuration management with environment variable support
- Module-specific exception hierarchy
- Firecrawl integration submodule
  - `FirecrawlClient` wrapper for Firecrawl SDK
  - `FirecrawlAdapter` implementing `BaseScraper` interface
- Support for multiple output formats (markdown, HTML, JSON, screenshots, metadata)
- Website crawling capabilities
- Site mapping functionality
- Web search with optional content scraping
- LLM-based structured data extraction with schema support
- Comprehensive documentation (README, AGENTS, SPEC, SECURITY)
- Unit and integration test structure

### Features
- Single URL scraping with multiple formats
- Website crawling with depth and limit controls
- Site structure mapping with search filtering
- Web search with result scraping
- AI/LLM extraction with JSON schemas and prompts
- Dynamic content support (actions: click, scroll, wait)
- Batch URL processing
- Error handling with specific exception types
- Logging integration with logging_monitoring module
- Type hints throughout

### Documentation
- User-facing README with examples
- Technical AGENTS.md documentation
- Functional SPEC.md specification
- Security considerations in SECURITY.md
- Firecrawl submodule documentation

### Testing
- Test structure for unit and integration tests
- Test files for core abstractions, scraper, and Firecrawl integration

[0.1.0]: https://github.com/codomyrmex/codomyrmex/releases/tag/scrape-v0.1.0


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
