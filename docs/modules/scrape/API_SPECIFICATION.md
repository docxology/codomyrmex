# Scrape Module API Specification

**Version**: v1.0.0 | **Last Updated**: February 2026

## Overview

This document provides detailed API reference for the scrape module, including all classes, methods, and data structures.

## Core Classes

### Scraper

Main interface for scraping operations.

```python
class Scraper(BaseScraper):
    def __init__(self, config: Optional[ScrapeConfig] = None, adapter: Optional[BaseScraper] = None)
    def scrape(url: str, options: Optional[ScrapeOptions] = None) -> ScrapeResult
    def crawl(url: str, options: Optional[ScrapeOptions] = None) -> CrawlResult
    def map(url: str, search: Optional[str] = None) -> MapResult
    def search(query: str, options: Optional[ScrapeOptions] = None) -> SearchResult
    def extract(urls: List[str], schema: Optional[Dict[str, Any]] = None, prompt: Optional[str] = None) -> ExtractResult
```

### ScrapeConfig

Configuration management for scraping operations.

```python
class ScrapeConfig:
    api_key: Optional[str]
    base_url: str
    default_timeout: float
    default_formats: List[str]
    max_retries: int
    retry_delay: float
    rate_limit: Optional[float]
    user_agent: str
    respect_robots_txt: bool

    @classmethod
    def from_env(cls) -> ScrapeConfig
    def validate(self) -> None
    def to_dict(self) -> Dict[str, Any]
```

## Data Structures

### ScrapeResult

```python
@dataclass
class ScrapeResult:
    url: str
    content: str = ""
    formats: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status_code: Optional[int] = None
    success: bool = True
    error: Optional[str] = None

    def get_format(format_type: ScrapeFormat | str) -> Any
    def has_format(format_type: ScrapeFormat | str) -> bool
```

### ScrapeOptions

```python
@dataclass
class ScrapeOptions:
    formats: List[ScrapeFormat | str] = field(default_factory=lambda: [ScrapeFormat.MARKDOWN])
    timeout: Optional[float] = None
    headers: Dict[str, str] = field(default_factory=dict)
    wait_for: Optional[str] = None
    actions: List[Dict[str, Any]] = field(default_factory=list)
    exclude_tags: List[str] = field(default_factory=list)
    include_tags: List[str] = field(default_factory=list)
    max_depth: Optional[int] = None
    limit: Optional[int] = None
    follow_links: bool = True
    respect_robots_txt: bool = True

    def to_dict() -> Dict[str, Any]
```

### ScrapeFormat

```python
class ScrapeFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    LINKS = "links"
    SCREENSHOT = "screenshot"
    METADATA = "metadata"
```

### CrawlResult

```python
@dataclass
class CrawlResult:
    job_id: str
    status: str
    total: int = 0
    completed: int = 0
    results: List[ScrapeResult] = field(default_factory=list)
    credits_used: int = 0
    expires_at: Optional[str] = None
```

### MapResult

```python
@dataclass
class MapResult:
    links: List[Dict[str, Any]] = field(default_factory=list)
    total: int = 0
```

### SearchResult

```python
@dataclass
class SearchResult:
    query: str
    results: List[ScrapeResult] = field(default_factory=list)
    total: int = 0
```

### ExtractResult

```python
@dataclass
class ExtractResult:
    job_id: Optional[str] = None
    status: str = "completed"
    data: Dict[str, Any] = field(default_factory=dict)
    urls: List[str] = field(default_factory=list)
```

## Exceptions

### ScrapeError

Base exception for all scrape-related errors.

```python
class ScrapeError(CodomyrmexError):
    pass
```

### ScrapeConnectionError

Raised when there's a network or connection issue.

```python
class ScrapeConnectionError(ScrapeError):
    def __init__(message: str, url: Optional[str] = None, status_code: Optional[int] = None, **kwargs)
```

### ScrapeTimeoutError

Raised when a scraping operation times out.

```python
class ScrapeTimeoutError(ScrapeError):
    def __init__(message: str, url: Optional[str] = None, timeout: Optional[float] = None, **kwargs)
```

### ScrapeValidationError

Raised when input validation fails.

```python
class ScrapeValidationError(ScrapeError):
    def __init__(message: str, field: Optional[str] = None, value: Optional[str] = None, **kwargs)
```

### FirecrawlError

Raised when Firecrawl-specific errors occur.

```python
class FirecrawlError(ScrapeError):
    def __init__(message: str, firecrawl_error: Optional[Exception] = None, **kwargs)
```

## Configuration Functions

### get_config

Get the global configuration instance.

```python
def get_config() -> ScrapeConfig
```

### set_config

Set the global configuration instance.

```python
def set_config(config: ScrapeConfig) -> None
```

### reset_config

Reset the global configuration to None.

```python
def reset_config() -> None
```

## Firecrawl Integration

### FirecrawlClient

Low-level wrapper around Firecrawl SDK.

```python
class FirecrawlClient:
    def __init__(self, config: ScrapeConfig)
    def scrape_url(url: str, formats: Optional[List[str]] = None, ...) -> Dict[str, Any]
    def crawl_url(url: str, limit: Optional[int] = None, ...) -> Dict[str, Any]
    def map_url(url: str, search: Optional[str] = None) -> Dict[str, Any]
    def search_web(query: str, limit: Optional[int] = None, ...) -> Dict[str, Any]
    def extract_data(urls: List[str], schema: Optional[Dict] = None, ...) -> Dict[str, Any]
```

### FirecrawlAdapter

High-level adapter implementing BaseScraper.

```python
class FirecrawlAdapter(BaseScraper):
    def __init__(self, config: Optional[ScrapeConfig] = None)
    def scrape(url: str, options: Optional[ScrapeOptions] = None) -> ScrapeResult
    def crawl(url: str, options: Optional[ScrapeOptions] = None) -> CrawlResult
    def map(url: str, search: Optional[str] = None) -> MapResult
    def search(query: str, options: Optional[ScrapeOptions] = None) -> SearchResult
    def extract(urls: List[str], schema: Optional[Dict] = None, ...) -> ExtractResult
```


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../README.md)
