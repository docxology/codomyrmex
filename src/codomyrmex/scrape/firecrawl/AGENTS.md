# Codomyrmex Agents — src/codomyrmex/scrape/firecrawl

## Signposting
- **Parent**: [scrape](../AGENTS.md)
- **Self**: [Firecrawl Agents](AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Firecrawl integration submodule providing typed interfaces to the Firecrawl web scraping service. This submodule wraps the Firecrawl Python SDK and adapts it to work with the core scraping abstractions.

## Module Overview

### Key Capabilities
- **SDK Wrapping**: Low-level wrapper around firecrawl-py SDK
- **Type Conversion**: Converts between Firecrawl SDK types and core abstractions
- **Error Translation**: Translates Firecrawl errors to module exceptions
- **API Management**: Handles API key management and configuration

### Key Classes

#### FirecrawlClient
Low-level client wrapper for the Firecrawl SDK.

**Location**: `client.py`

**Key Methods**:
- `scrape_url(url: str, formats: Optional[List[str]] = None, actions: Optional[List[Dict[str, Any]]] = None, wait_for: Optional[str] = None) -> Dict[str, Any]`
- `crawl_url(url: str, limit: Optional[int] = None, scrape_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
- `map_url(url: str, search: Optional[str] = None) -> Dict[str, Any]`
- `search_web(query: str, limit: Optional[int] = None, scrape_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
- `extract_data(urls: List[str], schema: Optional[Dict[str, Any]] = None, prompt: Optional[str] = None) -> Dict[str, Any]`

**Dependencies**:
- `firecrawl-py` package
- `ScrapeConfig` from parent module
- Module exceptions for error handling

#### FirecrawlAdapter
High-level adapter implementing `BaseScraper` interface.

**Location**: `adapter.py`

**Key Methods**:
- `scrape(url: str, options: Optional[ScrapeOptions] = None) -> ScrapeResult`
- `crawl(url: str, options: Optional[ScrapeOptions] = None) -> CrawlResult`
- `map(url: str, search: Optional[str] = None) -> MapResult`
- `search(query: str, options: Optional[ScrapeOptions] = None) -> SearchResult`
- `extract(urls: List[str], schema: Optional[Dict[str, Any]] = None, prompt: Optional[str] = None) -> ExtractResult`

**Internal Methods**:
- `_convert_scrape_result(firecrawl_data: Dict[str, Any], url: str) -> ScrapeResult`
- `_convert_crawl_result(firecrawl_data: Dict[str, Any], url: str) -> CrawlResult`
- `_convert_map_result(firecrawl_data: Dict[str, Any]) -> MapResult`
- `_convert_search_result(firecrawl_data: Dict[str, Any], query: str) -> SearchResult`
- `_convert_extract_result(firecrawl_data: Dict[str, Any], urls: List[str]) -> ExtractResult`

**Dependencies**:
- `FirecrawlClient` for API communication
- Core abstractions from parent module
- Module exceptions for error handling

## Operating Contracts

1. **API Key Required**: Firecrawl operations require a valid API key in `ScrapeConfig`
2. **Error Translation**: All Firecrawl SDK errors are translated to module exceptions
3. **Type Safety**: All methods use type hints and return typed results
4. **Logging**: All operations are logged using the logging_monitoring module

## Integration Points

- **Parent Module**: Uses core abstractions (`ScrapeResult`, `ScrapeOptions`, etc.)
- **Configuration**: Uses `ScrapeConfig` from parent module
- **Exceptions**: Uses module exceptions from parent module
- **Logging**: Uses `logging_monitoring` for all logging

## Active Components

- `__init__.py` - Package initialization and exports
- `client.py` - FirecrawlClient implementation
- `adapter.py` - FirecrawlAdapter implementation
- `README.md` - User-facing documentation
- `AGENTS.md` - This file: technical documentation
- `SPEC.md` - Functional specification

## Navigation Links

- **Parent Module**: [scrape/AGENTS.md](../AGENTS.md) - Main scrape module documentation
- **Parent README**: [scrape/README.md](../README.md) - Main scrape module overview
- **Firecrawl SDK**: https://github.com/firecrawl/firecrawl - Official Firecrawl repository

