# Codomyrmex Agents — src/codomyrmex/scrape

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Scrape Agents](AGENTS.md)
- **Children**:
    - [Firecrawl Integration Agents](firecrawl/AGENTS.md)
    - [Documentation Agents](docs/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core Layer module providing web scraping capabilities for the Codomyrmex platform. This module offers a unified interface for scraping web content, crawling websites, mapping site structures, and extracting structured data using AI/LLM.

The scrape module serves as the web data extraction layer, enabling reliable conversion of web content into LLM-ready formats with support for multiple scraping providers.

## Module Overview

### Key Capabilities
- **Web Scraping**: Scrape individual web pages with multiple format support
- **Website Crawling**: Crawl entire websites and extract content
- **Site Mapping**: Discover and map website structure
- **Web Search**: Search the web and scrape results
- **LLM Extraction**: Extract structured data using AI/LLM
- **Provider Abstraction**: Support for multiple scraping providers via adapter pattern

### Key Classes

#### Scraper
Main interface for scraping operations.

**Location**: `scraper.py`

**Key Methods**:
- `scrape(url: str, options: Optional[ScrapeOptions] = None) -> ScrapeResult`
- `crawl(url: str, options: Optional[ScrapeOptions] = None) -> CrawlResult`
- `map(url: str, search: Optional[str] = None) -> MapResult`
- `search(query: str, options: Optional[ScrapeOptions] = None) -> SearchResult`
- `extract(urls: List[str], schema: Optional[Dict[str, Any]] = None, prompt: Optional[str] = None) -> ExtractResult`

**Dependencies**:
- `BaseScraper` from core
- Provider adapters (e.g., `FirecrawlAdapter`)
- `ScrapeConfig` for configuration
- Module exceptions for error handling

#### ScrapeConfig
Configuration management for scraping operations.

**Location**: `config.py`

**Key Methods**:
- `from_env() -> ScrapeConfig`: Create config from environment variables
- `validate() -> None`: Validate configuration
- `to_dict() -> Dict[str, Any]`: Convert to dictionary

**Attributes**:
- `api_key: Optional[str]`: API key for scraping service
- `base_url: str`: Base URL for API
- `default_timeout: float`: Default timeout in seconds
- `max_retries: int`: Maximum retry attempts
- `respect_robots_txt: bool`: Whether to respect robots.txt

#### Core Data Structures

**Location**: `core.py`

- `ScrapeResult`: Standard result structure with content, formats, metadata
- `ScrapeOptions`: Configuration for scraping operations
- `ScrapeFormat`: Enum of supported formats (markdown, html, json, etc.)
- `CrawlResult`: Result structure for crawl operations
- `MapResult`: Result structure for map operations
- `SearchResult`: Result structure for search operations
- `ExtractResult`: Result structure for extract operations
- `BaseScraper`: Abstract base class for scraper implementations

### Key Functions

**Location**: `config.py`

- `get_config() -> ScrapeConfig`: Get global configuration instance
- `set_config(config: ScrapeConfig) -> None`: Set global configuration
- `reset_config() -> None`: Reset global configuration

## Operating Contracts

1. **Provider Adapter Required**: Scraper requires a provider adapter (e.g., FirecrawlAdapter)
2. **API Key Required**: Most operations require a valid API key in ScrapeConfig
3. **Error Handling**: All errors are raised as module-specific exceptions
4. **Logging**: All operations use logging_monitoring for structured logging
5. **Type Safety**: All methods use type hints and return typed results

## Integration Points

- **Logging**: Uses `codomyrmex.logging_monitoring` for all logging
- **Exceptions**: Uses `codomyrmex.exceptions.CodomyrmexError` as base
- **Configuration**: Environment variable support via `ScrapeConfig.from_env()`
- **Provider Adapters**: Uses adapter pattern for provider integration

## Active Components

### Core Files
- `__init__.py` - Package initialization and public API exports
- `core.py` - Core abstractions and data structures
- `scraper.py` - Main Scraper class
- `config.py` - Configuration management
- `exceptions.py` - Module-specific exceptions

### Submodules
- `firecrawl/` - Firecrawl integration submodule
  - `__init__.py` - Firecrawl exports
  - `client.py` - FirecrawlClient wrapper
  - `adapter.py` - FirecrawlAdapter implementation

### Documentation
- `README.md` - User-facing documentation
- `AGENTS.md` - This file: technical documentation
- `SPEC.md` - Functional specification
- `SECURITY.md` - Security considerations
- `CHANGELOG.md` - Version history
- `docs/` - Additional documentation

### Tests
- `tests/unit/` - Unit test suites
- `tests/integration/` - Integration test suites

## Navigation Links

- **Parent**: [codomyrmex/AGENTS.md](../AGENTS.md) - Package overview
- **Firecrawl Integration**: [firecrawl/AGENTS.md](firecrawl/AGENTS.md) - Firecrawl submodule
- **Functional Spec**: [SPEC.md](SPEC.md) - Detailed specification
- **User Guide**: [README.md](README.md) - User-facing documentation

