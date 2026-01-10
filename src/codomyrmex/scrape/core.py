from typing import Any, Dict, List, Optional

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from codomyrmex.logging_monitoring import get_logger











































"""Core scraping abstractions and data structures.


logger = get_logger(__name__)
This module defines the core abstractions for the scrape module,
including result types, configuration options, and abstract base classes.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL: """

class ScrapeFormat(str, Enum):
    """Supported output formats for scraping operations."""

    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    LINKS = "links"
    SCREENSHOT = "screenshot"
    METADATA = "metadata"


@dataclass
class ScrapeResult:
    """Standard result structure for scraping operations.

    Attributes:
        url: The URL that was scraped
        content: The main content (markdown or HTML)
        formats: Dictionary mapping format types to their content
        metadata: Additional metadata about the scraped page
        status_code: HTTP status code if available
        success: Whether the scrape operation was successful
        error: Error message if the operation failed
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:     """

    url: str
    content: str = ""
    formats: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status_code: Optional[int] = None
    success: bool = True
    error: Optional[str] = None

    def get_format(self, format_type: ScrapeFormat | str) -> Any:
        """Get content in a specific format."""
        format_key = format_type.value if isinstance(format_type, ScrapeFormat) else format_type
        return self.formats.get(format_key)

    def has_format(self, format_type: ScrapeFormat | str) -> bool:
        """Check if a specific format is available."""
        format_key = format_type.value if isinstance(format_type, ScrapeFormat) else format_type
        return format_key in self.formats


@dataclass
class ScrapeOptions:
    """Configuration options for scraping operations.

    Attributes:
        formats: List of formats to request (markdown, html, json, etc.)
        timeout: Request timeout in seconds
        headers: Custom HTTP headers to send
        wait_for: CSS selector or time to wait for before scraping
        actions: List of actions to perform before scraping (click, scroll, etc.)
        exclude_tags: List of HTML tags to exclude from content
        include_tags: List of HTML tags to include in content
        max_depth: Maximum crawl depth (for crawl operations)
        limit: Maximum number of pages to scrape (for crawl operations)
        follow_links: Whether to follow links when crawling
        respect_robots_txt: Whether to respect robots.txt
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:     """

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

    def to_dict(self) -> Dict[str, Any]:
        """Convert options to dictionary format."""
        result: Dict[str, Any] = {
            "formats": [
                f.value if isinstance(f, ScrapeFormat) else f for f in self.formats
            ],
            "headers": self.headers,
            "actions": self.actions,
            "exclude_tags": self.exclude_tags,
            "include_tags": self.include_tags,
            "follow_links": self.follow_links,
            "respect_robots_txt": self.respect_robots_txt,
        }
        if self.timeout is not None:
            result["timeout"] = self.timeout
        if self.wait_for is not None:
            result["wait_for"] = self.wait_for
        if self.max_depth is not None:
            result["max_depth"] = self.max_depth
        if self.limit is not None:
            result["limit"] = self.limit
        return result


@dataclass
class CrawlResult:
    """Result structure for crawl operations.

    Attributes:
        job_id: Unique identifier for the crawl job
        status: Current status of the crawl (pending, running, completed, failed)
        total: Total number of pages found
        completed: Number of pages completed
        results: List of ScrapeResult objects for each page
        credits_used: Number of API credits used
        expires_at: When the crawl result expires
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:     """

    job_id: str
    status: str
    total: int = 0
    completed: int = 0
    results: List[ScrapeResult] = field(default_factory=list)
    credits_used: int = 0
    expires_at: Optional[str] = None


@dataclass
class MapResult:
    """Result structure for map operations.

    Attributes:
        links: List of discovered links with metadata
        total: Total number of links found (auto-calculated from links if not set)
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:     """

    links: List[Dict[str, Any]] = field(default_factory=list)
    total: int = 0

    def __post_init__(self):
        """Auto-calculate total from links if not explicitly set."""
        if self.total == 0 and self.links:
            self.total = len(self.links)


@dataclass
class SearchResult:
    """Result structure for search operations.

    Attributes:
        query: The search query
        results: List of search results with content
        total: Total number of results
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:     """

    query: str
    results: List[ScrapeResult] = field(default_factory=list)
    total: int = 0


@dataclass
class ExtractResult:
    """Result structure for extract operations.

    Attributes:
        job_id: Unique identifier for the extract job
        status: Current status of the extraction
        data: Extracted structured data
        urls: URLs that were processed
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:     """

    job_id: Optional[str] = None
    status: str = "completed"
    data: Dict[str, Any] = field(default_factory=dict)
    urls: List[str] = field(default_factory=list)


class BaseScraper(ABC):
    """Abstract base class for scraper implementations.

    All scraper implementations should inherit from this class
    and implement the required methods.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:     """

    @abstractmethod
    def scrape(self, url: str, options: Optional[ScrapeOptions] = None) -> ScrapeResult:
        """Scrape a single URL.

        Args:
            url: The URL to scrape
            options: Optional scraping configuration

        Returns:
            ScrapeResult containing the scraped content
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        pass

    @abstractmethod
    def crawl(
        self, url: str, options: Optional[ScrapeOptions] = None
    ) -> CrawlResult:
        """Crawl a website starting from a URL.

        Args:
            url: The starting URL to crawl
            options: Optional crawling configuration

        Returns:
            CrawlResult containing the crawl job information
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        pass

    @abstractmethod
    def map(self, url: str, search: Optional[str] = None) -> MapResult:
        """Map the structure of a website.

        Args:
            url: The URL to map
            search: Optional search term to filter links

        Returns:
            MapResult containing discovered links
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        pass

    @abstractmethod
    def search(
        self, query: str, options: Optional[ScrapeOptions] = None
    ) -> SearchResult:
        """Search the web and optionally scrape results.

        Args:
            query: The search query
            options: Optional scraping configuration for results

        Returns:
            SearchResult containing search results
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        pass

    @abstractmethod
    def extract(
        self,
        urls: List[str],
        schema: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None,
    ) -> ExtractResult:
        """Extract structured data from URLs using LLM.

        Args:
            urls: List of URLs to extract data from
            schema: Optional JSON schema for extraction
            prompt: Optional prompt for extraction

        Returns:
            ExtractResult containing extracted data
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        pass


