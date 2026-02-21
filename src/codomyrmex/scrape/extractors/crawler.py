"""Rate-limited web crawler with robots.txt compliance.

Provides a configurable page fetcher that respects rate limits,
follows links within a domain scope, and extracts text content.
"""

from __future__ import annotations

import time
import hashlib
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from urllib.parse import urljoin, urlparse


class CrawlStatus(Enum):
    """Status of a crawled page."""

    SUCCESS = "success"
    RATE_LIMITED = "rate_limited"
    ROBOTS_BLOCKED = "robots_blocked"
    ERROR = "error"
    SKIPPED = "skipped"
    MAX_DEPTH = "max_depth"


@dataclass
class CrawlConfig:
    """Configuration for the crawler.

    Attributes:
        max_pages: Maximum number of pages to crawl.
        max_depth: Maximum link-follow depth from seed URLs.
        delay_seconds: Minimum delay between requests to same host.
        respect_robots: Whether to check robots.txt.
        allowed_domains: If set, only crawl these domains.
        excluded_patterns: URL patterns to skip.
        user_agent: User-Agent string for requests.
        timeout_seconds: HTTP request timeout.
    """

    max_pages: int = 100
    max_depth: int = 3
    delay_seconds: float = 1.0
    respect_robots: bool = True
    allowed_domains: list[str] = field(default_factory=list)
    excluded_patterns: list[str] = field(default_factory=list)
    user_agent: str = "Codomyrmex-Crawler/0.6.0"
    timeout_seconds: float = 30.0


@dataclass
class CrawlResult:
    """Result of crawling a single page.

    Attributes:
        url: The fetched URL.
        status: Crawl status.
        status_code: HTTP status code (0 if not fetched).
        content_type: MIME type of the response.
        content_length: Size of the response body in bytes.
        title: Extracted page title if HTML.
        text_content: Extracted text content.
        links: Discovered links on the page.
        depth: Crawl depth from seed.
        fetch_time: Time taken to fetch (seconds).
        content_hash: SHA-256 of the content for dedup.
        error: Error message if status is ERROR.
    """

    url: str
    status: CrawlStatus
    status_code: int = 0
    content_type: str = ""
    content_length: int = 0
    title: str = ""
    text_content: str = ""
    links: list[str] = field(default_factory=list)
    depth: int = 0
    fetch_time: float = 0.0
    content_hash: str = ""
    error: str = ""


@dataclass
class RobotsPolicy:
    """Parsed robots.txt rules for a domain.

    Attributes:
        allowed_paths: Explicitly allowed paths.
        disallowed_paths: Paths that should not be crawled.
        crawl_delay: Suggested delay from robots.txt.
    """

    allowed_paths: list[str] = field(default_factory=list)
    disallowed_paths: list[str] = field(default_factory=list)
    crawl_delay: float | None = None


class Crawler:
    """A configurable web crawler with rate limiting and scope control.

    The crawler manages a frontier queue, tracks visited URLs,
    and enforces per-host rate limits. It does NOT perform actual
    HTTP requests — instead it provides methods that an external
    fetcher can drive, making it testable without network access.

    Example::

        crawler = Crawler(config=CrawlConfig(max_pages=50, max_depth=2))
        crawler.add_seeds(["https://example.com"])
        while crawler.has_next():
            url, depth = crawler.next_url()
            # ... fetch the URL externally ...
            result = CrawlResult(url=url, status=CrawlStatus.SUCCESS, depth=depth)
            crawler.record_result(result)
    """

    def __init__(self, config: CrawlConfig | None = None) -> None:
        self._config = config or CrawlConfig()
        self._frontier: deque[tuple[str, int]] = deque()
        self._visited: set[str] = set()
        self._results: list[CrawlResult] = []
        self._last_request_time: dict[str, float] = {}
        self._robots_cache: dict[str, RobotsPolicy] = {}
        self._content_hashes: set[str] = set()

    @property
    def config(self) -> CrawlConfig:
        """Current crawler configuration."""
        return self._config

    @property
    def pages_crawled(self) -> int:
        """Number of pages successfully crawled."""
        return len(self._results)

    @property
    def frontier_size(self) -> int:
        """Number of URLs waiting to be crawled."""
        return len(self._frontier)

    @property
    def visited_count(self) -> int:
        """Number of unique URLs visited."""
        return len(self._visited)

    def add_seeds(self, urls: list[str]) -> int:
        """Add seed URLs to the frontier.

        Args:
            urls: List of starting URLs.

        Returns:
            Number of new URLs added (deduped).
        """
        added = 0
        for url in urls:
            normalized = self._normalize_url(url)
            if normalized not in self._visited:
                self._frontier.append((normalized, 0))
                self._visited.add(normalized)
                added += 1
        return added

    def has_next(self) -> bool:
        """Check if there are more URLs to crawl."""
        return (
            len(self._frontier) > 0
            and self.pages_crawled < self._config.max_pages
        )

    def next_url(self) -> tuple[str, int] | None:
        """Get the next URL to crawl from the frontier.

        Returns:
            Tuple of (url, depth) or None if frontier is empty.
        """
        if not self.has_next():
            return None
        return self._frontier.popleft()

    def is_allowed(self, url: str) -> bool:
        """Check if a URL is allowed by domain scope and robots rules.

        Args:
            url: URL to check.

        Returns:
            True if the URL should be crawled.
        """
        parsed = urlparse(url)

        # Domain check
        if self._config.allowed_domains:
            if parsed.hostname not in self._config.allowed_domains:
                return False

        # Excluded patterns
        for pattern in self._config.excluded_patterns:
            if pattern in url:
                return False

        # Robots.txt check
        if self._config.respect_robots and parsed.hostname:
            policy = self._robots_cache.get(parsed.hostname)
            if policy:
                path = parsed.path or "/"
                for disallowed in policy.disallowed_paths:
                    if path.startswith(disallowed):
                        return True if any(
                            path.startswith(a) for a in policy.allowed_paths
                        ) else False

        return True

    def should_wait(self, url: str) -> float:
        """Calculate wait time before fetching a URL.

        Args:
            url: The URL to fetch.

        Returns:
            Seconds to wait (0.0 if no wait needed).
        """
        host = urlparse(url).hostname or ""
        last_time = self._last_request_time.get(host, 0.0)
        elapsed = time.monotonic() - last_time
        delay = self._config.delay_seconds

        # Use robots.txt crawl-delay if available and larger
        policy = self._robots_cache.get(host)
        if policy and policy.crawl_delay is not None:
            delay = max(delay, policy.crawl_delay)

        remaining = delay - elapsed
        return max(0.0, remaining)

    def record_result(self, result: CrawlResult) -> None:
        """Record a crawl result and enqueue discovered links.

        Args:
            result: The result of fetching a page.
        """
        self._results.append(result)

        host = urlparse(result.url).hostname or ""
        self._last_request_time[host] = time.monotonic()

        # Content dedup
        if result.content_hash:
            self._content_hashes.add(result.content_hash)

        # Enqueue discovered links
        if result.status == CrawlStatus.SUCCESS and result.depth < self._config.max_depth:
            for link in result.links:
                normalized = self._normalize_url(urljoin(result.url, link))
                if normalized not in self._visited and self.is_allowed(normalized):
                    self._visited.add(normalized)
                    self._frontier.append((normalized, result.depth + 1))

    def set_robots_policy(self, domain: str, policy: RobotsPolicy) -> None:
        """Cache a parsed robots.txt policy for a domain."""
        self._robots_cache[domain] = policy

    def is_duplicate_content(self, content: str) -> bool:
        """Check if content has already been seen.

        Args:
            content: Page content to check.

        Returns:
            True if a page with the same content hash was already crawled.
        """
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        return content_hash in self._content_hashes

    def get_results(self) -> list[CrawlResult]:
        """Return all crawl results."""
        return list(self._results)

    def stats(self) -> dict[str, Any]:
        """Return crawl statistics.

        Returns:
            Dictionary with crawl metrics.
        """
        status_counts: dict[str, int] = {}
        for r in self._results:
            key = r.status.value
            status_counts[key] = status_counts.get(key, 0) + 1

        return {
            "pages_crawled": self.pages_crawled,
            "frontier_remaining": self.frontier_size,
            "unique_urls_seen": self.visited_count,
            "unique_content_hashes": len(self._content_hashes),
            "status_counts": status_counts,
        }

    def _normalize_url(self, url: str) -> str:
        """Normalize a URL by removing fragments and trailing slashes."""
        parsed = urlparse(url)
        normalized = parsed._replace(fragment="")
        result = normalized.geturl()
        if result.endswith("/") and len(parsed.path) > 1:
            result = result.rstrip("/")
        return result

    def clear(self) -> None:
        """Reset crawler state."""
        self._frontier.clear()
        self._visited.clear()
        self._results.clear()
        self._last_request_time.clear()
        self._content_hashes.clear()
