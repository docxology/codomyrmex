# Codomyrmex Agents — src/codomyrmex/scrape

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [firecrawl](firecrawl/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Web data extraction engine providing a unified interface for scraping web content, crawling websites, mapping site structures, and extracting structured data. Abstracts different scraping providers (e.g., Firecrawl) behind a consistent Pythonic interface with support for multiple formats (markdown, HTML, JSON, screenshots, metadata), batch operations, JavaScript-rendered content, and LLM-powered structured data extraction.

## Active Components
- `CHANGELOG.md` – Project file
- `NO_MOCKS_VERIFICATION.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file
- `TESTING.md` – Project file
- `__init__.py` – Module exports and public API
- `config.py` – Configuration management for scraping operations
- `core.py` – Core scraping abstractions and data structures
- `docs/` – Directory containing docs components
- `exceptions.py` – Scraping-specific exceptions
- `firecrawl/` – Directory containing Firecrawl adapter implementation
- `requirements.txt` – Project file
- `scraper.py` – Main scraper class implementing the core scraping interface
- `tests/` – Directory containing tests components

## Key Classes and Functions

### Scraper (`scraper.py`)
- `Scraper(config: Optional[ScrapeConfig] = None, adapter: Optional[BaseScraper] = None)` – Main scraper class providing unified interface
- `scrape(url: str, options: Optional[ScrapeOptions] = None) -> ScrapeResult` – Scrape a single URL
- `crawl(url: str, options: Optional[ScrapeOptions] = None) -> CrawlResult` – Crawl a website starting from a URL
- `map(url: str, search: Optional[str] = None) -> MapResult` – Map the structure of a website
- `search(query: str, options: Optional[ScrapeOptions] = None) -> SearchResult` – Search the web and optionally scrape results
- `extract(urls: List[str], schema: Optional[Dict[str, Any]] = None, prompt: Optional[str] = None) -> ExtractResult` – Extract structured data from URLs using LLM

### BaseScraper (`core.py`)
- `BaseScraper` (ABC) – Abstract base class for scraper implementations
- `scrape(url: str, options: Optional[ScrapeOptions] = None) -> ScrapeResult` – Abstract method for scraping
- `crawl(url: str, options: Optional[ScrapeOptions] = None) -> CrawlResult` – Abstract method for crawling
- `map(url: str, search: Optional[str] = None) -> MapResult` – Abstract method for mapping
- `search(query: str, options: Optional[ScrapeOptions] = None) -> SearchResult` – Abstract method for searching
- `extract(urls: List[str], schema: Optional[Dict[str, Any]] = None, prompt: Optional[str] = None) -> ExtractResult` – Abstract method for extraction

### ScrapeResult (`core.py`)
- `ScrapeResult` (dataclass) – Standard result structure:
  - `url: str` – The URL that was scraped
  - `content: str` – The main content (markdown or HTML)
  - `formats: Dict[str, Any]` – Dictionary mapping format types to their content
  - `metadata: Dict[str, Any]` – Additional metadata about the scraped page
  - `status_code: Optional[int]` – HTTP status code if available
  - `success: bool` – Whether the scrape operation was successful
  - `error: Optional[str]` – Error message if the operation failed
- `get_format(format_type: ScrapeFormat | str) -> Any` – Get content in a specific format
- `has_format(format_type: ScrapeFormat | str) -> bool` – Check if a specific format is available

### ScrapeOptions (`core.py`)
- `ScrapeOptions` (dataclass) – Configuration options:
  - `formats: List[ScrapeFormat | str]` – List of formats to request
  - `timeout: Optional[float]` – Request timeout in seconds
  - `headers: Dict[str, str]` – Custom HTTP headers
  - `wait_for: Optional[str]` – CSS selector or time to wait for
  - `actions: List[Dict[str, Any]]` – Actions to perform before scraping
  - `exclude_tags: List[str]` – HTML tags to exclude
  - `include_tags: List[str]` – HTML tags to include
  - `max_depth: Optional[int]` – Maximum crawl depth
  - `limit: Optional[int]` – Maximum number of pages
  - `follow_links: bool` – Whether to follow links
  - `respect_robots_txt: bool` – Whether to respect robots.txt
- `to_dict() -> Dict[str, Any]` – Convert options to dictionary format

### ScrapeConfig (`config.py`)
- `ScrapeConfig` (dataclass) – Configuration for scraping operations:
  - `api_key: Optional[str]` – API key for the scraping service
  - `base_url: str` – Base URL for the scraping API
  - `default_timeout: float` – Default timeout for requests
  - `default_formats: list[str]` – Default formats to request
  - `max_retries: int` – Maximum number of retry attempts
  - `retry_delay: float` – Delay between retries
  - `rate_limit: Optional[float]` – Rate limit (requests per second)
  - `user_agent: str` – User agent string
  - `respect_robots_txt: bool` – Whether to respect robots.txt
- `from_env() -> ScrapeConfig` (classmethod) – Create configuration from environment variables
- `validate() -> None` – Validate the configuration
- `to_dict() -> Dict[str, Any]` – Convert configuration to dictionary

### ScrapeFormat (`core.py`)
- `ScrapeFormat` (Enum) – Supported output formats: MARKDOWN, HTML, JSON, LINKS, SCREENSHOT, METADATA

### Module Functions (`__init__.py`)
- `get_config() -> ScrapeConfig` – Get the current scraping configuration
- `set_config(config: ScrapeConfig) -> None` – Set the scraping configuration
- `reset_config() -> None` – Reset configuration to defaults

### Exceptions (`exceptions.py`)
- `ScrapeError` – Base exception for scraping operations
- `ScrapeConnectionError` – Raised when connection fails
- `ScrapeTimeoutError` – Raised when operation times out
- `ScrapeValidationError` – Raised when validation fails
- `FirecrawlError` – Raised when Firecrawl-specific errors occur

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation